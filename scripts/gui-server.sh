#!/bin/bash
# notif-sound GUI server — starts a web dashboard on port 6998
# Usage: gui-server.sh [start|stop]

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/notif-sound-local}"
PID_FILE="$DATA_DIR/gui.pid"
PORT=6998
ACTION="${1:-start}"

# Detect available Python command (python3, python, py)
PYTHON_CMD=""
for cmd in python3 python py; do
  if command -v "$cmd" &>/dev/null; then
    PYTHON_CMD="$cmd"
    break
  fi
done

# Kill a process and its entire tree (cross-platform)
kill_tree() {
  local pid="$1"
  if [ -z "$pid" ]; then return; fi
  # Windows (MSYS/Git Bash): use taskkill to kill process tree
  if command -v taskkill &>/dev/null; then
    taskkill //PID "$pid" //T //F &>/dev/null
  else
    # Unix: kill process group, fall back to single kill
    kill -- "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null
  fi
}

# Kill any process listening on our port
kill_port() {
  if command -v netstat &>/dev/null; then
    # Windows: parse netstat for PIDs on our port
    netstat -ano 2>/dev/null | grep "127.0.0.1:$PORT" | grep "LISTENING" | while read -r line; do
      local pid
      pid=$(echo "$line" | awk '{print $NF}')
      if [ -n "$pid" ] && [ "$pid" != "0" ]; then
        kill_tree "$pid"
      fi
    done
  elif command -v lsof &>/dev/null; then
    # macOS/Linux: use lsof
    lsof -ti :"$PORT" 2>/dev/null | while read -r pid; do
      kill_tree "$pid"
    done
  fi
}

stop_server() {
  # Kill PID from pid file
  if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    kill_tree "$OLD_PID"
    rm -f "$PID_FILE"
  fi
  # Kill anything still on the port
  kill_port
}

case "$ACTION" in
  start)
    # Stop any existing server (pid file + port cleanup)
    stop_server

    # Brief pause to let port release
    sleep 1

    # Start Python HTTP server with custom handler
    $PYTHON_CMD "$PLUGIN_ROOT/scripts/gui-server.py" "$PLUGIN_ROOT" "$DATA_DIR" "$PORT" &
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
    stop_server
    echo "GUI server stopped"
    ;;
  *)
    echo "Usage: gui-server.sh [start|stop]"
    exit 1
    ;;
esac
