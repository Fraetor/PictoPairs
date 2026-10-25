import asyncio
import random
import threading
import time
from websockets.asyncio.server import serve

HOST = "::1"
PORT = 12345

WIDTH_PIX = 228
HEIGHT_PIX = 80
SCALE = 16

DEFAULT_PROMPTS = ["A horse hosting HackNotts",
                   "Volcano in A32",
                   "The joy of greggs sausage roll",
                   "The smallest hacker ever",
                   "Haskell: finally useful",
                   "Hamster playing tetris",
                   "Team 9 wins Hacknotts!",
                   "85kg of Quiche..."]

class PictoChatServe:
    def __init__(self):
        self.active_clients = set()
        self.active_prompt = random.choice(DEFAULT_PROMPTS)

        self.pairs = []  # Active pairs
        self.art   = []

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
            self.pairs = []  # Active pairs
            self.art   = []
            n_of_players = len(self.active_clients)
            # Assign players to teams
            if n_of_players < 4 or n_of_players % 2 != 0:
                continue  # Wait for players

            players = self.active_clients.copy()
            players = list(players)
            random.shuffle(players)

            self.pairs = list(zip(players[: n_of_players // 2], players[n_of_players // 2 :]))
            print("[PAIRS ASSIGNED]")
            print(self.pairs)

            # Send prompt (start drawing!)
            await self.send_prompt()

            await self.countdown(25)
            await self.send_end()
            await asyncio.sleep(2)

            # Players should send back histories, and clear the canvas
            await self.send_art()

            mess = bytes((0,0,0,0, 251))
            choice = random.choice(self.active_clients) 
            await choice.send(mess) 

            # Everyone gets to see the art
            await self.countdown(12)

            # Choose next prompt
            self.active_prompt = random.choice(DEFAULT_PROMPTS)



    async def countdown(self, seconds):
        count = seconds
        while count > -1:
            for client in self.active_clients:
                mess = bytes((count,0,0,0,252))
                await client.send(mess)
            count -= 1
            await asyncio.sleep(1)

    async def send_art(self):
        print(f"[SENDING ART] {len(self.art)}")
        for client in self.active_clients:
            for artist, art in self.art:
                if artist != client:
                    mess = bytes((0,0,0,0,253)) + art.encode()
                    print(len(mess)) 
                    print(mess[:20])
                    await client.send(mess)

    async def send_end(self):
            for client in self.active_clients:
                print("[SENDING PROMPT]")
                await client.send(bytes((0, 0, 0, 0, 255)))

    async def send_prompt(self):
        for client in self.active_clients:
            print("[SENDING PROMPT]")
            await client.send(bytes((0, 0, 0, 0, 254)) + self.active_prompt.encode())

    async def handle_client(self, websocket):
        addr = websocket.remote_address
        self.active_clients.add(websocket)

        print(f"[CONNECTED] {addr}")
        print(f"[ACTIVE CLIENTS] {len(self.active_clients)}")

        try:
            async for data in websocket:
                
                if isinstance(data, str):
                    if data.startswith('data:'):
                        self.art.append((websocket, data))
                    elif data != "":
                        self.active_prompt = data
                    else:
                        self.active_prompt = random.choice(DEFAULT_PROMPTS)
                try:
                    message = tuple(data)

                    # Forward the message to the corresponding pairs
                    recipient = self.get_pair(websocket)
    
                    if recipient == None:
                        # No pair..
                        continue
    
                    results = await recipient.send(data)
                    print(f"[{addr}] {message}")
                except:
                    # Not a tuple
                    pass
                    

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
