import json
from typing import Dict, Any, List, Optional
from backend.app.models.timeline import TimelineNode, Decision, Choice
from backend.app.models.world import World, Character, Location
from backend.app.models.memory import Memory
from backend.app.models.scenario import Scenario
from backend.app.services.rag.chunker import chunker, TextChunk

class ProcessedDocument:
    def __init__(
        self,
        document_id: str,
        user_id: str,
        entity_type: str,
        entity_id: str,
        title: str,
        searchable_text: str,
        metadata: Dict[str, Any],
        scenario_id: Optional[str] = None,
        branch_id: Optional[str] = None
    ):
        self.document_id = document_id
        self.user_id = user_id
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.title = title
        self.searchable_text = searchable_text
        self.metadata = metadata
        self.scenario_id = scenario_id
        self.branch_id = branch_id
        self.chunks: List[TextChunk] = chunker.chunk_document(searchable_text, metadata)

class DocumentProcessor:
    """
    Transforms rich relational KSHAN entities into structured, searchable textual documents
    with dense metadata for vector embedding and retrieval.
    """

    def process_timeline_node(self, node: TimelineNode, user_id: str) -> ProcessedDocument:
        choices_text = []
        try:
            if "choices" in node.__dict__ and node.choices:
                for c in node.choices:
                    choices_text.append(f"Option: {c.choice_label} - {c.choice_description}")
        except Exception:
            pass

        choices_block = ("\nChoices:\n" + "\n".join(f"- {c}" for c in choices_text)) if choices_text else ""
        sensory_block = f"\nSensory ambiance: {node.sensory_cue}" if node.sensory_cue else ""
        impact_block = f"\nButterfly effect impact: {node.butterfly_impact}" if node.butterfly_impact else ""

        full_text = (
            f"Timeline Era: {node.era_year} (Depth Level {node.depth_level})\n"
            f"Narrative: {node.story_text}"
            f"{sensory_block}"
            f"{impact_block}"
            f"{choices_block}"
        )

        return ProcessedDocument(
            document_id=f"doc_node_{node.id}",
            user_id=user_id,
            entity_type="timeline_node",
            entity_id=node.id,
            title=f"Timeline Event [{node.era_year}]",
            searchable_text=full_text,
            metadata={
                "depth_level": node.depth_level,
                "era_year": node.era_year,
                "audio_ambiance": node.audio_ambiance,
                "has_butterfly_impact": bool(node.butterfly_impact)
            },
            branch_id=node.branch_id
        )

    def process_memory(self, memory: Memory, user_id: str) -> ProcessedDocument:
        full_text = (
            f"Memory Shard: {memory.title}\n"
            f"Type: {memory.memory_type.upper()} | Emotional Tone: {memory.emotional_tone.upper()}\n"
            f"Clarity Level: {memory.clarity_level}\n"
            f"Content: {memory.content}"
        )

        return ProcessedDocument(
            document_id=f"doc_memory_{memory.id}",
            user_id=user_id,
            entity_type="memory",
            entity_id=memory.id,
            title=f"Memory: {memory.title}",
            searchable_text=full_text,
            metadata={
                "memory_type": memory.memory_type,
                "emotional_tone": memory.emotional_tone,
                "clarity_level": memory.clarity_level,
                "node_id": memory.node_id
            },
            branch_id=memory.branch_id
        )

    def process_character(self, character: Character, user_id: str, scenario_id: Optional[str] = None) -> ProcessedDocument:
        full_text = (
            f"Character: {character.name}\n"
            f"Role: {character.role} | Faction: {character.faction or 'Independent'}\n"
            f"Backstory: {character.backstory}\n"
            f"Psychological Profile: {character.psychological_profile}\n"
            f"Dialogue Style: {character.dialogue_style}"
        )

        return ProcessedDocument(
            document_id=f"doc_character_{character.id}",
            user_id=user_id,
            entity_type="character",
            entity_id=character.id,
            title=f"Dossier: {character.name}",
            searchable_text=full_text,
            metadata={
                "character_name": character.name,
                "role": character.role,
                "faction": character.faction,
                "world_id": character.world_id
            },
            scenario_id=scenario_id
        )

    def process_location(self, location: Location, user_id: str, scenario_id: Optional[str] = None) -> ProcessedDocument:
        full_text = (
            f"Realm Location: {location.name}\n"
            f"Zone: {location.realm_zone} | Danger Rating: {location.danger_rating}\n"
            f"Atmosphere: {location.atmosphere}\n"
            f"Description: {location.description}"
        )

        return ProcessedDocument(
            document_id=f"doc_location_{location.id}",
            user_id=user_id,
            entity_type="location",
            entity_id=location.id,
            title=f"Location: {location.name}",
            searchable_text=full_text,
            metadata={
                "location_name": location.name,
                "realm_zone": location.realm_zone,
                "danger_rating": location.danger_rating,
                "world_id": location.world_id
            },
            scenario_id=scenario_id
        )

    def process_world(self, world: World, user_id: str, scenario_id: Optional[str] = None) -> ProcessedDocument:
        full_text = (
            f"World Lore: {world.name} ({world.cosmos_type})\n"
            f"Laws of Physics: {world.laws_of_physics or 'Standard Multiverse Laws'}\n"
            f"Factions: {world.factions_overview}\n"
            f"Chronicle: {world.lore_chronicle}"
        )

        return ProcessedDocument(
            document_id=f"doc_world_{world.id}",
            user_id=user_id,
            entity_type="world",
            entity_id=world.id,
            title=f"World Lore: {world.name}",
            searchable_text=full_text,
            metadata={
                "world_name": world.name,
                "cosmos_type": world.cosmos_type,
                "scenario_id": world.scenario_id
            },
            scenario_id=scenario_id or world.scenario_id
        )

    def process_decision(self, decision: Decision, user_id: str, choice: Optional[Choice] = None, branch_id: Optional[str] = None) -> ProcessedDocument:
        chosen = choice or getattr(decision, "chosen_choice", None)
        action_label = chosen.choice_label if chosen else "Custom Path"
        full_text = (
            f"Pivotal Decision Taken\n"
            f"Action Chosen: {action_label}\n"
            f"Rationale / Philosophy: {decision.rationale or 'Intuitive Leap'}\n"
            f"Divergence Magnitude: {decision.divergence_magnitude}"
        )

        return ProcessedDocument(
            document_id=f"doc_decision_{decision.id}",
            user_id=user_id,
            entity_type="decision",
            entity_id=decision.id,
            title="Decision Point",
            searchable_text=full_text,
            metadata={
                "node_id": decision.node_id,
                "chosen_choice_id": decision.chosen_choice_id,
                "divergence_magnitude": decision.divergence_magnitude
            },
            branch_id=branch_id
        )

document_processor = DocumentProcessor()
