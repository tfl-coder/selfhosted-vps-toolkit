#!/usr/bin/env bash
# Playback probe for a self-hosted Invidious instance.
# - Checks the API answers AND a canary video actually streams
#   through the instance proxy (API-only checks miss most breakage).
# - Two consecutive failures -> restart the compose stack.
# - Still failing after the restart -> fire one webhook alert.
#
# Config via environment (set them in the .service unit):
#   INSTANCE_URL   e.g. https://<your-host>:8446
#   COMPOSE_DIR    e.g. /opt/invidious
#   ALERT_WEBHOOK  any webhook that accepts a JSON {"text": ...} POST;
#                  leave empty to skip alerting
#   CANARY_VIDEO   any popular video id, default aqz-KE-bpKQ
set -u
STATE_FILE=/tmp/invidious-health.state
CANARY_VIDEO="${CANARY_VIDEO:-aqz-KE-bpKQ}"

probe() {
    # search API responds
    curl -fsS --max-time 15 "$INSTANCE_URL/api/v1/search?q=test&type=video" \
        >/dev/null 2>&1 || return 1
    # a real media range through the instance proxy streams bytes
    curl -fsS --max-time 20 -r 0-1023 \
        "$INSTANCE_URL/videoplayback?local=true&id=$CANARY_VIDEO" \
        >/dev/null 2>&1 || return 1
    return 0
}

alert() {
    [ -n "${ALERT_WEBHOOK:-}" ] || return 0
    curl -fsS --max-time 10 -X POST "$ALERT_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{\"text\": \"Invidious health: $1\"}" >/dev/null 2>&1 || true
}

fails=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
if probe; then
    echo 0 > "$STATE_FILE"
    exit 0
fi

fails=$((fails + 1))
echo "$fails" > "$STATE_FILE"
if [ "$fails" -ge 2 ]; then
    (cd "$COMPOSE_DIR" && docker compose restart) >/dev/null 2>&1
    sleep 30
    if probe; then
        echo 0 > "$STATE_FILE"
    else
        alert "playback still failing after restart, please check the instance"
    fi
fi
