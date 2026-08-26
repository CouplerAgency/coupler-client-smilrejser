#!/usr/bin/env bash
# Capture a full-width screenshot of a page with headless Chrome on macOS.
#
#   scripts/shot.sh <url> <output.png> [WIDTHxHEIGHT]
#
#   scripts/shot.sh https://example.com assets/shots/example.png 1440x1400
#   scripts/shot.sh "file://$PWD/index.html#5" .preview/slide5.png 1440x900
#
# Why this exists instead of a one-liner: headless Chrome on macOS hangs with
# --headless=new, refuses to exit after writing the file, and locks a shared
# --user-data-dir when called in a loop. This handles all three.

set -uo pipefail

URL="${1:?bruk: shot.sh <url> <output.png> [WIDTHxHEIGHT]}"
OUT="${2:?bruk: shot.sh <url> <output.png> [WIDTHxHEIGHT]}"
SIZE="${3:-1440x1200}"
WINDOW="${SIZE/x/,}"

CHROME="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || { echo "Fant ikke Chrome på: $CHROME (sett CHROME_BIN)" >&2; exit 1; }

mkdir -p "$(dirname "$OUT")"
PROFILE="$(mktemp -d "${TMPDIR:-/tmp}/couplerdeck.XXXXXX")"
trap 'pkill -9 -f "user-data-dir=$PROFILE" >/dev/null 2>&1; rm -rf "$PROFILE"' EXIT

# --headless (not =new) is deliberate: =new hangs indefinitely here.
"$CHROME" \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --hide-scrollbars \
  --no-first-run \
  --no-default-browser-check \
  --disable-extensions \
  --allow-file-access-from-files \
  --user-data-dir="$PROFILE" \
  --window-size="$WINDOW" \
  --virtual-time-budget=8000 \
  --screenshot="$OUT" \
  "$URL" >/dev/null 2>&1 &
CHROME_PID=$!

# Chrome writes the file but does not always exit, so poll and then kill it.
for _ in $(seq 1 25); do
  sleep 1
  if [ -s "$OUT" ]; then sleep 1; break; fi
done
kill -9 "$CHROME_PID" >/dev/null 2>&1
wait "$CHROME_PID" 2>/dev/null   # reap quietly, otherwise the shell prints "Killed: 9"

if [ -s "$OUT" ]; then
  echo "$OUT ($(du -h "$OUT" | awk '{print $1}'))"
else
  echo "FEILET: ingen fil skrevet for $URL" >&2
  exit 1
fi
