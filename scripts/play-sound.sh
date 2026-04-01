#!/bin/bash
# notif-sound: Play a random notification sound for Claude Code events
# Usage: play-sound.sh [stop|question|notification|permission|all]

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/notif-sound-local}"
SOUNDS_DIR="$PLUGIN_ROOT/sounds"
CONFIG_FILE="$DATA_DIR/config.json"
CATEGORY="${1:-all}"

# Skip if a notif-sound is already playing (check our own PID file)
PID_FILE="$DATA_DIR/.player-pid"
if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE" 2>/dev/null)
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    # Our previous sound is still playing — skip
    exit 0
  fi
  rm -f "$PID_FILE"
fi

# Read volume (1-10, default 4)
VOLUME=4
if [ -f "$CONFIG_FILE" ]; then
  V=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('volume', 4))" 2>/dev/null)
  [ -n "$V" ] && VOLUME="$V"
fi

# Collect sound files: category-specific first, then fallback to all/
CANDIDATES=()
if [ -d "$SOUNDS_DIR/$CATEGORY" ]; then
  while IFS= read -r f; do
    [ -n "$f" ] && CANDIDATES+=("$f")
  done < <(find "$SOUNDS_DIR/$CATEGORY" -maxdepth 1 \( -name "*.mp3" -o -name "*.wav" \) 2>/dev/null)
fi

# Fallback to all/ if no category-specific sounds
if [ ${#CANDIDATES[@]} -eq 0 ] && [ -d "$SOUNDS_DIR/all" ]; then
  while IFS= read -r f; do
    [ -n "$f" ] && CANDIDATES+=("$f")
  done < <(find "$SOUNDS_DIR/all" -maxdepth 1 \( -name "*.mp3" -o -name "*.wav" \) 2>/dev/null)
fi

# No sounds found
if [ ${#CANDIDATES[@]} -eq 0 ]; then
  exit 0
fi

# Pick a random sound
SOUND="${CANDIDATES[$((RANDOM % ${#CANDIDATES[@]}))]}"

# Detect OS and play
OS="$(uname -s)"
case "$OS" in
  Darwin)
    # macOS: volume 1-10 → 0.1-1.0
    AFPLAY_VOL=$(python3 -c "print($VOLUME / 10)" 2>/dev/null || echo "0.4")
    afplay -v "$AFPLAY_VOL" "$SOUND" &
    echo $! > "$PID_FILE"
    ;;
  Linux)
    # Linux: volume 1-10 → 6553-65536
    if command -v paplay &>/dev/null; then
      PA_VOL=$(python3 -c "print(int($VOLUME * 6553.6))" 2>/dev/null || echo "26214")
      paplay --volume="$PA_VOL" "$SOUND" &
      echo $! > "$PID_FILE"
    elif command -v aplay &>/dev/null; then
      aplay "$SOUND" &
      echo $! > "$PID_FILE"
    fi
    ;;
  *)
    # WSL or unknown: try paplay, then powershell
    if command -v paplay &>/dev/null; then
      PA_VOL=$(python3 -c "print(int($VOLUME * 6553.6))" 2>/dev/null || echo "26214")
      paplay --volume="$PA_VOL" "$SOUND" &
      echo $! > "$PID_FILE"
    elif command -v powershell.exe &>/dev/null; then
      powershell.exe -c "(New-Object Media.SoundPlayer '$SOUND').PlaySync()" &
      echo $! > "$PID_FILE"
    fi
    ;;
esac

# Bounce Dock icon (macOS) / flash taskbar (Linux terminals)
printf '\a'

exit 0
