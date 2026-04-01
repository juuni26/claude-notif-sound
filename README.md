# notif-sound

> Never miss when Claude needs you.

Audio alerts for Claude Code — plays notification sounds when Claude finishes responding, asks a question, needs permission, or sends a notification.

## Install

```bash
claude --plugin-dir ~/.claude/plugins/local/notif-sound
```

## Commands

| Command | Description |
|---------|-------------|
| `/notif-sound:test` | Play a test sound |
| `/notif-sound:volume <1-10>` | Set volume level |
| `/notif-sound:list` | List all sounds by category |
| `/notif-sound:add <path>` | Add a sound file |
| `/notif-sound:remove <name>` | Remove a sound file |
| `/notif-sound:gui` | Open web dashboard (port 6998) |

## Hooks

| Event | When |
|-------|------|
| Stop | Claude finished responding |
| Notification | Background agent done, system alert |
| AskUserQuestion | Claude asks you a question (blocker) |
| PermissionRequest | Claude needs tool approval (blocker) |

## Sound Categories

Place sounds in category folders for event-specific audio:

- `sounds/all/` — fallback for all events
- `sounds/stop/` — only for Stop events
- `sounds/question/` — only for questions
- `sounds/notification/` — only for notifications
- `sounds/permission/` — only for permission requests

## OS Support

- macOS (`afplay`)
- Linux (`paplay` / `aplay`)
- WSL (`powershell.exe` fallback)

## License

MIT
