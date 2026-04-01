---
description: "Check plugin health: verify scripts, sounds, audio player, and hooks are working. Use when the user wants to know if the plugin is set up correctly."
---

# Plugin Status

Run a health check on the notif-sound plugin and report the results.

Run ALL of these checks:

1. Check scripts are executable:

```bash
ls -la "${CLAUDE_PLUGIN_ROOT}/scripts/play-sound.sh" "${CLAUDE_PLUGIN_ROOT}/scripts/gui-server.sh" 2>/dev/null
```

2. Check sound files exist:

```bash
ls -1 "${CLAUDE_PLUGIN_ROOT}/sounds/" 2>/dev/null | grep -E '\.(mp3|wav)$' || echo "NO_SOUNDS"
```

3. Check audio player is available:

```bash
if [ "$(uname -s)" = "Darwin" ]; then
  command -v afplay && echo "PLAYER_OK" || echo "PLAYER_MISSING"
elif command -v paplay 2>/dev/null; then
  echo "PLAYER_OK (paplay)"
elif command -v aplay 2>/dev/null; then
  echo "PLAYER_OK (aplay)"
else
  echo "PLAYER_MISSING"
fi
```

4. Check python3 is available:

```bash
python3 --version 2>/dev/null || echo "PYTHON_MISSING"
```

5. Read current config:

```bash
cat "${CLAUDE_PLUGIN_DATA}/config.json" 2>/dev/null || echo '{"volume": 4} (default, no config file yet)'
```

6. Check if GUI server is running:

```bash
curl -s http://localhost:6998/api/status 2>/dev/null && echo "GUI_RUNNING" || echo "GUI_STOPPED"
```

7. Present a clear status report to the user:

   **Plugin Status**
   - Scripts: whether play-sound.sh and gui-server.sh are executable (fix with `chmod +x` if not)
   - Sounds: count of .mp3/.wav files found (suggest `/notif-sound:add` if none)
   - Audio player: which player was detected (afplay/paplay/aplay) or missing
   - Python 3: installed or missing
   - Volume: current setting (1-10)
   - GUI: running or stopped
   - Overall: "All good" if everything passes, or list what needs fixing

   Use checkmarks for passing checks and X marks for failures. If everything passes, confirm the plugin is fully operational.
