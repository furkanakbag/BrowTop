import asyncio
import json
import pathlib
import subprocess
import ssl
import base64
import psutil
from aiohttp import web

# Basic Authentication Middleware
async def auth_middleware(app, handler):
    async def middleware_handler(request):
        if request.path in ["/monitor", "/ws"]:
            auth_header = request.headers.get("Authorization")
            if auth_header is None or not validate_auth(auth_header):
                headers = {"WWW-Authenticate": 'Basic realm="Server Monitor"'}
                return web.Response(text="Unauthorized", status=401, headers=headers)
        return await handler(request)
    return middleware_handler

def validate_auth(auth_header):
    """Validate Basic Auth credentials."""
    auth_type, encoded_credentials = auth_header.split(" ", 1)
    if auth_type.lower() != "basic":
        return False
    decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
    username, password = decoded_credentials.split(":", 1)
    return username == "admin" and password == "password"

async def monitor(request):
    """Serve the HTML monitor page."""
    path = pathlib.Path(__file__).parents[0].joinpath("monitor.html")
    return web.FileResponse(path)

async def get_system_stats():
    """Collect system statistics."""
    processes = [{
        "pid": p.pid,
        "name": p.name(),
        "cpu": p.cpu_percent(interval=0.1),
        "memory": p.memory_info().rss / (1024 * 1024),  # Convert to MB
        "status": p.status()
    } for p in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_info', 'status'])]

    # Process summary
    process_states = [p["status"] for p in processes]
    summary = {
        "running": process_states.count(psutil.STATUS_RUNNING),
        "sleeping": process_states.count(psutil.STATUS_SLEEPING),
        "stopped": process_states.count(psutil.STATUS_STOPPED),
        "zombie": process_states.count(psutil.STATUS_ZOMBIE),
        "total": len(processes),
    }

    # Last 50 lines of system log
    try:
        with open('/var/log/syslog', 'r') as log_file:
            logs = log_file.readlines()[-50:]
    except FileNotFoundError:
        logs = ["Log file not found."]

    # Last 10 logged users
    try:
        last_output = subprocess.check_output(["last", "-n", "10"]).decode("utf-8").splitlines()
        logged_users = [line.split()[0] for line in last_output if line and not line.startswith("wtmp")]
    except Exception as e:
        logged_users = [f"Error fetching logged users: {str(e)}"]

    stats = {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage("/")._asdict(),
        "load_avg": psutil.getloadavg(),
        "processes": processes,
        "process_summary": summary,
        "uptime": int(psutil.boot_time()),
        "users": [user.name for user in psutil.users()],
        "system_logs": logs,
        "logged_users": logged_users,
    }
    return stats

async def send_stats(request):
    """Send system stats to WebSocket client."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.text and msg.data == "stats":
            data = await get_system_stats()
            response = ["stats", data]
            await ws.send_str(json.dumps(response))
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
    """Start WebSocket server."""
    ssl_context = create_ssl_context()
    app = web.Application(middlewares=[auth_middleware])
    app.add_routes(
        [
            web.get("/ws", send_stats),
            web.get("/monitor", monitor),
        ]
    )
    web.run_app(app, port=8765, ssl_context=ssl_context)

if __name__ == "__main__":
    print("Server started at wss://localhost:8765")
    run()
