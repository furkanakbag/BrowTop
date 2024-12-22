import asyncio
import json
import pathlib
import ssl
import psutil
import time
from aiohttp import web

# Sabit şifre
SECURE_PASSWORD = "secure_password"

# Login log dosyası
LOGINS_DB = pathlib.Path(__file__).parent.joinpath("logins.json")


def save_login(username):
    """Giriş yapan kullanıcıyı kaydet."""
    logins = []
    if LOGINS_DB.exists():
        with open(LOGINS_DB, "r") as file:
            logins = json.load(file)

    logins.insert(0, {"username": username, "timestamp": time.time()})
    logins = logins[:10]  # Son 10 kullanıcıyla sınırla
    with open(LOGINS_DB, "w") as file:
        json.dump(logins, file)


def load_logins():
    """Son giriş yapan 10 kullanıcıyı yükle."""
    if LOGINS_DB.exists():
        with open(LOGINS_DB, "r") as file:
            return json.load(file)
    return []


async def login_page(request):
    """Giriş ekranını göster."""
    path = pathlib.Path(__file__).parent.joinpath("login.html")
    if not path.exists():
        return web.Response(status=404, text="Login page not found.")
    return web.FileResponse(path)


async def login(request):
    """Kullanıcı giriş işlemi."""
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if password == SECURE_PASSWORD:
        save_login(username)
        response = web.json_response({"status": "success", "message": "Login successful"})
        response.set_cookie("logged_in", "true", max_age=3600)  # 1 saat geçerli oturum
        return response
    return web.json_response({"status": "failure", "message": "Invalid password"}, status=401)


async def monitor(request):
    """Monitor sayfasını yükle."""
    logged_in = request.cookies.get("logged_in")
    if not logged_in or logged_in != "true":
        return web.HTTPFound("/login")  # Giriş ekranına yönlendir

    path = pathlib.Path(__file__).parent.joinpath("monitor.html")
    if not path.exists():
        return web.Response(status=404, text="Monitor file not found.")
    return web.FileResponse(path)


async def send_stats(request):
    """WebSocket üzerinden istatistik gönder."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    try:
        while True:
            stats = {
                "cpu": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage("/")._asdict(),
                "logged_users": load_logins(),
            }
            await ws.send_json(stats)
            await asyncio.sleep(2)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("WebSocket bağlantısı kapatıldı.")
    return ws


def create_ssl_context():
    """SSL bağlamını oluştur."""
    cert_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.crt")
    key_file = pathlib.Path(__file__).parents[1].joinpath("cert/localhost.key")
    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_file, key_file)
        return ssl_context
    except Exception as e:
        print(f"SSL sertifikaları yüklenemedi: {e}")
        raise


def run():
    """Sunucuyu başlat."""
    ssl_context = create_ssl_context()
    app = web.Application()
    app.add_routes(
        [
            web.get("/login", login_page),
            web.post("/login", login),
            web.get("/monitor", monitor),
            web.get("/ws", send_stats),
        ]
    )
    print("Sunucu çalışıyor: https://localhost:8765")
    web.run_app(app, port=8765, ssl_context=ssl_context)


if __name__ == "__main__":
    print("Sunucu başlatılıyor...")
    run()
