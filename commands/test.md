---
description: "Test play a random notification sound. Use when the user wants to hear what the notification sounds like."
argument-hint: "[stop|question|notification|permission|all]"
---

# Test Sound

Play a random notification sound to test the setup.

1. Run the play script with the optional category from `$ARGUMENTS` (default: `all`):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/play-sound.sh" ${ARGUMENTS:-all}
```

2. Report to the user that the sound was played. If no sound was heard, suggest:
   - Check volume with `/notif-sound:volume`
   - Check if sounds exist with `/notif-sound:list`
   - Check system volume
