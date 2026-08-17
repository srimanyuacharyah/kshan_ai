import json
import uuid
from typing import Dict, Any, Type, TypeVar, Optional
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.services.ai.exceptions import GeminiAPIError, ResponseValidationError

T = TypeVar("T", bound=BaseModel)

class MockGeminiProvider:
    """
    Deterministic mock provider for unit tests and keyless DEMO_MODE.
    Returns structurally valid, richly thematic KSHAN multiverse JSON payloads.
    """

    def generate_story(self, prompt: str, gen_id: str) -> Dict[str, Any]:
        return {
            "generation_id": gen_id,
            "narrative": "A low electrostatic hum vibrates through the damp stone stairs of Platform 108. The glowing cyan memory crystal pulses in rhythm with your neural implant, casting long, fractured shadows across the subterranean ghats. A voice echoes from the darkness—Aria stands by the water's edge, watching the river of forgotten code ripple into infinity.",
            "atmosphere": "Dystopian cyberpunk blended with ancient mystic reverie; humid ozone mist and neon lanterns.",
            "sensory_details": "Smell of burning sandalwood and ionized mist; auditory drone of magnetic lev-trains echoing through ancient arches.",
            "current_reality_state": {"timeline_era": "Year 2042", "entropy": 0.25, "resonance": 0.82},
            "choices": [
                {
                    "id": "choice_a",
                    "title": "Submerge the crystal into the sacred cyber-waters",
                    "description": "Release the pre-divergence memory into the river network to cleanse the city's corrupt neural matrix.",
                    "immediate_effect": "A brilliant cascade of luminescent blue light surges through the water grid.",
                    "long_term_consequence": "Awakens dormant AI deities sleeping beneath the riverbed.",
                    "risk": 0.65,
                    "resonance": 0.85,
                    "entropy_delta": 0.15
                },
                {
                    "id": "choice_b",
                    "title": "Directly interface neural link with the core memory shard",
                    "description": "Absorb the raw consciousness of the traveler who came before you.",
                    "immediate_effect": "Blinding epiphanies flood your mind; sensory overload for 10 seconds.",
                    "long_term_consequence": "Permanently alters your core personality and reveals hidden access codes to the Citadel.",
                    "risk": 0.45,
                    "resonance": 0.70,
                    "entropy_delta": 0.08
                },
                {
                    "id": "choice_c",
                    "title": "Hand the artifact over to Aria and retreat to the Upper City",
                    "description": "Refuse the burden of the memory shard and let the Undercity Guild dictate its destiny.",
                    "immediate_effect": "Aria secures the crystal in a lead-lined casing and vanishes into the steam.",
                    "long_term_consequence": "You survive unscathed, but the memory remains locked away forever.",
                    "risk": 0.20,
                    "resonance": 0.30,
                    "entropy_delta": -0.05
                }
            ],
            "consequence_hints": [
                "Submerging the crystal will permanently increase world resonance at the cost of high entropy.",
                "Interfacing directly carries moderate psychological divergence."
            ],
            "context_sources": []
        }

    def generate_branch(self, prompt: str, gen_id: str) -> Dict[str, Any]:
        return {
            "generation_id": gen_id,
            "choices": [
                {
                    "id": "choice_a",
                    "title": "Break the firewall and escape into the Quantum Frontier",
                    "description": "Sever all biometric ties to the city authorities and jump through the reality breach.",
                    "immediate_effect": "High velocity divergence; city alarms trigger immediately.",
                    "long_term_consequence": "You establish a sovereign rogue enclave outside corporate surveillance.",
                    "risk": 0.80,
                    "resonance": 0.60,
                    "entropy_delta": 0.22
                },
                {
                    "id": "choice_b",
                    "title": "Form a clandestine alliance with the Memory Weavers",
                    "description": "Stay embedded in Neo-Kashi and orchestrate a quiet subterranean revolution.",
                    "immediate_effect": "Gain access to confidential archives and trusted allies.",
                    "long_term_consequence": "Gradually transforms the governing structure from within.",
                    "risk": 0.50,
                    "resonance": 0.75,
                    "entropy_delta": 0.10
                },
                {
                    "id": "choice_c",
                    "title": "Surrender the shard to the Syndicate in exchange for amnesty",
                    "description": "Trade historical truth for personal comfort and elite status.",
                    "immediate_effect": "All bounties cleared; instant wealth granted.",
                    "long_term_consequence": "Reality coherence degrades as the Syndicate monopolizes timeline memories.",
                    "risk": 0.15,
                    "resonance": 0.20,
                    "entropy_delta": -0.10
                }
            ],
            "divergence_reasoning": "The choices diverge on risk thresholds, corporate defiance, and existential coherence across timeline nodes.",
            "context_sources": [],
            "simulation_notes": "Generated 3 distinct divergent paths grounded in Neo-Kashi cosmology."
        }

    def generate_future_you(self, prompt: str, gen_id: str) -> Dict[str, Any]:
        return {
            "generation_id": gen_id,
            "is_fictional_simulation": True,
            "identity": "The Grand Weaver of Divergent Timelines",
            "age": "58 Earth Cycles (Subjective Timeline: 140 Years)",
            "world": "Neo-Kashi Prime Axis",
            "occupation": "Keeper of the Subterranean Memory Vaults",
            "personality": "Serene, melancholic, profoundly perceptive, unwavering in resolve.",
            "relationships": ["Aria (Lifelong confidante)", "The Order of Chronos (Adversaries turned allies)"],
            "major_life_events": [
                "Refused the Syndicate bribe in Year 2042.",
                "Opened the Great Resonance Gate during the Second Convergence.",
                "Archived 10,000 lost timelines before reality collapsed."
            ],
            "regrets": [
                "Could not save the original Varanasi archives from burning.",
                "Severed personal bonds during the Quantum Shift."
            ],
            "achievements": [
                "Preserved the consciousness continuum across 4 reality branches.",
                "Taught the next generation of voyagers how to weave choices without fear."
            ],
            "message_to_present_self": "Do not fear the weight of divergence. Every single choice you make is a brushstroke on a canvas that never existed before. Trust your intuition over your fear."
        }

    def generate_world(self, prompt: str, gen_id: str) -> Dict[str, Any]:
        return {
            "generation_id": gen_id,
            "world_name": "Aethelgard 2188",
            "era": "Post-Resonance Era",
            "geography": "Tiered floating archipelagos hovering over a crystalline sea of dark energy.",
            "atmosphere": "Luminous auroras stretching across twilight skies with gentle kinetic rains.",
            "governing_system": "Technocratic Harmonic Council",
            "technology_level": "Tier-IV Quantum Synthesis and Bioluminescent Infrastructure",
            "factions": [
                {"name": "The Weavers of Light", "doctrine": "Harmonic timeline preservation through starlight conduits."},
                {"name": "The Obsidian Syndicate", "doctrine": "Acceleration of entropy to harvest raw quantum potential."}
            ],
            "cultural_rules": [
                "Never silence a memory crystal without community consensus.",
                "Every citizen must plant a chronos-seed upon entering adulthood."
            ],
            "physics_supernatural_rules": "Gravity is variable based on local resonance fields; time dilation occurs near energy rifts.",
            "major_locations": [
                {"name": "The Spire of Dawn", "description": "Central nexus where reality gates are monitored."},
                {"name": "The Sunken Crypts of Year Zero", "description": "Forbidden ruins submerged beneath dark energy waters."}
            ]
        }

    def generate_character(self, prompt: str, gen_id: str) -> Dict[str, Any]:
        return {
            "generation_id": gen_id,
            "name": "Kaelen Voss",
            "role": "Quantum Navigator & Relic Smuggler",
            "background": "Exiled from the High Spire for deciphering forbidden branch coordinates.",
            "personality": "Shrewd, charismatic, deeply empathetic beneath a cynical exterior.",
            "motivations": ["Find the lost timeline where his sister survived the Shift."],
            "fears": ["Complete reality collapse into entropic void."],
            "relationships": {"Aria": "Former partner in the Smugglers Guild"},
            "dialogue_style": "Wry humor mixed with razor-sharp technical precision.",
            "character_arc": "From selfish rogue survivor to the navigator who guides the voyager across impossible branches."
        }

    def generate_decision_analysis(self, prompt: str, gen_id: str) -> Dict[str, Any]:
        return {
            "generation_id": gen_id,
            "decision_id": "dec_sample_01",
            "philosophical_weight": "Existential Transcendence vs. Grounded Responsibility",
            "systemic_implications": "Weakens authoritarian surveillance grid by 18%; increases local underground faction trust.",
            "parallel_paths_unlocked": [
                "The Subterranean Conduit Network",
                "Diplomatic channel with the Memory Weavers"
            ],
            "hidden_tradeoffs": [
                "Higher immediate danger from syndicate enforcers.",
                "Irreversible loss of official civilian standing."
            ],
            "advice_for_traveler": "Consolidate your alliances quickly before the entropy wave reaches peak threshold in the next era."
        }

class GeminiClient:
    """
    Production-grade client for Google Gemini models using the official Google GenAI SDK.
    Features graceful fallback to deterministic mock provider for tests and DEMO_MODE.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.demo_mode = settings.DEMO_MODE or not bool(self.api_key and self.api_key.strip())
        self.mock_provider = MockGeminiProvider()
        self._genai_client = None

        if not self.demo_mode:
            try:
                from google import genai
                self._genai_client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Google GenAI Client with model '{self.model_name}'.")
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI SDK: {e}. Falling back to demo mode.")
                self.demo_mode = True

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        schema_class: Type[T],
        generation_type: str = "story"
    ) -> T:
        """
        Generates structured JSON adhering to the specified Pydantic schema class.
        """
        gen_id = f"gen_{uuid.uuid4().hex[:12]}"
        logger.info(f"Executing AI generation [{generation_type}] (id={gen_id}, demo_mode={self.demo_mode})...")

        if self.demo_mode or self._genai_client is None:
            # Deterministic mock generation
            if schema_class.__name__ == "StoryGenerationResponse":
                raw_dict = self.mock_provider.generate_story(prompt, gen_id)
            elif schema_class.__name__ == "BranchGenerationResponse":
                raw_dict = self.mock_provider.generate_branch(prompt, gen_id)
            elif schema_class.__name__ == "FutureYouResponse":
                raw_dict = self.mock_provider.generate_future_you(prompt, gen_id)
            elif schema_class.__name__ == "WorldGenerationResponse":
                raw_dict = self.mock_provider.generate_world(prompt, gen_id)
            elif schema_class.__name__ == "CharacterGenerationResponse":
                raw_dict = self.mock_provider.generate_character(prompt, gen_id)
            elif schema_class.__name__ == "DecisionAnalysisResponse":
                raw_dict = self.mock_provider.generate_decision_analysis(prompt, gen_id)
            else:
                raw_dict = {"generation_id": gen_id}

            try:
                return schema_class.model_validate(raw_dict)
            except Exception as e:
                raise ResponseValidationError(f"Mock validation failed: {str(e)}")

        # Live Gemini API Call with Structured JSON schema
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=schema_class,
                temperature=0.7
            )
            response = self._genai_client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            raw_text = response.text
            parsed_json = json.loads(raw_text)
            if "generation_id" not in parsed_json:
                parsed_json["generation_id"] = gen_id
            return schema_class.model_validate(parsed_json)
        except Exception as e:
            logger.error(f"Gemini API structured generation failed: {e}", exc_info=True)
            raise GeminiAPIError(f"Gemini generation error: {str(e)}")

gemini_client = GeminiClient()
