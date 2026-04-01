---
description: "List all notification sounds and show current volume. Use when the user wants to see installed sounds or check settings."
---

# List Sounds

Show all notification sounds and current settings.

1. Read volume from config:

```bash
cat "${CLAUDE_PLUGIN_DATA}/config.json" 2>/dev/null || echo '{"volume": 4}'
```

2. List sounds:

```bash
ls -1 "${CLAUDE_PLUGIN_ROOT}/sounds/" 2>/dev/null | grep -E '\.(mp3|wav)$' || echo "(no sounds found)"
```

3. Check the platform:

```bash
uname -s
```

4. Present results in a clean format showing:
   - Current volume (1-10). If on Windows (uname starts with `MINGW` or `MSYS`), add "(not supported on Windows — use system volume)" next to the volume value
   - Sound count
   - File names
   - Reminder of available commands: `/notif-sound:add`, `/notif-sound:volume` (macOS/Linux only), `/notif-sound:test`, `/notif-sound:remove`, `/notif-sound:gui`
