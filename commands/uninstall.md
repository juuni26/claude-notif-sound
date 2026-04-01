---
description: "Cleanly uninstall the notif-sound plugin: stop GUI, remove cache, remove data. Use when the user wants to fully remove the plugin."
---

# Uninstall Plugin

Cleanly remove the notif-sound plugin and all its files.

**IMPORTANT:** Before running any steps, ask the user to confirm they want to uninstall. Tell them this will:
- Stop the GUI server if running
- Remove all cached plugin files
- Optionally remove saved config and data

Only proceed if the user confirms.

1. Stop the GUI server if running:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/gui-server.sh" stop 2>/dev/null; echo "GUI stopped"
```

2. Remove the plugin cache directory:

```bash
rm -rf ~/.claude/plugins/cache/juuni26-plugins/notif-sound && echo "Cache removed" || echo "No cache found"
```

3. Check if the marketplace directory is now empty, and clean it up if so:

```bash
[ -d ~/.claude/plugins/cache/juuni26-plugins ] && [ -z "$(ls -A ~/.claude/plugins/cache/juuni26-plugins 2>/dev/null)" ] && rm -rf ~/.claude/plugins/cache/juuni26-plugins && echo "Marketplace cache cleaned" || echo "Marketplace cache has other plugins, kept"
```

4. Ask the user if they also want to remove their saved config (volume settings). If yes:

```bash
rm -rf "${CLAUDE_PLUGIN_DATA}" && echo "Config removed" || echo "No config found"
```

If no, skip this step and tell them their config is kept at `${CLAUDE_PLUGIN_DATA}`.

5. Tell the user to run these two commands to finish:
   - `/plugin` → select notif-sound → uninstall (to remove plugin registration)
   - `/reload-plugins` (to refresh the plugin list)

6. Present a summary:
   - GUI server: stopped
   - Plugin cache: removed
   - Config/data: removed or kept (based on user choice)
   - Remind them to run `/plugin` uninstall + `/reload-plugins` to complete the removal
   - Thank them for using notif-sound!
