import asyncio
import json
import pathlib
import ssl
import time
import psutil
from aiohttp import web


PASSWORD = "123"  
last_users = []  
current_user = None  

async def authenticate(ws, username, password):
    """Authenticate the user."""
    global last_users, current_user
    if password == PASSWORD:
        current_user = username
        
        last_users.append(username)
        if len(last_users) > 10:
            last_users.pop(0)
        await ws.send_str(json.dumps(["auth_status", {"status": "success"}]))
        await ws.send_str(json.dumps(["last_users", last_users]))
        await ws.send_str(json.dumps(["current_user", current_user]))
    else:
        await ws.send_str(json.dumps(["auth_status", {"status": "failure"}]))


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
        "uptime": get_system_uptime(),
        "processes": await get_process_list(),
        "process_summary": get_process_summary(),
        "logs": get_system_logs(),
    }
    return stats

def get_system_uptime():
    """Get system uptime as a human-readable string."""
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, minutes = divmod(remainder, 3600)[0], divmod(remainder, 60)[1]
    return f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"

async def get_process_list():
    """Fetch list of processes."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return sorted(processes, key=lambda x: x.get("cpu_percent", 0), reverse=True)[:10]  # Top 10 processes

def get_process_summary():
    """Get summary of the number of processes and their states."""
    process_states = {
        "running": 0,
        "sleeping": 0,
        "stopped": 0,
        "zombie": 0,
        "other": 0,
    }

    for proc in psutil.process_iter(['status']):
        try:
            status = proc.info['status']
            if status == psutil.STATUS_RUNNING:
                process_states["running"] += 1
            elif status == psutil.STATUS_SLEEPING:
                process_states["sleeping"] += 1
            elif status == psutil.STATUS_STOPPED:
                process_states["stopped"] += 1
            elif status == psutil.STATUS_ZOMBIE:
                process_states["zombie"] += 1
            else:
                process_states["other"] += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    total_processes = sum(process_states.values())
    return {"total": total_processes, **process_states}

def get_system_logs():
    """Fetch the last 50 lines of the system log."""
    log_path = '/var/log/syslog' if pathlib.Path('/var/log/syslog').exists() else '/var/log/messages'
    try:
        with open(log_path, 'r') as log_file:
            logs = log_file.readlines()[-50:]  # Get the last 50 lines
        return logs if logs else ["No logs available."]
    except FileNotFoundError:
        return ["Log file not found."]
    except PermissionError:
        return ["Permission denied while reading logs."]
    except Exception as e:
        return [f"Error reading logs: {str(e)}"]

async def send_stats(request):
    """Send system stats and user info to WebSocket client."""
    global last_users, current_user
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
                    username = data["username"]
                    password = data["password"]
                    await authenticate(ws, username, password)
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
