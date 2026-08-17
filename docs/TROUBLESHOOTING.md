# KSHAN — Production Troubleshooting & Incident Playbook

## 1. Database Connectivity & pgvector Issues

### Symptoms
- Backend startup fails with `ConnectionRefusedError` or `UndefinedObjectError: type "vector" does not exist`.
- Readiness probe `GET /api/v1/health/ready` returns HTTP 503.

### Resolution Steps
1. Verify PostgreSQL is running:
   ```bash
   docker compose ps db
   ```
2. Ensure the `vector` extension is enabled in PostgreSQL:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Check `DATABASE_URL` format. Ensure `postgresql+asyncpg://` is used for async FastAPI connections.

---

## 2. Gemini Generative AI Service Disruption

### Symptoms
- Log messages indicating `Gemini API key missing or invalid`.
- `/api/v1/ai/*` returns mock fallback narrative.

### Resolution Steps
1. Verify `GEMINI_API_KEY` is exported in the environment.
2. Confirm the Gemini model configured through `GEMINI_MODEL` is accessible (e.g. `gemini-2.5-flash` or `gemini-1.5-pro`).
3. Note: KSHAN is architected with a **Deterministic Mock Fallback**—if no API key is provided, the platform automatically produces deterministic narratives so game mechanics remain 100% playable.

---

## 3. Model Context Protocol (MCP) Service Unreachable

### Symptoms
- Readiness probe logs `MCP Server connection warning`.

### Resolution Steps
1. Check if the standalone MCP microservice is active on port 8001:
   ```bash
   curl http://localhost:8001/mcp
   ```
2. Verify `MCP_SERVER_URL` in `.env` matches the deployed hostname (`http://mcp-server:8001/mcp` inside Docker networks).

---

## 4. CORS & Cross-Origin Rejections

### Symptoms
- Browser console error: `Access to XMLHttpRequest has been blocked by CORS policy`.

### Resolution Steps
1. In production, ensure the frontend domain is listed in `BACKEND_CORS_ORIGINS`.
2. Example `.env`:
   ```bash
   BACKEND_CORS_ORIGINS=https://kshan.ai,https://www.kshan.ai,http://localhost:3000
   ```
3. Restart the backend service to apply updated origin settings.

---

## 5. Database Schema & Migration Drift

### Symptoms
- Query errors: `column reality_branches.regret_index does not exist`.

### Resolution Steps
1. Apply the latest Alembic migrations:
   ```bash
   alembic upgrade head
   ```
2. Verify migration head matches repository schema:
   ```bash
   alembic current
   ```
