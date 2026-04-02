#!/bin/bash
# notif-sound: Play a random notification sound for Claude Code events
# Usage: play-sound.sh

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/notif-sound-local}"
SOUNDS_DIR="$PLUGIN_ROOT/sounds"
CONFIG_FILE="$DATA_DIR/config.json"

# Detect available Python command (python3, python, py)
PYTHON_CMD=""
for cmd in python3 python py; do
  if command -v "$cmd" &>/dev/null; then
    PYTHON_CMD="$cmd"
    break
  fi
done

# If no Python found, exit gracefully
if [ -z "$PYTHON_CMD" ]; then
  exit 0
fi

# Ensure data directory exists
mkdir -p "$DATA_DIR"

# Skip if a notif-sound is already playing (check our own PID file)
PID_FILE="$DATA_DIR/.player-pid"
if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE" 2>/dev/null)
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    exit 0
  fi
  rm -f "$PID_FILE"
fi

# Read volume (1-10, default 4) and validate it's an integer
VOLUME=4
if [ -f "$CONFIG_FILE" ]; then
  V=$($PYTHON_CMD -c "import json, sys; print(json.load(open(sys.argv[1])).get('volume', 4))" "$CONFIG_FILE" 2>/dev/null)
  if [ -n "$V" ] && [[ "$V" =~ ^[0-9]+$ ]] && [ "$V" -ge 1 ] && [ "$V" -le 10 ]; then
    VOLUME="$V"
  fi
fi

# Detect OS once
OS="$(uname -s)"

# Collect sound files from sounds/ directory
# On Windows (MINGW/MSYS), only .wav is supported (PowerShell Media.SoundPlayer)
CANDIDATES=()
if [[ "$OS" == MINGW* ]] || [[ "$OS" == MSYS* ]]; then
  while IFS= read -r f; do
    [ -n "$f" ] && CANDIDATES+=("$f")
  done < <(find "$SOUNDS_DIR" -maxdepth 1 -name "*.wav" 2>/dev/null)
else
  while IFS= read -r f; do
    [ -n "$f" ] && CANDIDATES+=("$f")
  done < <(find "$SOUNDS_DIR" -maxdepth 1 \( -name "*.mp3" -o -name "*.wav" \) 2>/dev/null)
fi

# No sounds found
if [ ${#CANDIDATES[@]} -eq 0 ]; then
  exit 0
fi

# Pick a random sound
SOUND="${CANDIDATES[$((RANDOM % ${#CANDIDATES[@]}))]}"

# Detect OS and play
PLAYED=false
case "$OS" in
  Darwin)
    # macOS: volume 1-10 -> 0.1-1.0
    AFPLAY_VOL=$($PYTHON_CMD -c "import sys; print(round(int(sys.argv[1]) / 10, 1))" "$VOLUME" 2>/dev/null || echo "0.4")
    afplay -v "$AFPLAY_VOL" "$SOUND" &
    echo $! > "$PID_FILE"
    PLAYED=true
    ;;
  Linux)
    # Linux: volume 1-10 -> 6553-65536
    if command -v paplay &>/dev/null; then
      PA_VOL=$($PYTHON_CMD -c "import sys; print(int(int(sys.argv[1]) * 6553.6))" "$VOLUME" 2>/dev/null || echo "26214")
      paplay --volume="$PA_VOL" "$SOUND" &
      echo $! > "$PID_FILE"
      PLAYED=true
    elif command -v aplay &>/dev/null; then
      # aplay only supports .wav — re-filter candidates
      WAV_ONLY=()
      for f in "${CANDIDATES[@]}"; do
        [[ "$f" == *.wav ]] && WAV_ONLY+=("$f")
      done
      [ ${#WAV_ONLY[@]} -eq 0 ] && exit 0
      SOUND="${WAV_ONLY[$((RANDOM % ${#WAV_ONLY[@]}))]}"
      aplay "$SOUND" &
      echo $! > "$PID_FILE"
      PLAYED=true
    fi
    ;;
  MINGW*|MSYS*)
    # Native Windows (Git Bash): convert path for PowerShell, .wav only
    if command -v powershell.exe &>/dev/null; then
      WIN_SOUND="$(cygpath -w "$SOUND" 2>/dev/null || echo "$SOUND")"
      SAFE_SOUND="${WIN_SOUND//\'/\'\'}"
      powershell.exe -c "(New-Object Media.SoundPlayer '$SAFE_SOUND').PlaySync()" &
      echo $! > "$PID_FILE"
      PLAYED=true
    fi
    ;;
  *)
    # WSL or unknown: try paplay, then powershell
    if command -v paplay &>/dev/null; then
      PA_VOL=$($PYTHON_CMD -c "import sys; print(int(int(sys.argv[1]) * 6553.6))" "$VOLUME" 2>/dev/null || echo "26214")
      paplay --volume="$PA_VOL" "$SOUND" &
      echo $! > "$PID_FILE"
      PLAYED=true
    elif command -v powershell.exe &>/dev/null; then
      WIN_SOUND="$(cygpath -w "$SOUND" 2>/dev/null || echo "$SOUND")"
      SAFE_SOUND="${WIN_SOUND//\'/\'\'}"
      powershell.exe -c "(New-Object Media.SoundPlayer '$SAFE_SOUND').PlaySync()" &
      echo $! > "$PID_FILE"
      PLAYED=true
    fi
    ;;
esac

# Bounce Dock icon (macOS) / flash taskbar (Linux terminals) — only if sound was played
if [ "$PLAYED" = true ]; then
  printf '\a'
fi

exit 0
