FROM python:3.9-slim

WORKDIR /app

COPY . /app

# Install dependencies for mkcert
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libnss3-tools \
 && rm -rf /var/lib/apt/lists/*

# Download and install mkcert binary
RUN curl -L -o /usr/local/bin/mkcert https://github.com/FiloSottile/mkcert/releases/latest/download/mkcert-v1.4.4-linux-amd64 \
 && chmod +x /usr/local/bin/mkcert

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Setup mkcert
RUN mkcert -install \
 && mkdir -p cert \
 && mkcert -key-file cert/localhost.key -cert-file cert/localhost.crt localhost

EXPOSE 8765

CMD ["python3", "src/server.py"]