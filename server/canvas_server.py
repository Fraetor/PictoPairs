import socket
import threading
from dataclasses import dataclass
import numpy as np
import cv2


HOST = "0.0.0.0"
PORT = 12345

WIDTH_PIX  = 228
HEIGHT_PIX = 80
SCALE = 16

clients = []
clients_lock = threading.Lock()

def handle_client(conn, addr, active_clients):
    print(f"[CONNECTED] {addr}")

    try:
        while True:
            # recieve event from client
            data = conn.recv(5)

            if not data:
                continue

            message = tuple(data)
            print(f"[{addr}] {message}")

            if message == (0,): raise ConnectionResetError

            #Forward it to other clients
            with clients_lock:
                for ex_conn, ex_addr in active_clients:
                    if ex_addr == addr: continue
                    ex_conn.send(data)
                
    except (ConnectionResetError, OSError):
        pass

    finally:
        with clients_lock:
            if (conn, addr) in active_clients:
                print("BYE BYE")
                active_clients.remove((conn, addr))

        conn.close()
        print(f"[DISCONNECTED] {addr}")
        print(active_clients)


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[LISTENING] {HOST}:{PORT}")

    active_clients = []

    try:
        while True:
            conn, addr = server.accept()

            with clients_lock:
                active_clients.append((conn,addr))

            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr, active_clients),
                daemon=True
            )
            thread.start()

            print(f"[ACTIVE CLIENTS] {threading.active_count() - 1}")
            with clients_lock:
                print(active_clients)

    except KeyboardInterrupt:
        print("\nShutting down server...")

    finally:
        server.close()

        with clients_lock:
            for conn, addr in active_clients:
                conn.close()

            clients.clear()


if __name__ == "__main__":
    main()