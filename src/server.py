import asyncio
import json
import pathlib
import ssl
from aiohttp import web

SECURE_PASSWORD = "secure_password"
LOGINS_DB = pathlib.Path(__file__).parent.joinpath("logins.json")

def save_login(username):
    """Save the login username."""
    logins = []
    if LOGINS_DB.exists():
        with open(LOGINS_DB, "r") as file:
            logins = json.load(file)

    logins.insert(0, {"username": username})
    logins = logins[:10]
    with open(LOGINS_DB, "w") as file:
        json.dump(logins, file)

async def monitor(request):
    """Serve the monitor.html file."""
    html_path = pathlib.Path(__file__).parent.joinpath("monitor.html")
    return web.FileResponse(html_path)

async def login(request):
    """Authenticate the user."""
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if password == SECURE_PASSWORD:
        save_login(username)
        return web.json_response({"status": "success"})
    return web.json_response({"status": "failure"})

def create_ssl_context():
    """Set up SSL context."""
    cert_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.crt")
    key_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.key")
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(cert_file, key_file)
    return ssl_context

def run():
    ssl_context = create_ssl_context()
    app = web.Application()
    app.add_routes([
        web.get("/monitor", monitor),
        web.post("/login", login),
    ])
    web.run_app(app, port=8765, ssl_context=ssl_context)

if __name__ == "__main__":
    run()
