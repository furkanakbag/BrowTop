import asyncio
import json
import os
from aiohttp import web
import psutil
import logging
import ssl


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password for authentication
PASSWORD = "secure_password"

# WebSocket clients
connected_clients = []

# Routes and WebSocket handlers
async def index(request):
    # Serve the HTML file for the root route
    html_path = os.path.join(os.path.dirname(__file__), 'monitor.html')
    if os.path.exists(html_path):
        return web.FileResponse(html_path)
    logger.error(f"HTML file not found at path: {html_path}")
    return web.Response(text="HTML file not found", status=404)

async def authenticate(request):
    data = await request.json()
    if data.get("password") == PASSWORD:
        return web.json_response({"status": "success"})
    return web.json_response({"status": "failure"}, status=401)

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    connected_clients.append(ws)
    logger.info("New WebSocket client connected")

    try:
        while True:
            stats = get_system_stats()
            await ws.send_json(stats)
            await asyncio.sleep(2)  # Update interval
    except asyncio.CancelledError:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        connected_clients.remove(ws)
    return ws

# System stats functions
def get_system_stats():
    process_info = get_process_list()
    users = [user.name for user in psutil.users()]
    uptime = psutil.boot_time()

    return {
        "cpu": psutil.cpu_percent(interval=None),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage('/')._asdict(),
        "load": os.getloadavg(),
        "processes": process_info,
        "logged_in_users": users,
        "uptime": uptime,
        "log": get_system_logs(),
    }

def get_process_list():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Skip processes that can't be accessed
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)

def get_system_logs():
    try:
        with open('/var/log/syslog', 'r') as log_file:
            lines = log_file.readlines()[-50:]
        return lines
    except FileNotFoundError:
        return ["Log file not found"]
    except PermissionError:
        return ["Log file is not accessible. Please check permissions."]

# Main app setup
app = web.Application()
app.router.add_get('/', index)  # Serve the HTML file
app.router.add_post('/authenticate', authenticate)  # Handle authentication
app.router.add_get('/ws', websocket_handler)  # WebSocket for live stats

if __name__ == '__main__':
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('/app/cert/localhost.crt', '/app/cert/localhost.key')
    web.run_app(app, host='0.0.0.0', port=8765, ssl_context=ssl_context)

