---
description: "Add a new sound file to the notification sounds library. Use when the user wants to add, import, or install a custom sound."
argument-hint: "<file-path> [--category stop|question|notification|permission|all]"
---

# Add Sound File

The user wants to add a new sound file to the notif-sound plugin.

1. Parse `$ARGUMENTS` to extract the file path and optional `--category` flag (default: `all`)
2. Valid categories: `all`, `stop`, `question`, `notification`, `permission`
3. Validate the file exists and is `.mp3` or `.wav`:

```bash
test -f "<path>" && echo "File exists" || echo "File not found"
```

4. Copy the file to the appropriate category directory:

```bash
cp "<path>" "${CLAUDE_PLUGIN_ROOT}/sounds/<category>/"
```

5. Confirm to the user: which file was added, to which category
6. Play the newly added sound as confirmation:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/play-sound.sh" <category>
```
