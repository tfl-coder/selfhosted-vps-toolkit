#!/usr/bin/env python3
"""Persist a residential SOCKS outbound + domain routing into 3x-ui.

Run ON the server. Uses the current generated
/usr/local/x-ui/bin/config.json as the template base (that file IS the
default template the panel regenerates from), adds the outbound + rule,
and stores it as the xrayTemplateConfig setting so the panel keeps
using it across restarts. Creds come from env and are printed nowhere.

Usage:
    RES_HOST=... RES_PORT=... RES_USER=... RES_PASS=... python3 setup_relay.py
Then: systemctl restart x-ui, and read back the generated config.json
to confirm the rule is in place.
"""
import json
import os
import sqlite3

# Domains whose services reject datacenter IPs: AI assistants and
# streaming. Adjust to your own needs.
DOMAINS = [
    "domain:chatgpt.com", "domain:openai.com", "domain:oaistatic.com",
    "domain:oaiusercontent.com", "domain:claude.ai", "domain:anthropic.com",
    "domain:gemini.google.com", "domain:aistudio.google.com",
    "domain:ai.google.dev", "domain:generativelanguage.googleapis.com",
    "domain:perplexity.ai",
    "domain:facebook.com", "domain:fbcdn.net", "domain:instagram.com",
    "domain:cdninstagram.com", "domain:whatsapp.com",
    "domain:disneyplus.com", "domain:disney-plus.net", "domain:dssott.com",
    "domain:bamgrid.com", "domain:netflix.com", "domain:nflxvideo.net",
    "domain:nflximg.net", "domain:nflxext.com",
    "domain:x.com", "domain:twitter.com", "domain:t.co", "domain:twimg.com",
]

tpl = json.load(open("/usr/local/x-ui/bin/config.json"))

outbounds = [o for o in tpl.get("outbounds", []) if o.get("tag") != "residential"]
outbounds.append({
    "tag": "residential",
    "protocol": "socks",
    "settings": {"servers": [{
        "address": os.environ["RES_HOST"],
        "port": int(os.environ["RES_PORT"]),
        "users": [{"user": os.environ["RES_USER"], "pass": os.environ["RES_PASS"]}],
    }]},
})
tpl["outbounds"] = outbounds

routing = tpl.setdefault("routing", {})
rules = [r for r in routing.get("rules", []) if r.get("outboundTag") != "residential"]
rules.insert(1, {"type": "field", "outboundTag": "residential", "domain": DOMAINS})
routing["rules"] = rules

tpl_str = json.dumps(tpl, indent=2)

db = sqlite3.connect("/etc/x-ui/x-ui.db")
existing = db.execute(
    "SELECT id FROM settings WHERE key='xrayTemplateConfig'").fetchone()
if existing:
    db.execute("UPDATE settings SET value=? WHERE key='xrayTemplateConfig'",
               (tpl_str,))
    print("TEMPLATE_UPDATED")
else:
    db.execute("INSERT INTO settings (key, value) "
               "VALUES ('xrayTemplateConfig', ?)", (tpl_str,))
    print("TEMPLATE_INSERTED")
db.commit()
row = db.execute(
    "SELECT length(value) FROM settings WHERE key='xrayTemplateConfig'"
).fetchone()
print("TEMPLATE_LEN:", row[0] if row else None)
db.close()
