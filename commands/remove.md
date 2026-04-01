---
description: "Remove a sound file from the notification sounds library. Use when the user wants to delete or remove a sound."
argument-hint: "<filename>"
---

# Remove Sound

The user wants to remove a sound file from the plugin.

1. Search for the file by name across all category directories:

```bash
find "${CLAUDE_PLUGIN_ROOT}/sounds" -name "$ARGUMENTS" -type f
```

2. If found, show the full path and confirm deletion
3. Delete the file:

```bash
rm "${CLAUDE_PLUGIN_ROOT}/sounds/<category>/$ARGUMENTS"
```

4. Confirm removal to the user
5. If not found, list available sounds so the user can pick the right name
