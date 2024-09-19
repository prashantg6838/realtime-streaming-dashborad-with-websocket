import asyncio
import websockets
import json

connected_clients = set()

async def handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # Broadcast message to all clients
            for client in connected_clients:
                await client.send(message)
    finally:
        connected_clients.remove(websocket)

async def send_to_websocket(data):
    message = json.dumps(data)
    # You can broadcast this message to all clients connected
    for client in connected_clients:
        await client.send(message)

start_server = websockets.serve(handler, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
