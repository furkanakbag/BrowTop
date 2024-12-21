import asyncio
import json
import os
import psutil
from aiohttp import web

PASSWORD = "Furkan&arda2752"

async def handle_stats(request):
    auth_header = request.headers.get('Authorization')
    if auth_header != PASSWORD:
        return web.Response(status=401, text="Unauthorized")

    stats = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk_usage": psutil.disk_usage('/')._asdict(),
        "load_avg": os.getloadavg(),
        "uptime": int(psutil.boot_time()),
        "logged_in_users": [user._asdict() for user in psutil.users()],
        "processes": [
            {
                "pid": proc.pid,
                "name": proc.name(),
                "cpu_percent": proc.cpu_percent(interval=0.1),
                "memory_percent": proc.memory_percent(),
                "status": proc.status(),
            }
            for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent", "status"])
        ],
    }
    stats["process_summary"] = {
        "total": len(stats["processes"]),
        "by_state": {
            state: sum(1 for proc in stats["processes"] if proc["status"] == state)
            for state in set(proc["status"] for proc in stats["processes"])
        },
    }
    stats["system_logs"] = get_system_logs(50)
    stats["last_logged_users"] = get_last_logged_users(10)
    return web.json_response(stats)

def get_system_logs(lines):
    try:
        with open('/var/log/syslog', 'r') as f:
            return f.readlines()[-lines:]
    except FileNotFoundError:
        return []

def get_last_logged_users(count):
    try:
        with open('/var/log/wtmp', 'rb') as f:
            return f"Last {count} logged users data."  # Implement detailed parsing as needed
    except FileNotFoundError:
        return []

async def handle_index(request):
    return web.FileResponse('./static/index.html')

async def start_server():
    app = web.Application()
    app.router.add_get('/stats', handle_stats)
    app.router.add_get('/', handle_index)
    return app

if __name__ == "__main__":
    web.run_app(start_server(), host="0.0.0.0", port=8765)