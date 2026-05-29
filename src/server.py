import argparse
from datetime import datetime
import socket
import threading


STORE = {}
COMMAND_LOG = []
MAX_LOG_ENTRIES = 50
LOG_OUTPUT_LIMIT = 10
STORE_LOCK = threading.Lock()


def execute_command(line):
    parts = line.strip().split(maxsplit=2)
    if not parts:
        return "ERROR empty command"

    command = parts[0].upper()

    if command == "PING":
        if len(parts) != 1:
            return "ERROR usage: PING"
        return "PONG"

    if command == "SET":
        if len(parts) != 3:
            return "ERROR usage: SET key value"
        key, value = parts[1], parts[2]
        with STORE_LOCK:
            STORE[key] = value
        return "OK"

    if command == "GET":
        if len(parts) != 2:
            return "ERROR usage: GET key"
        with STORE_LOCK:
            value = STORE.get(parts[1])
        return value if value is not None else "NULL"

    if command == "DELETE":
        if len(parts) != 2:
            return "ERROR usage: DELETE key"
        with STORE_LOCK:
            existed = parts[1] in STORE
            STORE.pop(parts[1], None)
        return "1" if existed else "0"

    if command == "EXISTS":
        if len(parts) != 2:
            return "ERROR usage: EXISTS key"
        with STORE_LOCK:
            exists = parts[1] in STORE
        return "1" if exists else "0"

    if command == "KEYS":
        if len(parts) != 1:
            return "ERROR usage: KEYS"
        with STORE_LOCK:
            keys = sorted(STORE.keys())
        return ", ".join(keys) if keys else "EMPTY"

    if command == "FLUSH":
        if len(parts) != 1:
            return "ERROR usage: FLUSH"
        with STORE_LOCK:
            STORE.clear()
        return "OK"

    if command == "UPDATE":
        if len(parts) != 3:
            return "ERROR usage: UPDATE key value"
        key, value = parts[1], parts[2]
        with STORE_LOCK:
            if key not in STORE:
                return "KEY_NOT_FOUND"
            STORE[key] = value
        return "OK"

    if command == "LOG":
        if len(parts) != 1:
            return "ERROR usage: LOG"
        with STORE_LOCK:
            entries = list(COMMAND_LOG[-LOG_OUTPUT_LIMIT:])
        return format_log_entries(entries)

    return "ERROR unknown command"


def execute_and_log(line):
    response = execute_command(line)
    record_command(line, response)
    return response


def record_command(line, result):
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "command": line.strip(),
        "result": summarize_result(result),
    }
    with STORE_LOCK:
        COMMAND_LOG.append(entry)
        del COMMAND_LOG[:-MAX_LOG_ENTRIES]


def summarize_result(result):
    clean_result = " ".join(result.split())
    if len(clean_result) > 120:
        return clean_result[:117] + "..."
    return clean_result


def format_log_entries(entries):
    if not entries:
        return "EMPTY"
    return " || ".join(
        f"{entry['time']} | {entry['command']} | {entry['result']}"
        for entry in entries
    )


def handle_client(connection, address):
    with connection:
        file = connection.makefile("rwb")
        for raw_line in file:
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            if line.upper() in {"QUIT", "EXIT"}:
                file.write(b"BYE\n")
                file.flush()
                break
            response = execute_and_log(line)
            file.write((response + "\n").encode("utf-8"))
            file.flush()
    print(f"Client disconnected: {address[0]}:{address[1]}")


def run_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Mini Redis Server is running on {host}:{port}")

        while True:
            connection, address = server_socket.accept()
            print(f"Client connected: {address[0]}:{address[1]}")
            thread = threading.Thread(
                target=handle_client,
                args=(connection, address),
                daemon=True,
            )
            thread.start()


def parse_args():
    parser = argparse.ArgumentParser(description="TCP Mini Redis Server")
    parser.add_argument("--host", default="127.0.0.1", help="TCP host")
    parser.add_argument("--port", default=6379, type=int, help="TCP port")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_server(args.host, args.port)
