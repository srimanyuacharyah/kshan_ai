# KSHAN — Production Security Audit & Threat Modeling

## Executive Summary

A comprehensive production security audit of **KSHAN** was conducted across the application, database, MCP microservice, container layer, and CI/CD pipelines.

The platform employs a **defense-in-depth architecture** with strict tenant isolation, immutable relational structures, non-root containers, and zero frontend secret leakage.

---

## Threat Matrix & Security Controls

| Category | Potential Threat | KSHAN Security Control | Classification |
|---|---|---|---|
| **Authentication** | Credential Stuffing / Rainbow Tables | Passwords hashed using standard `bcrypt` with unique salts. Minimum length validated. | Verified Secure (LOW) |
| **Session Security** | Token Hijacking / Replay | Ephemeral JWT Bearer tokens with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`). | Verified Secure (LOW) |
| **Data Isolation** | Cross-Tenant Reality Bleed | Every query enforces `user_id == current_user.id` at the ORM layer and pgvector query filter. | Verified Secure (CRITICAL Control) |
| **SQL Injection** | SQL Injection in Tensors/Branches | 100% parameterized queries via SQLAlchemy 2.0 async engine. Zero raw string interpolation. | Verified Secure (CRITICAL Control) |
| **AI Vector Security** | Vector RAG Data Leakage | Cosine similarity searches require explicit `user_id` metadata filtering before computing vector distances. | Verified Secure (HIGH Control) |
| **MCP Microservice** | Unauthorized Tool Execution | MCP client validates tenant identity before dispatching tool operations over Streamable HTTP. | Verified Secure (HIGH Control) |
| **Browser Security** | Secret Exposure in Bundles | `GEMINI_API_KEY`, `JWT_SECRET`, and `DATABASE_URL` are strictly server-side. Frontend only receives public `VITE_API_URL`. | Verified Secure (CRITICAL Control) |
| **Error Leakage** | Stack Trace Disclosure | Custom exception handlers trap unhandled 500s and return a sanitized JSON error envelope with `request_id`. | Verified Secure (MEDIUM Control) |
| **Container Security** | Privilege Escalation | Dockerfiles execute under dedicated non-root users (`appuser` UID 10001, `mcpuser` UID 10002). | Verified Secure (MEDIUM Control) |
| **CORS Policy** | Unauthorized Cross-Origin Exploits | Wildcards (`*`) are disallowed when credentials are enabled. Allowed origins configured via `BACKEND_CORS_ORIGINS`. | Verified Secure (MEDIUM Control) |

---

## Detailed Findings & Classification

### 1. Zero Secret Leakage Verification
- **Status**: PASSED (Verified via CI Security Audit job).
- **Detail**: Static scanning confirmed zero unencrypted API keys or `.env` files are tracked in version control. `.gitignore` strictly ignores `.env*` while preserving `.env.example`.

### 2. Multi-Tenant Branch Isolation
- **Status**: PASSED (Automated test: `backend/tests/test_e2e_multiverse.py::STEP 28`).
- **Detail**: Attempting to read or execute choices on another user's reality branch returns HTTP 400/403/404, preventing cross-tenant information disclosure.

### 3. Rate Limiting on Generative AI Endpoints
- **Status**: IMPLEMENTED & DOCUMENTED.
- **Detail**: Rate limits are placed on expensive AI generation (`/api/v1/ai/*`) and RAG vector searches (`/api/v1/rag/*`) to prevent resource exhaustion and cost spikes.

---

## Security Best Practices for Operators

1. **Rotate Secrets Regularly**: Use cloud secrets managers (AWS Secrets Manager, Doppler, or GitHub Secrets) to inject `JWT_SECRET_KEY` and `GEMINI_API_KEY`.
2. **Enable TLS 1.3**: Terminate HTTPS at the reverse proxy / Cloudflare edge.
3. **Database Network Isolation**: Ensure PostgreSQL is only accessible via internal VPC networks or SSL-enforced connection pooling.
