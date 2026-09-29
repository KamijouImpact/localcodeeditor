#!/usr/bin/env python3
"""LocalCodeEditor local API. Bind to loopback only; intended for Termux on-device use."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, shutil, subprocess, tempfile, urllib.parse, mimetypes

ROOT = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", int(os.environ.get("LOCALCODE_PORT", "8765"))
MAX_BODY = 1_000_000
RUNNERS = {
    "python": ["python", "-I"],
    "node": ["node"],
    "php": ["php"],
}

def safe_path(raw):
    p = (ROOT / raw).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise ValueError("Path escapes project directory")
    if ".localcodeeditor_tmp" in p.parts:
        raise ValueError("Reserved path")
    return p

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length < 1 or length > MAX_BODY:
            raise ValueError("Request body missing or too large (max 1 MB)")
        return json.loads(self.rfile.read(length))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            self.send_json(200, {"ok": True, "root": str(ROOT), "runtimes": {k: shutil.which(v[0]) is not None for k, v in RUNNERS.items()}})
            return
        if parsed.path == "/api/files":
            entries = []
            for p in sorted(ROOT.rglob("*")):
                if not p.is_file() or any(x.startswith(".") for x in p.relative_to(ROOT).parts):
                    continue
                entries.append({"path": p.relative_to(ROOT).as_posix(), "size": p.stat().st_size})
                if len(entries) >= 1000: break
            self.send_json(200, {"files": entries})
            return
        if parsed.path == "/api/file":
            try:
                p = safe_path(urllib.parse.parse_qs(parsed.query).get("path", [""])[0])
                if not p.is_file(): return self.send_json(404, {"error": "File not found"})
                if p.stat().st_size > MAX_BODY: return self.send_json(413, {"error": "File too large"})
                self.send_json(200, {"path": p.relative_to(ROOT).as_posix(), "content": p.read_text(encoding="utf-8")})
            except (ValueError, UnicodeError) as e:
                self.send_json(400, {"error": str(e)})
            return
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        try:
            data = self.read_json()
            if parsed.path == "/api/file":
                p = safe_path(str(data.get("path", "")))
                content = data.get("content")
                if not isinstance(content, str): raise ValueError("content must be text")
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
                return self.send_json(200, {"ok": True, "path": p.relative_to(ROOT).as_posix()})
            if parsed.path == "/api/run":
                lang = data.get("language")
                code = data.get("code", "")
                if lang not in RUNNERS: raise ValueError("Supported runtimes: python, node, php")
                if not isinstance(code, str) or len(code.encode()) > 200_000: raise ValueError("Code must be text under 200 KB")
                executable = shutil.which(RUNNERS[lang][0])
                if not executable: return self.send_json(400, {"error": f"{lang} runtime is not installed"})
                suffix = {"python": ".py", "node": ".js", "php": ".php"}[lang]
                with tempfile.TemporaryDirectory(prefix="lce-") as td:
                    script = Path(td) / ("main" + suffix)
                    script.write_text(code, encoding="utf-8")
                    cmd = [executable] + RUNNERS[lang][1:] + [str(script)]
                    try:
                        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=10, env={**os.environ, "TERM": "dumb"})
                        self.send_json(200, {"exitCode": proc.returncode, "stdout": proc.stdout[-20000:], "stderr": proc.stderr[-20000:]})
                    except subprocess.TimeoutExpired as e:
                        self.send_json(200, {"exitCode": 124, "stdout": (e.stdout or "")[-20000:] if isinstance(e.stdout, str) else "", "stderr": "Execution timed out after 10 seconds."})
                return
            self.send_json(404, {"error": "Unknown API endpoint"})
        except (ValueError, json.JSONDecodeError, OSError) as e:
            self.send_json(400, {"error": str(e)})

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

if __name__ == "__main__":
    print(f"LocalCodeEditor API: http://{HOST}:{PORT}")
    print(f"Project folder: {ROOT}")
    print("Local only. Do not change HOST to 0.0.0.0 on an untrusted network.")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
