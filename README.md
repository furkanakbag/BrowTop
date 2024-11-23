# browtop - a Browser-based System Performance Monitor
browtop is an interactive graphical system performance monitor.

## How to run browtop
First, you need to install the required Python packages.

```bash
pip3 install -r requirements.txt
```

Then, you can run the browtop server by running the following command.

```bash
python3 websocket_server.py
```

In order to view the monitor, you need to run a webserver. You can use Python's built-in HTTP server for this purpose.

```bash
python3 -m http.server
```

Then, you can open the browtop monitor by visiting `http://localhost:8000/monitor.html` in your web browser.


# How to create local SSL certificate
```bash
mkcert -install
mkcert -key-file cert/localhost.key -cert-file cert/localhost.crt localhost
```

Installation instructions for mkcert can be found at [here](https://github.com/FiloSottile/mkcert).
