#!/usr/bin/env python3
"""notif-sound GUI server — serves web dashboard and API on port 6998."""

import http.server
import json
import os
import platform
import random
import shutil
import stat
import subprocess
import sys
import urllib.parse
import re

PLUGIN_ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/.claude/plugins/data/notif-sound-local")
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 6998

SOUNDS_DIR = os.path.join(PLUGIN_ROOT, "sounds")
GUI_DIR = os.path.join(PLUGIN_ROOT, "gui")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")


def get_config():
    try:
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
            # Validate volume
            vol = cfg.get("volume", 4)
            if not isinstance(vol, int) or vol < 1 or vol > 10:
                cfg["volume"] = 4
            return cfg
    except Exception:
        return {"volume": 4}


def save_config(cfg):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def list_sounds():
    files = []
    if os.path.isdir(SOUNDS_DIR):
        for f in sorted(os.listdir(SOUNDS_DIR)):
            if f.lower().endswith((".mp3", ".wav")):
                filepath = os.path.join(SOUNDS_DIR, f)
                if os.path.isfile(filepath):
                    files.append({
                        "name": f,
                        "size": os.path.getsize(filepath),
                    })
    return files


def _safe_path(base, untrusted):
    """Resolve a path and ensure it stays within base directory."""
    resolved = os.path.realpath(os.path.join(base, untrusted))
    if not resolved.startswith(os.path.realpath(base) + os.sep) and resolved != os.path.realpath(base):
        return None
    return resolved


SCRIPTS = ["play-sound.sh", "gui-server.sh", "gui-server.py"]


def _is_windows():
    """Detect Windows (native, Git Bash/MINGW, MSYS)."""
    return sys.platform in ("win32", "msys") or platform.system() == "Windows"


def _is_executable(path):
    """Check if a file exists and has the executable bit set for the owner.
    On Windows, executable bits are meaningless — just check the file exists."""
    try:
        if not os.path.isfile(path):
            return False
        if _is_windows():
            return True
        return (os.stat(path).st_mode & stat.S_IXUSR) != 0
    except OSError:
        return False


def _detect_player():
    """Detect the available audio player command for the current OS."""
    system = platform.system()
    if system == "Darwin":
        path = shutil.which("afplay")
        if path:
            return {"name": "afplay", "path": path}
    elif system == "Linux":
        for cmd in ("paplay", "aplay"):
            path = shutil.which(cmd)
            if path:
                return {"name": cmd, "path": path}
    elif _is_windows():
        path = shutil.which("powershell.exe") or shutil.which("powershell")
        if path:
            return {"name": "powershell.exe", "path": path}
    else:
        for cmd in ("paplay", "powershell.exe"):
            path = shutil.which(cmd)
            if path:
                return {"name": cmd, "path": path}
    return None


def verify_setup():
    """Run all verification checks and return a structured result."""
    checks = []
    all_ok = True

    # 1. Script permissions
    scripts_dir = os.path.join(PLUGIN_ROOT, "scripts")
    for name in SCRIPTS:
        path = os.path.join(scripts_dir, name)
        exists = os.path.isfile(path)
        executable = _is_executable(path) if exists else False
        ok = exists and executable
        if not ok:
            all_ok = False
        checks.append({
            "id": f"script_{name}",
            "label": f"Script: {name}",
            "ok": ok,
            "detail": "executable" if ok else ("missing" if not exists else "not executable"),
        })

    # 2. Sound files
    sounds = list_sounds()
    sounds_ok = len(sounds) > 0
    if not sounds_ok:
        all_ok = False
    checks.append({
        "id": "sounds",
        "label": "Sound files",
        "ok": sounds_ok,
        "detail": f"{len(sounds)} sound(s) found" if sounds_ok else "no .mp3 or .wav files in sounds/",
    })

    # 3. Audio player
    player = _detect_player()
    player_ok = player is not None
    if not player_ok:
        all_ok = False
    checks.append({
        "id": "player",
        "label": "Audio player",
        "ok": player_ok,
        "detail": player["name"] if player else "no supported player found",
    })

    # 4. Data directory writable
    data_ok = False
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        test_file = os.path.join(DATA_DIR, ".write-test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        data_ok = True
    except OSError:
        pass
    if not data_ok:
        all_ok = False
    checks.append({
        "id": "data_dir",
        "label": "Data directory",
        "ok": data_ok,
        "detail": "writable" if data_ok else "not writable",
    })

    # 5. Config readable
    cfg = get_config()
    checks.append({
        "id": "config",
        "label": "Config",
        "ok": True,
        "detail": f"volume={cfg.get('volume', 4)}",
    })

    return {"ok": all_ok, "checks": checks}


def fix_permissions():
    """Fix executable permissions on all plugin scripts. Returns list of fixed files.
    On Windows, chmod is a no-op on NTFS — permissions are always OK."""
    if _is_windows():
        return []
    fixed = []
    scripts_dir = os.path.join(PLUGIN_ROOT, "scripts")
    for name in SCRIPTS:
        path = os.path.join(scripts_dir, name)
        if os.path.isfile(path) and not _is_executable(path):
            try:
                current = os.stat(path).st_mode
                os.chmod(path, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                fixed.append(name)
            except OSError:
                pass
    return fixed


def play_sound(filename=None):
    """Play a sound file through the system audio player at the configured volume.

    If filename is None, picks a random sound. Returns a dict with success/error info.
    """
    sounds = list_sounds()
    if not sounds:
        return {"error": "No sound files found"}

    player = _detect_player()
    if not player:
        return {"error": "No audio player available"}

    # On Windows with PowerShell, only .wav is supported
    win_wav_only = _is_windows() and player["name"] == "powershell.exe"

    if filename:
        file_path = _safe_path(SOUNDS_DIR, filename)
        if not file_path or not os.path.isfile(file_path):
            return {"error": "Sound file not found"}
        if not filename.lower().endswith((".mp3", ".wav")):
            return {"error": "Unsupported format"}
        if win_wav_only and not filename.lower().endswith(".wav"):
            return {"error": "Windows only supports .wav files"}
    else:
        candidates = sounds
        if win_wav_only:
            candidates = [s for s in sounds if s["name"].lower().endswith(".wav")]
        if not candidates:
            return {"error": "No compatible sound files found (.wav required on Windows)"}
        chosen = random.choice(candidates)
        filename = chosen["name"]
        file_path = os.path.join(SOUNDS_DIR, filename)

    cfg = get_config()
    volume = cfg.get("volume", 4)

    try:
        system = platform.system()
        if system == "Darwin":
            afplay_vol = round(volume / 10, 1)
            subprocess.Popen(
                [player["path"], "-v", str(afplay_vol), file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif system == "Linux" and player["name"] == "paplay":
            pa_vol = int(volume * 6553.6)
            subprocess.Popen(
                [player["path"], "--volume=" + str(pa_vol), file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif _is_windows() and player["name"] == "powershell.exe":
            win_path = os.path.abspath(file_path).replace("'", "''")
            subprocess.Popen(
                [player["path"], "-c",
                 f"(New-Object Media.SoundPlayer '{win_path}').PlaySync()"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.Popen(
                [player["path"], file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except OSError as e:
        return {"error": f"Failed to play: {e.strerror}"}

    return {"success": True, "file": filename, "volume": volume}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=GUI_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/config":
            self._json_response(get_config())
        elif parsed.path == "/api/sounds":
            self._json_response(list_sounds())
        elif parsed.path == "/api/verify":
            self._json_response(verify_setup())
        elif parsed.path == "/api/status":
            self._json_response({
                "plugin": "notif-sound",
                "version": "1.0.0",
                "config": get_config(),
                "sounds": list_sounds(),
                "hooks": ["Stop", "Notification", "PreToolUse (AskUserQuestion)", "PermissionRequest"]
            })
        elif parsed.path.startswith("/sounds/"):
            # Serve sound files for browser playback — validate path stays in SOUNDS_DIR
            filename = urllib.parse.unquote(parsed.path[len("/sounds/"):])
            file_path = _safe_path(SOUNDS_DIR, filename)
            if file_path and os.path.isfile(file_path):
                self.send_response(200)
                if file_path.endswith(".mp3"):
                    self.send_header("Content-Type", "audio/mpeg")
                elif file_path.endswith(".wav"):
                    self.send_header("Content-Type", "audio/wav")
                else:
                    self._json_response({"error": "Unsupported format"}, 400)
                    return
                self.send_header("Content-Length", os.path.getsize(file_path))
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._json_response({"error": "Not found"}, 404)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/config":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 4096:
                self._json_response({"error": "Request too large"}, 413)
                return
            try:
                body = json.loads(self.rfile.read(content_length))
            except (json.JSONDecodeError, ValueError):
                self._json_response({"error": "Invalid JSON"}, 400)
                return
            cfg = get_config()
            if "volume" in body:
                try:
                    vol = int(body["volume"])
                except (ValueError, TypeError):
                    self._json_response({"error": "Volume must be an integer"}, 400)
                    return
                if 1 <= vol <= 10:
                    cfg["volume"] = vol
                else:
                    self._json_response({"error": "Volume must be 1-10"}, 400)
                    return
            save_config(cfg)
            self._json_response(cfg)

        elif parsed.path == "/api/play":
            result = play_sound()
            status = 200 if result.get("success") else 400
            self._json_response(result, status)

        elif parsed.path.startswith("/api/play/"):
            filename = urllib.parse.unquote(parsed.path[len("/api/play/"):])
            if not filename or "/" in filename or "\\" in filename or filename in (".", ".."):
                self._json_response({"error": "Invalid filename"}, 400)
                return
            result = play_sound(filename)
            status = 200 if result.get("success") else 400
            self._json_response(result, status)

        elif parsed.path == "/api/verify/fix":
            fixed = fix_permissions()
            result = verify_setup()
            result["fixed"] = fixed
            self._json_response(result)

        elif parsed.path == "/api/sounds/upload":
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                self._json_response({"error": "Expected multipart/form-data"}, 400)
                return

            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 10 * 1024 * 1024:  # 10 MB max
                self._json_response({"error": "File too large (max 10 MB)"}, 413)
                return
            body = self.rfile.read(content_length)

            # Extract boundary from content type
            boundary_match = re.search(r"boundary=(.+)", content_type)
            if not boundary_match:
                self._json_response({"error": "No boundary found"}, 400)
                return
            boundary = boundary_match.group(1).strip().encode()

            # Parse multipart parts
            parts = body.split(b"--" + boundary)
            filename = None
            file_data = None

            for part in parts:
                if b"Content-Disposition" not in part:
                    continue
                header_end = part.find(b"\r\n\r\n")
                if header_end == -1:
                    continue
                header_section = part[:header_end].decode("utf-8", errors="replace")
                part_body = part[header_end + 4:]
                # Strip trailing \r\n
                if part_body.endswith(b"\r\n"):
                    part_body = part_body[:-2]

                name_match = re.search(r'name="([^"]+)"', header_section)
                if not name_match:
                    continue
                field_name = name_match.group(1)

                if field_name == "file":
                    fn_match = re.search(r'filename="([^"]+)"', header_section)
                    if fn_match:
                        # Sanitize filename: basename only, no path traversal
                        filename = os.path.basename(fn_match.group(1))
                        file_data = part_body

            if filename and file_data:
                if filename.lower().endswith((".mp3", ".wav")):
                    os.makedirs(SOUNDS_DIR, exist_ok=True)
                    dest = os.path.join(SOUNDS_DIR, filename)
                    with open(dest, "wb") as f:
                        f.write(file_data)
                    self._json_response({"success": True, "file": filename})
                else:
                    self._json_response({"error": "Only .mp3 and .wav files are supported"}, 400)
            else:
                self._json_response({"error": "No file provided"}, 400)
        else:
            self._json_response({"error": "Not found"}, 404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)

        # DELETE /api/sounds/<filename>
        if parsed.path.startswith("/api/sounds/"):
            parts = parsed.path.split("/")
            if len(parts) == 4:  # ['', 'api', 'sounds', filename]
                filename = urllib.parse.unquote(parts[3])
                # Validate: must be a simple filename, no path separators
                if "/" in filename or "\\" in filename or filename in (".", ".."):
                    self._json_response({"error": "Invalid filename"}, 400)
                    return
                filepath = _safe_path(SOUNDS_DIR, filename)
                if filepath and os.path.isfile(filepath):
                    os.remove(filepath)
                    self._json_response({"success": True, "deleted": filename})
                else:
                    self._json_response({"error": "File not found"}, 404)
            else:
                self._json_response({"error": "Invalid path"}, 400)
        else:
            self._json_response({"error": "Not found"}, 404)

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", f"http://localhost:{PORT}")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", f"http://localhost:{PORT}")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress request logs


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"notif-sound GUI running on http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
