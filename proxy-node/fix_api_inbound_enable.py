#!/usr/bin/env python3
"""Fix clients that 3x-ui's panel API creates DISABLED.

Symptom: an inbound added via /panel/api/inbounds/add listens fine, but
every client auth fails, and the generated
/usr/local/x-ui/bin/config.json contains "clients": [] for it.
Cause: the API path stores enable=0 in three places — the `clients`
table, the `client_traffics` table, and the `enable` flag inside the
inbound's settings JSON.

Run ON the server, pass the inbound id(s), then restart x-ui and
read back the generated config to confirm the client is present
BEFORE declaring the inbound ready.

Usage: python3 fix_api_inbound_enable.py <inbound_id> [more ids...]
"""
import json
import sqlite3
import sys

ids = [int(x) for x in sys.argv[1:]]
if not ids:
    sys.exit("give at least one inbound id")

db = sqlite3.connect("/etc/x-ui/x-ui.db")

for iid in ids:
    # 1) clients table
    db.execute("UPDATE clients SET enable=1 WHERE inbound_id=?", (iid,))
    # 2) client_traffics table (keyed by inbound_id as well)
    db.execute("UPDATE client_traffics SET enable=1 WHERE inbound_id=?",
                 (iid,))
    # 3) enable flags inside the inbound's settings JSON
    row = db.execute("SELECT settings FROM inbounds WHERE id=?",
                     (iid,)).fetchone()
    if row and row[0]:
        settings = json.loads(row[0])
        for client in settings.get("clients", []):
            client["enable"] = True
        db.execute("UPDATE inbounds SET settings=? WHERE id=?",
                   (json.dumps(settings), iid))
    print(f"inbound {iid}: enable=1 in clients / client_traffics / settings")

db.commit()
db.close()
print("done — now: systemctl restart x-ui, then check "
      "/usr/local/x-ui/bin/config.json lists the client(s)")
