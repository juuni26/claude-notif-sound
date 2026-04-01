#!/bin/bash
# notif-sound GUI server — starts a web dashboard on port 6998
# Usage: gui-server.sh [start|stop]

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/notif-sound-local}"
PID_FILE="$DATA_DIR/gui.pid"
PORT=6998
ACTION="${1:-start}"

case "$ACTION" in
  start)
    # Kill existing server if running
    if [ -f "$PID_FILE" ]; then
      OLD_PID=$(cat "$PID_FILE")
      kill "$OLD_PID" 2>/dev/null
      rm -f "$PID_FILE"
    fi

    # Start Python HTTP server with custom handler
    python3 "$PLUGIN_ROOT/scripts/gui-server.py" "$PLUGIN_ROOT" "$DATA_DIR" "$PORT" &
    SERVER_PID=$!
    echo "$SERVER_PID" > "$PID_FILE"

    # Wait briefly for server to start
    sleep 1

    # Open browser
    OS="$(uname -s)"
    case "$OS" in
      Darwin) open "http://localhost:$PORT" ;;
      Linux) xdg-open "http://localhost:$PORT" 2>/dev/null || echo "Open http://localhost:$PORT in your browser" ;;
      *) echo "Open http://localhost:$PORT in your browser" ;;
    esac

    echo "GUI server started on http://localhost:$PORT (PID: $SERVER_PID)"
    ;;
  stop)
    if [ -f "$PID_FILE" ]; then
      PID=$(cat "$PID_FILE")
      kill "$PID" 2>/dev/null
      rm -f "$PID_FILE"
      echo "GUI server stopped"
    else
      echo "No GUI server running"
    fi
    ;;
  *)
    echo "Usage: gui-server.sh [start|stop]"
    exit 1
    ;;
esac
