---
description: "Add a new sound file to the notification sounds library. Use when the user wants to add, import, or install a custom sound."
argument-hint: "<file-path>"
---

# Add Sound File

The user wants to add a new sound file to the notif-sound plugin.

1. Parse `$ARGUMENTS` to extract the file path
2. Check the OS — on Windows (MINGW/MSYS), only `.wav` files are supported. On other platforms, `.mp3` and `.wav` are both accepted.
3. Validate the file exists and has a supported extension:

```bash
test -f "<path>" && echo "File exists" || echo "File not found"
```

If the user is on Windows and the file is `.mp3`, tell them: "Windows only supports `.wav` files because PowerShell's Media.SoundPlayer cannot play `.mp3`. Please convert it to `.wav` first."

4. Copy the file to the sounds directory:

```bash
cp "<path>" "${CLAUDE_PLUGIN_ROOT}/sounds/"
```

5. Confirm to the user which file was added
6. Play the newly added sound as confirmation:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/play-sound.sh"
```
