"""HTTP API for the maritime wireless digital-twin minimum loop.

Run:
    python backend/app.py
"""

from __future__ import annotations

import json
import random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    from .channel_model import predict_channel
except ImportError:  # Supports `python backend/app.py`.
    from channel_model import predict_channel


HOST = "127.0.0.1"
PORT = 8000


class TwinRequestHandler(BaseHTTPRequestHandler):
    server_version = "MaritimeTwinAPI/0.1"

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_json(200, {"ok": True})

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send_json(200, {"ok": True, "service": "maritime-twin-api"})
            return
        self._send_json(404, {"ok": False, "error": f"Unknown endpoint: {path}"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/channel/predict":
                self._send_json(200, {"ok": True, "prediction": predict_channel(payload)})
                return
            if path == "/api/dataset/sample":
                self._send_json(200, {"ok": True, "samples": build_samples(payload)})
                return
            self._send_json(404, {"ok": False, "error": f"Unknown endpoint: {path}"})
        except Exception as exc:  # pragma: no cover - defensive API boundary
            self._send_json(500, {"ok": False, "error": str(exc)})


def build_samples(payload: dict[str, Any]) -> list[dict[str, Any]]:
    count = int(payload.get("count", 8))
    count = max(1, min(count, 128))
    base = dict(payload.get("basePayload", {}))
    samples: list[dict[str, Any]] = []
    for _ in range(count):
        sample = {
            **base,
            "airTemp": random.uniform(18.0, 32.0),
            "seaTemp": random.uniform(20.0, 32.0),
            "rh": random.uniform(50.0, 95.0),
            "windSpeed": random.uniform(1.0, 14.0),
            "frequency": random.choice([700, 1800, 2600, 3500, 4900]),
            "ductHeight": random.uniform(0.0, 35.0),
        }
        samples.append({"input": sample, "output": predict_channel(sample)})
    return samples


def run() -> None:
    server = ThreadingHTTPServer((HOST, PORT), TwinRequestHandler)
    print(f"Maritime twin API listening at http://{HOST}:{PORT}")
    print(f"Workspace: {Path.cwd()}")
    server.serve_forever()


if __name__ == "__main__":
    run()
