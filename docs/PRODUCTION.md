# KSHAN — Production Operations, Observability & Security Runbook

## 1. Observability & Telemetry

### Request Identification & Latency
Every incoming HTTP request is assigned a unique `X-Request-ID` (UUIDv4) injected by `RequestObservabilityMiddleware`. 

The response headers include:
- `X-Request-ID`: Trace identifier propagating through all downstream logs.
- `X-Process-Time-Ms`: Server execution latency in milliseconds.

### Log Sanitation Rules
The logging engine enforces strict privacy rules:
- **Never Logged**: Passwords, plaintext JWTs, authorization bearer headers, or Gemini API keys.
- **Structured Fields**: `request_id`, `duration_ms`, `status_code`, `path`, `method`.

---

## 2. Standardized Error Handling

All API errors return a uniform, machine-readable envelope without leaking stack traces or internal implementation details:

```json
{
  "error": {
    "code": "HTTP_404",
    "message": "Reality branch was not found or is outside your multiverse cluster.",
    "request_id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
  }
}
```

---

## 3. Rate Limiting & Abuse Prevention Strategy

To protect computationally expensive LLM inference, embedding projections, and multiverse branch graph traversals:

| Endpoint Pattern | Rate Limit | Protection Mechanism |
|---|---|---|
| `/api/v1/ai/*` | 30 requests / min | In-memory token bucket + IP/User keying |
| `/api/v1/rag/search` | 60 requests / min | Vector query cache & budget governor |
| `/api/v1/multiverse/choose` | 45 requests / min | Deterministic state debounce |
| `/api/v1/health/*` | Unlimited | Excluded from rate limits for load balancer probes |

---

## 4. Database Backup & Disaster Recovery

### Automated Backup Strategy
- **Daily Full Snapshot**: Executed via cloud database provider (e.g. Supabase / AWS RDS automated daily snapshots retained for 30 days).
- **Point-in-Time Recovery (PITR)**: Write-Ahead Logs (WAL) archived continuously to enable recovery to any second within the retention window.

### Manual Backup (pg_dump)
```bash
pg_dump -h <host> -U <user> -d kshan_db -F c -b -v -f kshan_backup_$(date +%Y%m%d_%H%M%S).dump
```

### Manual Restore (pg_restore)
```bash
pg_restore -h <host> -U <user> -d kshan_db -v -c kshan_backup_20260817.dump
```

### Zero-Downtime Migration Policy
- Always run schema additions as backwards-compatible migrations.
- Execute `alembic upgrade head` before releasing new container images.
- Never drop columns or rename active tables in the same deployment phase as code changes.
