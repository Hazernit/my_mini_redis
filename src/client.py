import argparse
import socket


def send_command(host, port, command):
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall((command.strip() + "\n").encode("utf-8"))
        return sock.recv(4096).decode("utf-8").strip()


def interactive_client(host, port):
    print(f"Connected to Mini Redis Server at {host}:{port}")
    print("Commands: SET key value, GET key, DELETE key, EXISTS key, EXIT")

    while True:
        command = input("mini-redis> ").strip()
        if not command:
            continue
        response = send_command(host, port, command)
        print(response)
        if command.upper() in {"EXIT", "QUIT"}:
            break


def parse_args():
    parser = argparse.ArgumentParser(description="CLI client for Mini Redis Server")
    parser.add_argument("--host", default="127.0.0.1", help="TCP server host")
    parser.add_argument("--port", default=6379, type=int, help="TCP server port")
    parser.add_argument("command", nargs="*", help="Command to execute once")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command:
        print(send_command(args.host, args.port, " ".join(args.command)))
    else:
        interactive_client(args.host, args.port)
