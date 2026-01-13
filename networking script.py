import asyncio
import json

async def broadcast_state(game_to_net, clients):
    while True:
        msg = game_to_net.get()
        encoded = json.dumps(msg).encode() + b"\n"

        dead = []
        for writer in list(clients):
            try:
                writer.write(encoded)
                await writer.drain()
            except:
                dead.append(writer)

        for w in dead:
            clients.remove(w)