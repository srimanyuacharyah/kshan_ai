from typing import List, Dict, Set
from backend.app.services.rag.vector_store import VectorSearchResult

class ContextBuilder:
    """
    Synthesizes retrieved RAG chunks into clean, categorized, token-efficient context
    for the AI Orchestrator while preventing duplication and prompt overflow.
    """
    def __init__(self, max_context_chars: int = 4000):
        self.max_context_chars = max_context_chars

    def build_grounded_context(self, search_results: List[VectorSearchResult]) -> str:
        if not search_results:
            return "No prior multiverse memories or world records matched this query."

        # Category buckets
        categories: Dict[str, List[str]] = {
            "timeline_node": [],
            "memory": [],
            "decision": [],
            "character": [],
            "world": [],
            "location": [],
            "scenario": [],
            "future_profile": [],
            "other": []
        }

        seen_entities: Set[str] = set()
        total_chars = 0

        for r in search_results:
            # Deduplicate same entity chunks if content is mostly identical
            entity_key = f"{r.entity_type}:{r.entity_id}"
            if entity_key in seen_entities and r.score < 0.85:
                continue
            seen_entities.add(entity_key)

            snippet = r.document_content.strip()
            if total_chars + len(snippet) > self.max_context_chars:
                # Truncate if nearing budget
                remaining = self.max_context_chars - total_chars
                if remaining > 100:
                    snippet = snippet[:remaining] + "... [truncated]"
                else:
                    break

            cat = r.entity_type if r.entity_type in categories else "other"
            categories[cat].append(f"(Relevance: {int(r.score * 100)}%) {snippet}")
            total_chars += len(snippet)

        sections: List[str] = ["=== RETRIEVED KSHAN MULTIVERSE CONTEXT ==="]

        type_headers = [
            ("timeline_node", "CHRONICLES & TIMELINE EVENTS"),
            ("decision", "PAST CHOICES & TURNING POINTS"),
            ("memory", "MEMORIES & PARALLEL ECHOES"),
            ("character", "CHARACTERS & AFFINITIES"),
            ("world", "WORLD COSMOLOGY & RULES"),
            ("location", "KEY REALM LOCATIONS"),
            ("future_profile", "DESTINY & ARCHETYPES"),
            ("scenario", "ORIGIN SEED KSHAN"),
            ("other", "ADDITIONAL CONTEXT")
        ]

        for type_key, header in type_headers:
            items = categories.get(type_key, [])
            if items:
                sections.append(f"\n[{header}]")
                for item in items:
                    sections.append(f"• {item}")

        return "\n".join(sections)

context_builder = ContextBuilder()
