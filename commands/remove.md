---
description: "Remove a sound file from the notification sounds library. Use when the user wants to delete or remove a sound."
argument-hint: "<filename>"
---

# Remove Sound

The user wants to remove a sound file from the plugin.

1. Check if the file exists in the sounds directory:

```bash
ls "${CLAUDE_PLUGIN_ROOT}/sounds/" | grep -E '\.(mp3|wav)$'
```

2. If `$ARGUMENTS` matches a file, show the full path and confirm deletion
3. Delete the file (use basename to prevent path traversal):

```bash
SAFE_NAME="$(basename "$ARGUMENTS")"
rm "${CLAUDE_PLUGIN_ROOT}/sounds/$SAFE_NAME"
```

4. Confirm removal to the user
5. If not found, list available sounds so the user can pick the right name
