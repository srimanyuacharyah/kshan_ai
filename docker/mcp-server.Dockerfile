FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY mcp-server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app/backend
COPY mcp-server /app/mcp_server

ENV PYTHONPATH=/app
ENV PORT=8001
ENV HOST=0.0.0.0

EXPOSE 8001

CMD ["uvicorn", "mcp_server.app.server:app", "--host", "0.0.0.0", "--port", "8001"]
