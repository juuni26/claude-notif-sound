#!/usr/bin/env python3
"""notif-sound GUI server — serves web dashboard and API on port 6998."""

import http.server
import json
import os
import sys
import urllib.parse
import html
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


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=GUI_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/config":
            self._json_response(get_config())
        elif parsed.path == "/api/sounds":
            self._json_response(list_sounds())
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
        self.send_header("Access-Control-Allow-Origin", "http://localhost:6998")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "http://localhost:6998")
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
