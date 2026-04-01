---
description: "Start or stop the web GUI dashboard for managing notification sounds. Use when the user wants a visual interface."
argument-hint: "[start|stop]"
---

# GUI Dashboard

Start or stop the notif-sound web dashboard at http://localhost:6998.

If `$ARGUMENTS` is empty or `start`:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/gui-server.sh" start
```

If `$ARGUMENTS` is `stop`:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/gui-server.sh" stop
```

Report the result:
- On start: "GUI running at http://localhost:6998 — opened in browser"
- On stop: "GUI server stopped"
