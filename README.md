![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-blueviolet)
![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux%20|%20WSL-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

# notif-sound

> **Never miss when Claude needs you.**

Audio alerts for Claude Code — plays notification sounds when Claude finishes responding, asks a question, needs permission, or sends a notification. So you can multitask without babysitting your terminal.

## The Problem

I built this because I kept forgetting to check back on Claude. I'd ask it to do something, alt-tab to another app or grab coffee, and completely forget it was waiting for me — sometimes for minutes. It could be done, asking a question, or stuck waiting for permission, and I'd have no idea.

The problem is that Claude Code runs completely silent. There's no sound, no alert, nothing to pull you back. You either babysit the terminal or you miss things.

**notif-sound** fixes this. Now I hear a sound the moment Claude needs my attention — whether I'm in another app, another monitor, or across the room.

## Features

- **4 hook events** — Stop, AskUserQuestion, PermissionRequest, Notification
- **Volume control** — intuitive 1-10 scale via `/notif-sound:volume`
- **Custom sounds** — add your own .mp3/.wav files with `/notif-sound:add`
- **Web GUI dashboard** — visual sound management at `localhost:6998`
- **Smart dedup** — PID-based tracking skips if a sound is already playing
- **Cross-OS** — macOS (`afplay`), Linux (`paplay`/`aplay`), WSL (`powershell.exe`)
- **Minimal dependencies** — uses built-in OS audio tools + Python 3 (pre-installed on most systems)
- **Non-blocking** — all playback runs in background, never slows down Claude

## Prerequisites

You likely don't need to install anything — the plugin uses tools that come pre-installed on most systems.

| Platform | What you need | Already installed? |
|----------|--------------|-------------------|
| **macOS** | `afplay`, `python3` | Yes — both are built-in on macOS |
| **Linux** | `python3`, `paplay` or `aplay` | Usually yes. `python3` ships with most distros. `paplay` (PulseAudio) is standard on desktop installs; `aplay` (ALSA) is the fallback |
| **WSL** | `python3` | Yes — pre-installed in WSL. Audio falls back to `powershell.exe` if `paplay` isn't available |

**If something is missing:**

```bash
# Linux — install audio player if needed
sudo apt install pulseaudio-utils   # for paplay
# or
sudo apt install alsa-utils         # for aplay

# Linux — install Python 3 if needed
sudo apt install python3
```

> **Note:** Python 3 is used for reading config (volume), doing volume math, and running the optional web GUI. The core sound playback itself only needs `bash` and your OS audio player.

## Install

### Option A: Marketplace (recommended)

```bash
# Add the marketplace
/plugin marketplace add juuni26/claude-plugins-marketplace

# Install the plugin
/plugin install notif-sound
```

Hooks activate automatically. That's it.

### Option B: Local install

```bash
# Clone the plugin
git clone https://github.com/juuni26/claude-notif-sound.git ~/.claude/plugins/local/notif-sound

# Make scripts executable
chmod +x ~/.claude/plugins/local/notif-sound/scripts/*.sh

# Launch Claude with the plugin
claude --plugin-dir ~/.claude/plugins/local/notif-sound
```

### Add your own sounds

The plugin ships with `default.mp3` — a royalty-free sound from [Pixabay](https://pixabay.com/sound-effects/people-fah-469417/). Add your own `.mp3` or `.wav` files for variety — a random sound is picked each time a hook fires.

```bash
# Use the slash command
/notif-sound:add ~/my-sound.mp3

# Or use the web GUI to manage sounds visually
/notif-sound:gui
```

## Commands

| Command | Description |
|---------|-------------|
| `/notif-sound:test` | Play a test sound |
| `/notif-sound:volume <1-10>` | Set volume level |
| `/notif-sound:list` | List all sounds |
| `/notif-sound:add <path>` | Add a sound file |
| `/notif-sound:remove <name>` | Remove a sound file |
| `/notif-sound:gui` | Open web dashboard |
| `/notif-sound:test-hooks` | Test all 4 hooks sequentially |

## Hook Events

| Event | Trigger | Why it matters |
|-------|---------|----------------|
| `Stop` | Claude finished responding | Know when to come back |
| `Notification` | Background agent done | Don't miss async results |
| `PreToolUse` (AskUserQuestion) | Claude asks you a question | Blockers need fast response |
| `PermissionRequest` | Claude needs tool approval | Blockers need fast response |

## Sounds

The plugin includes `default.mp3` (royalty-free, from [Pixabay](https://pixabay.com/sound-effects/people-fah-469417/)). Drop your own `.mp3` or `.wav` files into the `sounds/` directory — a random sound is picked each time.

```
sounds/
  default.mp3          # included sample
  my-notification.mp3  # your custom sounds
  ding.wav
```

## Volume

Volume is a **limiter**, not an amplifier. Setting it to 10 means 100% of your system volume — to go louder, turn up your OS volume.

| Volume | macOS (`afplay -v`) | Linux (`paplay --volume`) |
|--------|---------------------|---------------------------|
| 1 | 0.1 (10%) | 6,554 (~10%) |
| 4 (default) | 0.4 (40%) | 26,214 (~40%) |
| 7 | 0.7 (70%) | 45,875 (~70%) |
| 10 | 1.0 (100%) | 65,536 (100%) |

> WSL's PowerShell `SoundPlayer` does not support volume control — sounds play at system volume.

## Web GUI

Run `/notif-sound:gui` to open a web dashboard at `http://localhost:6998`:

- Volume slider with live config updates
- Sound list with play/delete
- Drag-and-drop sound upload
- Plugin status display

Stop the server with `/notif-sound:gui stop`.

## OS Support

| OS | Audio Player | Volume Control | Formats |
|----|-------------|---------------|---------|
| macOS | `afplay` | Yes (0.0-1.0) | .mp3, .wav, .aac, .m4a |
| Linux | `paplay` (primary), `aplay` (fallback) | Yes (`paplay`), No (`aplay`) | .mp3 (`paplay`), .wav (both) |
| WSL | `paplay` (if available), `powershell.exe` (fallback) | Yes (`paplay`), No (PowerShell) | .mp3 (`paplay`), .wav (PowerShell) |

## How Deduplication Works

Multiple hooks can fire in rapid succession (e.g., `AskUserQuestion` + `Stop`). The plugin uses PID-based tracking to prevent overlapping sounds — before playing, it checks if a previous audio process is still alive via `kill -0`. If yes, it skips the new sound. No race conditions, no stale locks, no interference with other audio apps.

## Plugin Structure

```
notif-sound/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── hooks/
│   └── hooks.json           # Hook definitions
├── scripts/
│   ├── play-sound.sh        # Main playback engine
│   ├── gui-server.sh        # Web GUI launcher
│   └── gui-server.py        # Web GUI API server
├── commands/
│   ├── add.md               # /notif-sound:add
│   ├── gui.md               # /notif-sound:gui
│   ├── list.md              # /notif-sound:list
│   ├── remove.md            # /notif-sound:remove
│   ├── test.md              # /notif-sound:test
│   ├── test-hooks.md        # /notif-sound:test-hooks
│   └── volume.md            # /notif-sound:volume
├── gui/
│   └── index.html           # Single-file web dashboard
├── sounds/                  # Drop .mp3/.wav files here
│   ├── default.mp3          # Included sample
│   └── default.wav          # WAV version (WSL compatibility)
├── .gitignore
└── LICENSE
```

## How It Works

This plugin uses [Claude Code hooks](https://code.claude.com/docs/hooks) — user-defined shell commands that execute automatically at specific lifecycle points. When a hook event fires, Claude Code runs `play-sound.sh` which:

1. Checks if a previous sound is still playing (PID-based dedup) — skips if so
2. Reads volume from `config.json`
3. Picks a random sound from `sounds/`
4. Plays it in the background via the OS audio player
5. Sends a terminal bell (`\a`) for Dock bounce / taskbar flash

### Hook Configuration

Hooks are defined in `hooks/hooks.json` and activate automatically when the plugin is installed. Each hook entry specifies:
- **Event** — when it fires (`Stop`, `PreToolUse`, etc.)
- **Matcher** — optional filter (e.g., only `AskUserQuestion` for `PreToolUse`)
- **Command** — the shell command to run

No manual configuration in `~/.claude/settings.json` is needed. See the [hooks reference](https://code.claude.com/docs/hooks) for all available events.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_PLUGIN_ROOT` | Plugin installation directory (set by Claude Code) |
| `CLAUDE_PLUGIN_DATA` | Persistent data directory (survives plugin updates) |

## References

- [Claude Code Hooks](https://code.claude.com/docs/hooks) — full hooks reference (all events, configuration format, exit codes)
- [Hooks Guide](https://code.claude.com/docs/hooks-guide) — quick start guide for writing hooks
- [Claude Code Settings](https://code.claude.com/docs/settings) — where hooks and plugins are configured
- [Claude Code Skills](https://code.claude.com/docs/skills) — how slash commands work
- [Claude Code MCP](https://code.claude.com/docs/mcp) — Model Context Protocol integration
- [Claude Code Documentation](https://code.claude.com/docs) — full docs index

## Contributing

Contributions welcome! Feel free to open issues or submit PRs.

**Sound files**: Don't commit copyrighted audio. Use royalty-free sounds only.

## License

MIT — see [LICENSE](LICENSE).
