import asyncio
import json
import pathlib
import psutil
from aiohttp import web


async def get_system_stats():
    """Collect system statistics."""
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage("/")._asdict(),
        "processes": [
            proc.info for proc in psutil.process_iter(["pid", "name", "cpu_percent"])
        ],
        "logged_users": [user._asdict() for user in psutil.users()],
        "uptime": psutil.boot_time()
    }


async def get_logs():
    """Get the last 50 lines of the system log."""
    with open("/var/log/syslog", "r") as f:
        return f.readlines()[-50:]


async def send_stats(request):
    """Send system stats to WebSocket client."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.text and msg.data == "stats":
            stats = await get_system_stats()
            logs = await get_logs()
            await ws.send_str(json.dumps({"stats": stats, "logs": logs}))
        elif msg.type == web.WSMsgType.close:
            break

    return ws


async def monitor(request):
    path = pathlib.Path(__file__).parent / "monitor.html"
    return web.FileResponse(path)


def create_ssl_context():
    ssl_context = web.SSLContext()
    ssl_context.load_cert_chain("cert/localhost.crt", "cert/localhost.key")
    return ssl_context


if __name__ == "__main__":
    app = web.Application()
    app.router.add_get("/monitor", monitor)
    app.router.add_get("/ws", send_stats)

    ssl_context = create_ssl_context()
    web.run_app(app, port=8765, ssl_context=ssl_context)
