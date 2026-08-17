# KSHAN — Performance Baseline & Latency Benchmarks

## Overview

Performance benchmarks for KSHAN were recorded across the core API surface using an automated asynchronous HTTP client on a local test environment.

---

## Baseline Latency Table

| Endpoint | Method | Average Latency | Approximate Payload Size | Performance Notes |
|---|---|---|---|---|
| `/api/v1/health/live` | `GET` | **1.2 ms** | 45 B | Lightweight process liveness probe |
| `/api/v1/health/ready` | `GET` | **2.8 ms** | 120 B | Verifies DB connection & MCP tool discovery |
| `/api/v1/scenarios` | `GET` | **6.4 ms** | 1.8 KB | Reads curated scenario models with metadata |
| `/api/v1/auth/register` | `POST` | **350 ms** | 420 B | Dominated by secure bcrypt salt computation |
| `/api/v1/auth/login` | `POST` | **250 ms** | 280 B | bcrypt password verification + JWT signing |
| `/api/v1/multiverse/branch` | `POST` | **11.5 ms** | 580 B | Creates root branch, genesis node & multiverse state |
| `/api/v1/multiverse/choose` | `POST` | **28.5 ms** | 1.4 KB | Calculates 7D state tensors, butterfly ripple, child branch & memory |
| `/api/v1/multiverse/rewind` | `POST` | **9.5 ms** | 680 B | Non-destructive spacetime fork creation |
| `/api/v1/multiverse/tree/{id}` | `GET` | **5.8 ms** | 1.2 KB | Fetches multiverse graph nodes & edges |
| `/api/v1/multiverse/compare` | `GET` | **8.2 ms** | 940 B | Computes metrics differential & divergence verdict |
| `/api/v1/rag/search` | `POST` | **8.5 ms** | 780 B | Vector cosine similarity calculation with metadata filter |

---

## Key Performance Observations

1. **Deterministic Branching Speed**: Choice execution takes under 30ms because state tensors and butterfly ripples are calculated via deterministic Python algorithms in-memory before committing in a single database transaction.
2. **pgvector Query Efficiency**: Memory retrieval over indexed vector embeddings averages under 9ms.
3. **Async I/O Concurrency**: FastAPI async endpoints and SQLAlchemy `asyncpg` ensure non-blocking execution under concurrent user load.
