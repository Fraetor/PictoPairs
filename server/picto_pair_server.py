import asyncio
import random
import threading

from websockets.asyncio.server import serve

HOST = "::1"
PORT = 12345

WIDTH_PIX = 228
HEIGHT_PIX = 80
SCALE = 16

#
#
#


class PictoChatServe:
    def __init__(self):
        self.active_clients = set()
        self.active_prompt = "A horse hosting HackNotts"

        self.pairs = []  # Active pairs
        ser = threading.Thread(target=self.serve)
        try:
            ser.start()
            asyncio.run(self.game_loop())
        except KeyboardInterrupt:
            print("\nShutting down server...")

    def serve(self):
        asyncio.run(self.begin_serve())

    def get_pair(self, socket):
        for p1, p2 in self.pairs:
            if socket == p1:
                return p2
            if socket == p2:
                return p1
        return None

    async def begin_serve(self):
        print(f"[LISTENING] {HOST}:{PORT}")

        async with serve(self.handle_client, HOST, PORT, max_size=1024 * 1024):
            await asyncio.Future()

    async def game_loop(self):
        while True:
            n_of_players = len(self.active_clients)
            print(f"N Players: {n_of_players}")
            # Assign players to teams
            if n_of_players < 4 and n_of_players % 2 != 0:
                print("Not enough players")
                continue  # Wait for players

            players = self.active_clients.copy()
            players = list(players)
            random.shuffle(players)

            self.pairs = zip(players[: n_of_players // 2], players[n_of_players // 2 :])
            print("[PAIRS ASSIGNED]")
            print(self.pairs)

            # Send prompt (start drawing!)
            self.send_promt()
            break

    def send_promt(self):
        for client in self.active_clients:
            print("[SENDING PROMPT]")
            client.send(bytes(0, 0, 0, 0, 254, self.active_prompt.encode()))

    async def handle_client(self, websocket):
        addr = websocket.remote_address
        self.active_clients.add(websocket)

        print(f"[CONNECTED] {addr}")
        print(f"[ACTIVE CLIENTS] {len(self.active_clients)}")

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

                # Forward the message to the corresponding pairs
                recipient = self.get_pair(websocket)

                if recipient == None:
                    # No pair..
                    continue

                results = await recipient.send(data)

        except Exception as exc:
            print(f"[CONNECTION ERROR] {addr}: {exc}")

        finally:
            self.active_clients.discard(websocket)

            print("BYE BYE")
            print(f"[DISCONNECTED] {addr}")
            print(f"[ACTIVE CLIENTS] {len(self.active_clients)}")


if __name__ == "__main__":
    PictoChatServe()
