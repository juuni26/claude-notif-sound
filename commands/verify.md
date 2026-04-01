---
description: "Verify notif-sound plugin setup: check script permissions, sound files, and test playback. Use after install or when sounds aren't working."
---

# Verify Setup

Check that the notif-sound plugin is correctly set up and ready to play sounds.

Run ALL of these checks:

1. Fix permissions (make scripts executable):

```bash
chmod +x "${CLAUDE_PLUGIN_ROOT}/scripts/play-sound.sh" "${CLAUDE_PLUGIN_ROOT}/scripts/gui-server.sh" "${CLAUDE_PLUGIN_ROOT}/scripts/gui-server.py" 2>/dev/null && echo "Permissions OK"
```

2. Check sound files exist:

```bash
ls -1 "${CLAUDE_PLUGIN_ROOT}/sounds/" 2>/dev/null | grep -E '\.(mp3|wav)$' || echo "NO_SOUNDS"
```

3. Check data directory and config:

```bash
mkdir -p "${CLAUDE_PLUGIN_DATA}" && echo "Data dir OK: ${CLAUDE_PLUGIN_DATA}"
cat "${CLAUDE_PLUGIN_DATA}/config.json" 2>/dev/null || echo '{"volume": 4} (using default)'
```

4. Test playback:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/play-sound.sh"
```

5. Present a summary to the user:
   - Scripts: permissions fixed or already executable
   - Sounds: count of .mp3/.wav files found
   - Volume: current setting
   - Playback: whether test sound played
   - If anything is wrong, suggest the fix (e.g., `/notif-sound:add` if no sounds, `/notif-sound:volume` to adjust volume)
   - Mention that `/notif-sound:gui` also shows live status in the dashboard
