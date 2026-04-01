![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-blueviolet)
![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux%20|%20Windows%20|%20WSL-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

# notif-sound

> **Never miss when Claude needs your attention.**

## The Problem

I open Claude Code, prompt something, switch tabs, lose focus — and don't even realize it's already finished or waiting for my next action. That's frustrating. There's no official notification solution — Claude Code runs completely silent.

So I built **notif-sound**. It plays a sound the moment Claude needs my attention. I've been using it personally and I'm sharing it here so anyone with the same frustration can use it too.

## Demo

<!-- Video demo will be added here -->

## Getting Started

You don't need to be a developer to set this up. Just follow these steps inside Claude Code:

### Prerequisites

You likely already have everything you need. The plugin uses tools that come pre-installed on most systems.

| Platform | What you need | Already installed? |
|----------|--------------|-------------------|
| **macOS** | `afplay`, `python3` | Yes — both are built-in |
| **Linux** | `python3`, `paplay` or `aplay` | Usually yes |
| **Windows** | `python3`, `powershell` | `powershell` is built-in. Install Python 3 from [python.org](https://www.python.org/downloads/) or via `winget install Python.Python.3` |
| **WSL** | `python3` | Yes — pre-installed in WSL |

### Installation

**Step 1** — Add the plugin marketplace:

```
/plugin marketplace add juuni26/claude-plugins-marketplace
```

**Step 2** — Install the plugin:

```
/plugin install notif-sound
```

**Step 3** — Reload plugins to activate:

```
/reload-plugins
```

**Step 4** — Verify everything works:

```
/notif-sound:verify
```

Claude will run a few checks and ask for permission to execute the verification scripts. **Allow the permissions** — this is just the plugin checking that sounds can play on your system.

If all checks pass, you're done. Notification sounds will now play automatically whenever Claude finishes, asks a question, or needs your approval.

> **Tip:** Run `/notif-sound:test` to hear what it sounds like.

## GUI Dashboard

The easiest way to manage your sounds and settings is through the built-in web dashboard.

**Launch it:**

```
/notif-sound:gui
```

This opens a web dashboard at `http://localhost:6998` where you can:

- **Adjust volume** — drag the slider from 1 to 10
- **Preview sounds** — click play on any sound in your library
- **Add new sounds** — drag and drop `.wav` files (Windows) or `.mp3`/`.wav` files (macOS/Linux) right into the browser
- **Remove sounds** — hover over a sound and click the delete button
- **Check status** — see at a glance if everything is working

To stop the dashboard server:

```
/notif-sound:gui stop
```

<!-- GUI screenshot/video will be added here -->

## Features

- **4 hook events** — Stop, AskUserQuestion, PermissionRequest, Notification
- **Volume control** — intuitive 1-10 scale via `/notif-sound:volume` or GUI slider
- **Custom sounds** — add your own sound files, a random one plays each time
- **Web GUI dashboard** — visual sound management at `localhost:6998`
- **Smart dedup** — PID-based tracking skips if a sound is already playing
- **Cross-OS** — macOS (`afplay`), Linux (`paplay`/`aplay`), Windows (`powershell`), WSL (`powershell.exe`)
- **Minimal dependencies** — uses built-in OS audio tools + Python 3
- **Non-blocking** — all playback runs in background, never slows down Claude

## Commands

| Command | Description |
|---------|-------------|
| `/notif-sound:test` | Play a test sound |
| `/notif-sound:volume <1-10>` | Set volume level |
| `/notif-sound:list` | List all sounds |
| `/notif-sound:add <path>` | Add a sound file |
| `/notif-sound:remove <name>` | Remove a sound file |
| `/notif-sound:gui` | Open web dashboard |
| `/notif-sound:status` | Check plugin health |
| `/notif-sound:verify` | Verify setup and fix issues |
| `/notif-sound:test-hooks` | Test all 4 hooks sequentially |
| `/notif-sound:uninstall` | Cleanly remove the plugin |

---

## Advanced

### Hook Events

| Event | Trigger | Why it matters |
|-------|---------|----------------|
| `Stop` | Claude finished responding | Know when to come back |
| `Notification` | Background agent done | Don't miss async results |
| `PreToolUse` (AskUserQuestion) | Claude asks you a question | Blockers need fast response |
| `PermissionRequest` | Claude needs tool approval | Blockers need fast response |

### OS Support

| OS | Audio Player | Volume Control | Formats |
|----|-------------|---------------|---------|
| macOS | `afplay` | Yes (0.0-1.0) | .mp3, .wav, .aac, .m4a |
| Linux | `paplay` (primary), `aplay` (fallback) | Yes (`paplay`), No (`aplay`) | .mp3 (`paplay`), .wav (both) |
| Windows | `powershell` (`Media.SoundPlayer`) | No (system volume) | .wav only |
| WSL | `paplay` (if available), `powershell.exe` (fallback) | Yes (`paplay`), No (PowerShell) | .mp3 (`paplay`), .wav (PowerShell) |

> **Windows note:** Only `.wav` files are supported on native Windows because PowerShell's `Media.SoundPlayer` does not support `.mp3`. The plugin ships with `default.wav` which works out of the box.

### Volume

Volume is a **limiter**, not an amplifier. Setting it to 10 means 100% of your system volume — to go louder, turn up your OS volume.

| Volume | macOS (`afplay -v`) | Linux (`paplay --volume`) |
|--------|---------------------|---------------------------|
| 1 | 0.1 (10%) | 6,554 (~10%) |
| 4 (default) | 0.4 (40%) | 26,214 (~40%) |
| 7 | 0.7 (70%) | 45,875 (~70%) |
| 10 | 1.0 (100%) | 65,536 (100%) |

> WSL's PowerShell `SoundPlayer` does not support volume control — sounds play at system volume.

### Local Install (Alternative)

If you prefer not to use the marketplace:

```bash
# Clone the plugin
git clone https://github.com/juuni26/claude-notif-sound.git ~/.claude/plugins/local/notif-sound

# Make scripts executable
chmod +x ~/.claude/plugins/local/notif-sound/scripts/*.sh

# Launch Claude with the plugin
claude --plugin-dir ~/.claude/plugins/local/notif-sound
```

### Custom Sounds

The plugin ships with `default.mp3` and `default.wav` — royalty-free sounds from [Pixabay](https://pixabay.com/sound-effects/technology-new-notification-036-485897/). Add your own files for variety — a random sound is picked each time a hook fires.

```bash
# Use the slash command
/notif-sound:add ~/my-sound.wav

# Or drag and drop via the web GUI
/notif-sound:gui
```

```
sounds/
  default.mp3          # included sample
  default.wav          # WAV version (Windows compatible)
  my-notification.wav  # your custom sounds
```

### How Deduplication Works

Multiple hooks can fire in rapid succession (e.g., `AskUserQuestion` + `Stop`). The plugin uses PID-based tracking to prevent overlapping sounds — before playing, it checks if a previous audio process is still alive via `kill -0`. If yes, it skips the new sound.

### Plugin Structure

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
│   ├── status.md            # /notif-sound:status
│   ├── test.md              # /notif-sound:test
│   ├── test-hooks.md        # /notif-sound:test-hooks
│   ├── uninstall.md         # /notif-sound:uninstall
│   ├── verify.md            # /notif-sound:verify
│   └── volume.md            # /notif-sound:volume
├── gui/
│   └── index.html           # Single-file web dashboard
├── sounds/                  # Drop sound files here
│   ├── default.mp3          # Included sample
│   └── default.wav          # WAV version
├── .gitignore
└── LICENSE
```

### How It Works

This plugin uses [Claude Code hooks](https://code.claude.com/docs/hooks) — user-defined shell commands that execute automatically at specific lifecycle points. When a hook event fires, Claude Code runs `play-sound.sh` which:

1. Checks if a previous sound is still playing (PID-based dedup) — skips if so
2. Reads volume from `config.json`
3. Picks a random sound from `sounds/`
4. Plays it in the background via the OS audio player
5. Sends a terminal bell (`\a`) for Dock bounce / taskbar flash

#### Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_PLUGIN_ROOT` | Plugin installation directory (set by Claude Code) |
| `CLAUDE_PLUGIN_DATA` | Persistent data directory (survives plugin updates) |

## Tested On

- Windows 11
- macOS Tahoe

## References

- [Claude Code Hooks](https://code.claude.com/docs/hooks) — full hooks reference
- [Claude Code Documentation](https://code.claude.com/docs) — full docs index
