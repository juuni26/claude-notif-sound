---
description: "Test play a random notification sound. Use when the user wants to hear what the notification sounds like."
---

# Test Sound

Play a random notification sound to test the setup.

1. Run the play script:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/play-sound.sh"
```

2. Report to the user that the sound was played. If no sound was heard, suggest:
   - On macOS/Linux: check volume with `/notif-sound:volume`
   - On Windows: adjust your system volume (volume control is not supported)
   - Check if sounds exist with `/notif-sound:list`
