FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -r requirements.txt

RUN mkdir -p /app/cert && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /app/cert/localhost.key -out /app/cert/localhost.crt \
    -subj "/CN=localhost"

EXPOSE 8765

CMD ["python", "src/server.py"]
