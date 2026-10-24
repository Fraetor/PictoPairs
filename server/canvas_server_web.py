import asyncio

from websockets.asyncio.server import serve

HOST = "0.0.0.0"
PORT = 12345

WIDTH_PIX = 228
HEIGHT_PIX = 80
SCALE = 16

active_clients = set()


async def handle_client(websocket):
    addr = websocket.remote_address
    active_clients.add(websocket)

    print(f"[CONNECTED] {addr}")
    print(f"[ACTIVE CLIENTS] {len(active_clients)}")

    try:
        async for data in websocket:
            if isinstance(data, str):
                print(f"[ERROR] Expected binary data from {addr}")
                continue

            message = tuple(data)
            print(f"[{addr}] {message}")

            # Preserve the original disconnect command.
            if message == (0,):
                await websocket.close()
                break

            # Forward the message to every other connected client.
            recipients = active_clients.copy()
            recipients.discard(websocket)

            if recipients:
                results = await asyncio.gather(
                    *(client.send(data) for client in recipients),
                    return_exceptions=True,
                )

                # Log failed deliveries.
                for client, result in zip(recipients, results):
                    if isinstance(result, Exception):
                        print(f"[SEND ERROR] {client.remote_address}: {result}")

    except Exception as exc:
        print(f"[CONNECTION ERROR] {addr}: {exc}")

    finally:
        active_clients.discard(websocket)

        print("BYE BYE")
        print(f"[DISCONNECTED] {addr}")
        print(f"[ACTIVE CLIENTS] {len(active_clients)}")


async def main():
    print(f"[LISTENING] {HOST}:{PORT}")

    async with serve(handle_client, HOST, PORT, max_size=1024 * 1024):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down server...")
