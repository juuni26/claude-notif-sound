---
description: "List all notification sounds organized by category and show current volume. Use when the user wants to see installed sounds or check settings."
---

# List Sounds

Show all notification sounds organized by category and current settings.

1. Read volume from config:

```bash
cat "${CLAUDE_PLUGIN_DATA}/config.json"
```

2. List sounds in each category:

```bash
echo "=== all (fallback) ===" && ls -1 "${CLAUDE_PLUGIN_ROOT}/sounds/all/" 2>/dev/null | grep -E '\.(mp3|wav)$' || echo "(empty)"
echo "=== stop ===" && ls -1 "${CLAUDE_PLUGIN_ROOT}/sounds/stop/" 2>/dev/null | grep -E '\.(mp3|wav)$' || echo "(empty)"
echo "=== question ===" && ls -1 "${CLAUDE_PLUGIN_ROOT}/sounds/question/" 2>/dev/null | grep -E '\.(mp3|wav)$' || echo "(empty)"
echo "=== notification ===" && ls -1 "${CLAUDE_PLUGIN_ROOT}/sounds/notification/" 2>/dev/null | grep -E '\.(mp3|wav)$' || echo "(empty)"
echo "=== permission ===" && ls -1 "${CLAUDE_PLUGIN_ROOT}/sounds/permission/" 2>/dev/null | grep -E '\.(mp3|wav)$' || echo "(empty)"
```

3. Present results in a clean format showing:
   - Current volume (1-10)
   - Sound count per category
   - File names per category
   - Reminder of available commands: `/notif-sound:add`, `/notif-sound:volume`, `/notif-sound:test`, `/notif-sound:remove`, `/notif-sound:gui`
