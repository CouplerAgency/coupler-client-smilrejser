#!/usr/bin/env bash
# Dump the JS-rendered DOM of a page with headless Chrome on macOS.
#
#   scripts/dom.sh <url> <output.html> [virtual-time-budget-ms]
#
# Needed because smilrejser.dk is a Next.js App Router site: several sections
# (notably the departures table) are absent from the server HTML that curl sees.
# Comparing curl output against this tells us whether something is genuinely
# missing or merely client-rendered.

set -uo pipefail

URL="${1:?usage: dom.sh <url> <output.html> [budget-ms]}"
OUT="${2:?usage: dom.sh <url> <output.html> [budget-ms]}"
BUDGET="${3:-15000}"

CHROME="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || { echo "Chrome not found at: $CHROME (set CHROME_BIN)" >&2; exit 1; }

mkdir -p "$(dirname "$OUT")"
PROFILE="$(mktemp -d "${TMPDIR:-/tmp}/smildom.XXXXXX")"
trap 'pkill -9 -f "user-data-dir=$PROFILE" >/dev/null 2>&1; rm -rf "$PROFILE"' EXIT

"$CHROME" \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --no-first-run \
  --no-default-browser-check \
  --disable-extensions \
  --user-data-dir="$PROFILE" \
  --window-size=1440,1200 \
  --virtual-time-budget="$BUDGET" \
  --dump-dom \
  "$URL" > "$OUT" 2>/dev/null &
PID=$!

for _ in $(seq 1 30); do
  sleep 1
  if [ -s "$OUT" ]; then sleep 1; break; fi
done
kill -9 "$PID" >/dev/null 2>&1
wait "$PID" 2>/dev/null

if [ -s "$OUT" ]; then
  echo "$OUT ($(wc -c < "$OUT" | tr -d ' ') bytes)"
else
  echo "FAILED: no DOM written for $URL" >&2
  exit 1
fi
