# Lightweight Dockerfile for KSHAN Model Context Protocol (MCP) Server
FROM python:3.12-slim

WORKDIR /app

# Install dependencies and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 10002 mcpgroup && \
    useradd -u 10002 -g mcpgroup -s /bin/bash -m mcpuser

# Install requirements
COPY mcp-server/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY --chown=mcpuser:mcpgroup mcp-server/ /app/mcp-server/

USER mcpuser

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8001/mcp || exit 1

CMD ["python", "-m", "mcp_server.app.server", "--port", "8001"]
