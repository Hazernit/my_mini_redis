import argparse
import json
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer


REDIS_HOST = os.getenv("MINI_REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("MINI_REDIS_PORT", "6379"))


def call_tcp_server(command):
    with socket.create_connection((REDIS_HOST, REDIS_PORT), timeout=5) as sock:
        sock.sendall((command.strip() + "\n").encode("utf-8"))
        return sock.recv(4096).decode("utf-8").strip()


class MiniRedisApiHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(200, {"ok": True})

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"ok": True, "service": "mini-redis-api"})
            return
        self._send_json(404, {"ok": False, "error": "Route not found"})

    def do_POST(self):
        if self.path != "/command":
            self._send_json(404, {"ok": False, "error": "Route not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            command = build_command(payload)
            result = call_tcp_server(command)
            self._send_json(200, {"ok": True, "command": command, "result": result})
        except ValueError as error:
            self._send_json(400, {"ok": False, "error": str(error)})
        except OSError as error:
            self._send_json(
                503,
                {
                    "ok": False,
                    "error": "Mini Redis Server is unavailable",
                    "details": str(error),
                },
            )
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "Invalid JSON body"})

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))


def build_command(payload):
    command = str(payload.get("command", "")).upper()
    key = str(payload.get("key", "")).strip()
    value = str(payload.get("value", "")).strip()

    commands_with_key = {"GET", "DELETE", "EXISTS"}
    commands_with_key_value = {"SET", "UPDATE"}
    commands_without_args = {"PING", "KEYS", "FLUSH", "LOG"}
    allowed_commands = commands_with_key | commands_with_key_value | commands_without_args

    if command not in allowed_commands:
        raise ValueError(
            "Command must be SET, GET, DELETE, EXISTS, PING, KEYS, FLUSH, UPDATE, or LOG"
        )
    if command in commands_without_args:
        return command
    if command in commands_with_key and not key:
        raise ValueError("Key is required")
    if command in commands_with_key_value:
        if not key:
            raise ValueError("Key is required")
        if not value:
            raise ValueError(f"Value is required for {command}")
        return f"{command} {key} {value}"
    return f"{command} {key}"


def parse_args():
    parser = argparse.ArgumentParser(description="HTTP API for Mini Redis demo site")
    parser.add_argument("--host", default="127.0.0.1", help="HTTP API host")
    parser.add_argument("--port", default=8080, type=int, help="HTTP API port")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    server = HTTPServer((args.host, args.port), MiniRedisApiHandler)
    print(f"HTTP API is running on http://{args.host}:{args.port}")
    print(f"Forwarding commands to Mini Redis Server at {REDIS_HOST}:{REDIS_PORT}")
    server.serve_forever()
