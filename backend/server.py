
"""Local static web server + optional Gemini proxy for LifeQuest AI.

Run from project root: python backend/server.py
Copy .env.example -> .env and set GEMINI_API_KEY to enable real AI.
Only binds to 127.0.0.1; this is a local development server, NOT a
public production proxy. GitHub Pages cannot execute Python.
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_BODY_BYTES = 1024 * 1024
MODEL_PATTERN = re.compile(r"gemini-[A-Za-z0-9.-]{1,60}\Z")


def load_local_env() -> None:
    """Lightweight .env reader; never overrides existing environment vars."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        name = name.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            continue
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(name, value)


class LifeQuestHandler(BaseHTTPRequestHandler):
    server_version = "LifeQuestLocal/1.0"

    def send_bytes(self, status: int, payload: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def send_json(self, status: int, payload: dict) -> None:
        self.send_bytes(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                        "application/json; charset=utf-8")

    def do_GET(self) -> None:
        path = unquote(urlsplit(self.path).path)
        if path == "/api/health":
            return self.send_json(200, {"ok": True,
                                        "gemini_configured": bool(os.getenv("GEMINI_API_KEY"))})
        if path == "/":
            path = "/index.html"
        rel = path.lstrip("/")
        # Never serve .env, .git, backend scripts or private files.
        permitted = rel == "index.html" or rel.startswith("src/")
        if not permitted or "\\" in rel or ".." in Path(rel).parts:
            return self.send_json(404, {"error": "Not found"})
        target = (PROJECT_ROOT / rel).resolve()
        if not target.is_relative_to(PROJECT_ROOT.resolve()) or not target.is_file():
            return self.send_json(404, {"error": "Not found"})
        mime = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if mime.startswith("text/") or mime in ("application/javascript", "application/json"):
            mime += "; charset=utf-8"
        return self.send_bytes(200, target.read_bytes(), mime)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/gemini":
            return self.send_json(404, {"error": "Not found"})
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            return self.send_json(503, {"error": "Set GEMINI_API_KEY in your local .env file."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.send_json(400, {"error": "Invalid content length"})
        if length < 1 or length > MAX_BODY_BYTES:
            return self.send_json(413, {"error": "Request body must be 1 MB or less."})
        try:
            data = json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, ValueError):
            return self.send_json(400, {"error": "Expected JSON body"})
        if not isinstance(data, dict):
            return self.send_json(400, {"error": "Expected JSON object"})
        model = data.get("model", "gemini-2.5-flash")
        body = data.get("body")
        if not isinstance(model, str) or not MODEL_PATTERN.fullmatch(model):
            return self.send_json(400, {"error": "Invalid Gemini model"})
        if not isinstance(body, dict) or not isinstance(body.get("contents"), list):
            return self.send_json(400, {"error": "Invalid Gemini request body"})

        url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent"
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        request = Request(url, data=payload, method="POST", headers={
            "Content-Type": "application/json", "x-goog-api-key": api_key,
        })
        try:
            with urlopen(request, timeout=35) as response:
                upstream_body = response.read(2 * MAX_BODY_BYTES)
                return self.send_bytes(response.status, upstream_body,
                                       "application/json; charset=utf-8")
        except HTTPError as error:
            # Pass Google's JSON error back to the client; never expose our API key.
            remote_body = error.read(16 * 1024)
            self.send_bytes(error.code, remote_body or b'{"error":"Gemini request failed"}',
                            "application/json; charset=utf-8")
        except (URLError, TimeoutError):
            self.send_json(502, {"error": "Gemini service unavailable"})


def main() -> None:
    load_local_env()
    port = int(os.environ.get("LIFEQUEST_PORT", "8000"))
    with ThreadingHTTPServer(("127.0.0.1", port), LifeQuestHandler) as server:
        print(f"LifeQuest AI V11.6: http://127.0.0.1:{port}")
        print("Gemini AI:", "configured" if os.environ.get("GEMINI_API_KEY") else
              "not configured (offline game works)")
        print("Press Ctrl+C to stop.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
