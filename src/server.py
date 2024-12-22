import asyncio
import json
import pathlib
import ssl

import psutil
from aiohttp import web

last_user = None  # Variable to track the last logged-in user

async def monitor(request):
    """Serve the monitor.html file."""
    html_path = pathlib.Path(__file__).parents[0].joinpath("monitor.html")
    return web.FileResponse(html_path)

async def get_system_stats():
    """Collect system statistics."""
    stats = {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage("/")._asdict(),
        "load_avg": psutil.getloadavg(),
    }
    return stats

async def send_stats(request):
    """Send system stats and user info to WebSocket client."""
    global last_user
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.text:
            try:
                data = json.loads(msg.data)
                if data["action"] == "stats":
                    stats = await get_system_stats()
                    await ws.send_str(json.dumps(["stats", stats]))
                elif data["action"] == "login":
                    last_user = data["username"]
                    await ws.send_str(json.dumps(["last_user", last_user]))
            except Exception as e:
                print(f"Error processing WebSocket message: {e}")
        elif msg.type == web.WSMsgType.close:
            break

    return ws

def create_ssl_context():
    """Create SSL context for secure WebSocket connection."""
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    cert_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.crt")
    key_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.key")
    ssl_context.load_cert_chain(cert_file, key_file)
    return ssl_context

def run():
    """Start the WebSocket server."""
    ssl_context = create_ssl_context()
    app = web.Application()
    app.add_routes(
        [
            web.get("/monitor", monitor),
            web.get("/ws", send_stats),
        ]
    )
    web.run_app(app, port=8765, ssl_context=ssl_context)

if __name__ == "__main__":
    print("Server started at wss://localhost:8765")
    run()
