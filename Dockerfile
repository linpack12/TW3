FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libcups2 \
    fonts-liberation \
    fonts-unifont \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium

COPY src /app/src
COPY artifacts /app/artifacts
COPY demo.py /app/demo.py
COPY demo_part_2.py /app/demo_part_2.py
COPY run_local_server.py /app/run_local_server.py
COPY page1.html /app/page1.html
COPY page2.html /app/page2.html
COPY start.sh /app/start.sh

RUN mkdir -p /app/artifacts/screenshots
RUN mkdir -p /app/artifacts/html_dumps
RUN mkdir -p /app/artifacts/json_dumps

RUN chmod +x /app/start.sh

EXPOSE 8000 8888

ENTRYPOINT ["/app/start.sh"]
CMD []
