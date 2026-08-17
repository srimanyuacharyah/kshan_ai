import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.scenario import Scenario
from backend.app.core.logging import get_logger

logger = get_logger("kshan.api.scenarios")

router = APIRouter()

CURATED_SCENARIOS = [
    {
        "title": "Neo-Kashi 2042",
        "slug": "neo-kashi-2042",
        "genre": "Cyber-Mythic",
        "tagline": "The sacred river meets the quantum grid.",
        "premise": "In the floating megacity above the ancient ghats, a memory crystal falls from the sky into your hands, containing the redacted history of humanity's consciousness convergence.",
        "initial_kshan_moment": "You stand at the edge of the Manikarnika Sky-Pier. Rain sizzles on holographic prayer flags as the syndicate enforcers close in.",
        "sensory_ambiance": "Distant temple bells echoing through electrostatic hum; smell of wet petrichor and ozone.",
        "metadata_payload": {
            "danger_rating": "high",
            "estimated_divergence": "0.85",
            "atmosphere": "Neon Rain / Ancient Cybernetics",
            "cosmos_type": "Floating Megacity",
            "suggested_archetypes": ["The Quantum Rebel", "The Memory Weaver", "The Technocratic Guardian"]
        }
    },
    {
        "title": "Aethelgard 2188",
        "slug": "aethelgard-2188",
        "genre": "Quantum Sci-Fi",
        "tagline": "Where silence is the only remaining currency.",
        "premise": "The Harmonic Council governs an archipelago of floating spires. A subterranean frequency has begun disintegrating the crystalline stabilizers maintaining planetary gravity.",
        "initial_kshan_moment": "The Spire of Dawn shudders as dark energy waters swirl beneath your observation pod. A glowing seal begins deciphering itself before you.",
        "sensory_ambiance": "Luminous auroras shifting in deep lavender; crystalline chimes pulsing at 432 Hz.",
        "metadata_payload": {
            "danger_rating": "existential",
            "estimated_divergence": "0.92",
            "atmosphere": "Twilight Bioluminescence / Variable Gravity",
            "cosmos_type": "Tier-IV Harmonic Nexus",
            "suggested_archetypes": ["The Celestial Architect", "The Relic Smuggler", "The Void Seeker"]
        }
    },
    {
        "title": "The Obsidian Expanse",
        "slug": "the-obsidian-expanse",
        "genre": "Personal Crossroad",
        "tagline": "Every choice unbinds a universe.",
        "premise": "At the zero-point nexus of the multiverse, you are handed the Chronos Shard. Choosing who lives in the prime reality will permanently dissolve four parallel sibling timelines.",
        "initial_kshan_moment": "Infinite mirrors stretch into obsidian darkness. In every reflection, a different version of you reaches for the same shard.",
        "sensory_ambiance": "Profound silence punctuated by distant glass reverberations; absolute dark with starlight gold accents.",
        "metadata_payload": {
            "danger_rating": "moderate",
            "estimated_divergence": "0.78",
            "atmosphere": "Zero-G Glass Void / Temporal Mirrors",
            "cosmos_type": "Multiverse Nexus",
            "suggested_archetypes": ["The Philosopher King", "The Silent Witness", "The Reality Weaver"]
        }
    }
]

@router.get("", response_model=List[Dict[str, Any]])
async def list_scenarios(db: AsyncSession = Depends(get_db)):
    """
    Returns curated scenarios. Auto-seeds default curated scenarios if the database is clean.
    """
    try:
        stmt = select(Scenario).order_by(Scenario.created_at.asc())
        res = await db.execute(stmt)
        scenarios = res.scalars().all()

        if not scenarios:
            logger.info("Seeding initial curated scenarios into database...")
            for s_data in CURATED_SCENARIOS:
                sc = Scenario(
                    id=str(uuid.uuid4()),
                    title=s_data["title"],
                    slug=s_data["slug"],
                    genre=s_data["genre"],
                    tagline=s_data["tagline"],
                    premise=s_data["premise"],
                    initial_kshan_moment=s_data["initial_kshan_moment"],
                    sensory_ambiance=s_data["sensory_ambiance"],
                    is_curated=True,
                    metadata_payload=s_data["metadata_payload"]
                )
                db.add(sc)
            await db.commit()
            res = await db.execute(stmt)
            scenarios = res.scalars().all()

        return [
            {
                "id": s.id,
                "title": s.title,
                "slug": s.slug,
                "genre": s.genre,
                "tagline": s.tagline,
                "premise": s.premise,
                "initial_kshan_moment": s.initial_kshan_moment,
                "sensory_ambiance": s.sensory_ambiance,
                "cover_image_url": s.cover_image_url,
                "metadata": s.metadata_payload
            }
            for s in scenarios
        ]
    except Exception as e:
        logger.error(f"Error fetching scenarios: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{scenario_id}")
async def get_scenario(scenario_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieves a single scenario by ID or slug.
    """
    stmt = select(Scenario).where(
        (Scenario.id == scenario_id) | (Scenario.slug == scenario_id)
    )
    res = await db.execute(stmt)
    sc = res.scalar_one_or_none()
    if not sc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found.")
    return {
        "id": sc.id,
        "title": sc.title,
        "slug": sc.slug,
        "genre": sc.genre,
        "tagline": sc.tagline,
        "premise": sc.premise,
        "initial_kshan_moment": sc.initial_kshan_moment,
        "sensory_ambiance": sc.sensory_ambiance,
        "cover_image_url": sc.cover_image_url,
        "metadata": sc.metadata_payload
    }
