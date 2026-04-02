---
description: "Set the notification sound volume (1-10). Use when the user wants to change volume, make sounds louder or quieter."
argument-hint: "<1-10>"
---

# Set Volume

The user wants to change the notification sound volume.

**Important:** First check the platform:

```bash
uname -s
```

If the output starts with `MINGW` or `MSYS` (Windows), inform the user:
> Volume control is not supported on Windows — PowerShell's `Media.SoundPlayer` has no volume property. Adjust your system volume instead.

Then stop — do not proceed with the steps below.

---

**On macOS/Linux**, proceed:

1. If `$ARGUMENTS` is empty, read and report the current volume:

```bash
cat "${CLAUDE_PLUGIN_DATA}/config.json"
```

2. If `$ARGUMENTS` is provided, validate it is an integer between 1 and 10

3. Update the volume in config.json:

```bash
# Detect Python (python3, python, or py)
PYTHON_CMD=""
for cmd in python3 python py; do
  if command -v "$cmd" &>/dev/null; then
    PYTHON_CMD="$cmd"
    break
  fi
done
[ -z "$PYTHON_CMD" ] && echo "Python not found" && exit 1

$PYTHON_CMD -c "
import json, sys, os
cfg_path = '${CLAUDE_PLUGIN_DATA}/config.json'
os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
try:
    with open(cfg_path) as f:
        cfg = json.load(f)
except:
    cfg = {}
vol = int(sys.argv[1])
if vol < 1 or vol > 10:
    print('Error: volume must be 1-10')
    sys.exit(1)
cfg['volume'] = vol
with open(cfg_path, 'w') as f:
    json.dump(cfg, f, indent=2)
print(f'Volume set to {vol}/10')
" "$ARGUMENTS"
```

4. Play a test sound at the new volume:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/play-sound.sh"
```

5. Report the new volume to the user.
