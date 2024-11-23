import asyncio
import json
import pathlib
import ssl

import psutil
from websockets import WebSocketException
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed


async def get_system_stats():
    """Collect system statistics."""
    stats = {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage("/")._asdict(),
        "load_avg": psutil.getloadavg(),
    }
    return stats


async def send_stats(websocket):
    """Send system stats to WebSocket client."""
    print("Client connected")
    try:
        while True:
            stats = await get_system_stats()
            await websocket.send(json.dumps(stats))
            await asyncio.sleep(1)  # Send updates every second
    except ConnectionClosed as e:
        print("Client disconnected", e)
    except WebSocketException as e:
        print("WebSocket Exception", e)


def create_ssl_context():
    """Create SSL context for secure WebSocket connection."""
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    cert_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.crt")
    key_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.key")
    ssl_context.load_cert_chain(cert_file, key_file)
    return ssl_context


async def run():
    """Start WebSocket server."""
    ssl_context = create_ssl_context()
    server = await serve(send_stats, "localhost", 8765, ssl=ssl_context)
    await server.serve_forever()


if __name__ == "__main__":
    print("Server started at wss://localhost:8765")
    asyncio.run(run())
