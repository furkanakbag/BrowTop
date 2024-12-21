import asyncio
import json
import os
import psutil
from aiohttp import web


PASSWORD = "Furkanarda2752"

async def handle_stats(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {PASSWORD}":
        return web.Response(status=401, text="Unauthorized")

    try:
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
                if proc.info.get("name")
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
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

def get_system_logs(lines):
    try:
        with open('/var/log/syslog', 'r') as f:
            return f.readlines()[-lines:]
    except FileNotFoundError:
        return []

def get_last_logged_users(count):
    try:
        return "Last logged users data parsing not implemented."
    except FileNotFoundError:
        return []

async def handle_index(request):
    return web.FileResponse('./static/monitor.html')

async def start_server():
    app = web.Application()
    app.router.add_get('/stats', handle_stats)
    app.router.add_get('/', handle_index)
    return app

if __name__ == "__main__":
    web.run_app(start_server(), host="0.0.0.0", port=8765)
