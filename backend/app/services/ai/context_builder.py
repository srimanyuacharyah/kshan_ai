from typing import List, Dict, Any, Optional
from backend.app.services.ai.schemas import ContextSource
from backend.app.core.logging import logger

class ContextBudgetManager:
    """
    Manages context token/character budget for Gemini prompts.
    Performs source prioritization, deduplication, and truncation to prevent context blowup.
    
    Priority Hierarchy:
    1. Current Branch & Multiverse State
    2. Current World Lore & Physics
    3. Recent Turning Points / Decisions
    4. Grounded Memory Shards (RAG)
    5. Relevant Characters & Locations
    6. Historical Narrative Context
    """

    def __init__(self, max_context_chars: int = 8000, max_rag_chunks: int = 4):
        self.max_context_chars = max_context_chars
        self.max_rag_chunks = max_rag_chunks

    def assemble_budgeted_context(
        self,
        branch_state: Dict[str, Any],
        world_data: Optional[Dict[str, Any]] = None,
        recent_decisions: Optional[List[Dict[str, Any]]] = None,
        rag_memories: Optional[List[Dict[str, Any]]] = None,
        characters: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        sources: List[ContextSource] = []
        assembled_blocks: List[str] = []
        total_chars = 0

        # 1. Branch State (Priority 1)
        branch_summary = (
            f"Branch: {branch_state.get('branch_name', 'Prime')} ({branch_state.get('branch_code', 'TL-01')}) | "
            f"Entropy: {branch_state.get('entropy', 0.2)} | Resonance: {branch_state.get('resonance', 0.8)} | "
            f"Regret: {branch_state.get('regret', 0.0)}"
        )
        assembled_blocks.append(f"### Reality Branch State:\n{branch_summary}")
        total_chars += len(branch_summary)

        # 2. World Lore (Priority 2)
        if world_data and "name" in world_data:
            world_text = f"World: {world_data['name']} ({world_data.get('cosmos_type', 'Cosmos')})\nLaws: {world_data.get('laws_of_physics', 'Standard')}\nLore: {world_data.get('lore_chronicle', '')[:400]}"
            assembled_blocks.append(f"### World Cosmology:\n{world_text}")
            total_chars += len(world_text)
            sources.append(ContextSource(source_type="mcp_world", title=world_data["name"], snippet=world_text[:120]))

        # 3. Recent Decisions (Priority 3)
        if recent_decisions:
            dec_lines = []
            for d in recent_decisions[:3]:
                line = f"- {d.get('chosen_action', 'Pivotal Choice')}: {d.get('rationale', '')[:100]}"
                dec_lines.append(line)
            dec_block = "\n".join(dec_lines)
            assembled_blocks.append(f"### Recent Turning Points:\n{dec_block}")
            total_chars += len(dec_block)
            sources.append(ContextSource(source_type="mcp_decision", title="Recent Turning Points", snippet=dec_block[:120]))

        # 4. RAG Memory Shards (Priority 4)
        if rag_memories:
            mem_lines = []
            seen_titles = set()
            for m in rag_memories[:self.max_rag_chunks]:
                title = m.get("title", "Memory Shard")
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                content = m.get("content", "")[:350]
                if total_chars + len(content) <= self.max_context_chars:
                    mem_lines.append(f"[{title}]: {content}")
                    total_chars += len(content)
                    sources.append(ContextSource(source_type="rag_memory", title=title, snippet=content[:100]))
            
            if mem_lines:
                assembled_blocks.append(f"### Unlocked Memory Shards (RAG):\n" + "\n\n".join(mem_lines))

        # 5. Characters (Priority 5)
        if characters and total_chars < self.max_context_chars:
            char_lines = []
            for c in characters[:2]:
                c_text = f"- {c.get('name', 'Figure')} ({c.get('role', 'NPC')}): {c.get('backstory', '')[:150]}"
                if total_chars + len(c_text) <= self.max_context_chars:
                    char_lines.append(c_text)
                    total_chars += len(c_text)
            if char_lines:
                assembled_blocks.append("### Key Figures:\n" + "\n".join(char_lines))

        final_grounded_text = "\n\n".join(assembled_blocks)
        logger.info(f"Assembled budgeted context of {len(final_grounded_text)} chars from {len(sources)} sources.")

        return {
            "grounded_text": final_grounded_text,
            "sources": sources,
            "total_chars": len(final_grounded_text)
        }

context_budget_manager = ContextBudgetManager()
