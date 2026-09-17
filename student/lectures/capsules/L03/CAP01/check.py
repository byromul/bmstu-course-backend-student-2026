"""Проверка четырёх операций через настоящий loopback HTTP."""

from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from router import route


class Handler(BaseHTTPRequestHandler):
    def dispatch(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        status, body = route(self.command, self.path, payload)
        encoded = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(encoded)

    do_GET = dispatch
    do_POST = dispatch

    def log_message(self, _format: str, *_args: object) -> None:
        return


def request(
    base: str, method: str, path: str, body: dict[str, object]
) -> dict[str, object]:
    data = json.dumps(body).encode() if method == "POST" else None
    with urlopen(Request(base + path, data=data, method=method), timeout=5) as response:
        return json.loads(response.read())


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        assert request(base, "POST", "/api/v1/characters/initialize", {})["hp"] == 10
        assert request(base, "GET", "/api/v1/scenes/START", {})["id"] == "START"
        assert request(base, "POST", "/api/v1/dice/rolls", {})["value"] == 4
        combat = request(
            base,
            "POST",
            "/api/v1/combat/attacks/resolve",
            {
                "player": {"name": "Герой", "hp": 10, "str": 3, "def": 2},
                "opponent": {"name": "Крыса", "hp": 4, "str": 2, "def": 1},
                "player_roll": 5,
                "opponent_roll": 2,
            },
        )
        assert combat == {
            "attacker": "player",
            "damage": 2,
            "player": {"name": "Герой", "hp": 10, "str": 3, "def": 2},
            "opponent": {"name": "Крыса", "hp": 2, "str": 2, "def": 1},
            "outcome": "continue",
        }
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print("CAP01 ПРОЙДЕНА: четыре HTTP-операции ответили на loopback-порту")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
