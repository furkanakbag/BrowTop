# BrowTop - a Browser-based System Performance Monitor
BrowTop is an interactive graphical system performance monitor.

## How to run BrowTop
1. Install the dependencies

First, you need to install the required Python packages.

```bash
pip3 install -r requirements.txt
```

2. Create a locally-trusted TLS certificate

You can create locally-trusted TLS certificates by running the following command.

```bash
mkcert -install
mkcert -key-file cert/localhost.key -cert-file cert/localhost.crt localhost
```

Installation instructions for mkcert can be found at [here](https://github.com/FiloSottile/mkcert).

3. Run the BrowTop server 

You can run the BrowTop server by running the following command.

```bash
python3 src/server.py
```

This command will start the browtop server on `https://localhost:8765`. 

Afterwards, you can open the browtop monitor by visiting `http://localhost:8765/monitor` in your web browser.


