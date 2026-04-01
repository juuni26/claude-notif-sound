---
description: "Set the notification sound volume (1-10). Use when the user wants to change volume, make sounds louder or quieter."
argument-hint: "<1-10>"
---

# Set Volume

The user wants to change the notification sound volume.

1. If `$ARGUMENTS` is empty, read and report the current volume:

```bash
cat "${CLAUDE_PLUGIN_DATA}/config.json"
```

2. If `$ARGUMENTS` is provided, validate it is an integer between 1 and 10

3. Update the volume in config.json:

```bash
python3 -c "
import json, sys
cfg_path = '${CLAUDE_PLUGIN_DATA}/config.json'
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
bash "${CLAUDE_PLUGIN_ROOT}/scripts/play-sound.sh" all
```

5. Report the new volume to the user.
