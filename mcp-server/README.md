# KSHAN Multiverse Context Server (MCP)

Official Model Context Protocol (MCP) Server for **KSHAN: "One Moment. Infinite Lives. Your choices create worlds that never existed."**

## Overview
The KSHAN MCP server provides structured, user-authenticated, and tenant-isolated tool and resource access to multiverse timelines, realm locations, character dossiers, memories, decisions, and narrative context grounded by pgvector RAG.

## Transport
- **Streamable HTTP**: `http://localhost:8001/mcp`
- **Supported Transports**: Streamable HTTP (production & remote), In-memory (isolated deterministic tests).

## Registered Tools
1. `get_current_world` (read): World lore, cosmos physics, and factions.
2. `get_timeline` (read): Ordered sequence of timeline nodes for an authenticated branch.
3. `get_timeline_node` (read): Detailed narrative node, choices, and consequences.
4. `get_character` (read): Character profile, psychological stance, and dialogue style.
5. `get_location` (read): Realm zone description and danger ratings.
6. `search_memories` (read / RAG): Semantic vector retrieval across memories and reflections.
7. `get_recent_decisions` (read): Turning points and chosen actions for a branch.
8. `get_branch_state` (read): Entropy, resonance score, and multiverse state variables.
9. `get_world_events` (read): Chronological history of events in a reality branch.
10. `get_story_context` (read / composite): Complete context aggregator combining active world, branch state, recent decisions, and pgvector RAG chunks.
11. `create_memory` (write): Inserts a memory into PostgreSQL and automatically indexes into pgvector.
12. `create_timeline_event` (write): Inserts a timeline event and indexes into pgvector.

## Resources
- `kshan://world/{scenario_id}`: World chronicle and realm topology.
- `kshan://timeline/{branch_id}`: Full narrative chronicle for a branch.
- `kshan://memories/{branch_id}`: Unlocked memory vault.

## Prompts
- `future_you_context`: Grounding prompt for interacting with the traveler's alternate self.

## Running Locally
```bash
uvicorn mcp_server.app.server:app --host 0.0.0.0 --port 8001 --reload
```

## Inspecting with MCP Inspector
```bash
npx @modelcontextprotocol/inspector http://localhost:8001/mcp
```
