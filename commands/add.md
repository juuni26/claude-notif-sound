---
description: "Add a new sound file to the notification sounds library. Use when the user wants to add, import, or install a custom sound."
argument-hint: "<file-path>"
---

# Add Sound File

The user wants to add a new sound file to the notif-sound plugin.

1. Parse `$ARGUMENTS` to extract the file path
2. Validate the file exists and is `.mp3` or `.wav`:

```bash
test -f "<path>" && echo "File exists" || echo "File not found"
```

3. Copy the file to the sounds directory:

```bash
cp "<path>" "${CLAUDE_PLUGIN_ROOT}/sounds/"
```

4. Confirm to the user which file was added
5. Play the newly added sound as confirmation:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/play-sound.sh"
```
