import asyncio
import json
from typing import Dict, Set
import websockets as Socket

ROOMS: Dict[str, Set[Socket]] = {}


def get_id(path: str) -> str:
    params = path[path.index("?"):]
    room_id = params.split("=")[1]
    return room_id


async def handle(socket: Socket):
    room_id = get_id(socket.path)

    if room_id not in ROOMS:
        ROOMS[room_id] = set()

    room_connections = ROOMS[room_id]
    async with asyncio.Lock():
        room_connections.add(socket)
        print(str(socket.id))
        pass

    try:
        async for message in socket:
            Socket.broadcast(room_connections, json.dumps({
                "con": len(room_connections),
                "mes": message,
                "id": str(socket.id)
            }))
    finally:
        async with asyncio.Lock():
            room_connections.remove(socket)
            if len(room_connections) == 0:
                del ROOMS[room_id]
                print(f"room id: {room_id} deleted")


async def main():
    async with Socket.serve(handle, "localhost", 8765):
        print("server is on...")
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
