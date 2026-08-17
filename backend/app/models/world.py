from sqlalchemy import Column, String, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.app.models.base import Base, UUIDMixin, TimestampMixin

class World(Base, UUIDMixin, TimestampMixin):
    """World lore and cosmology associated with a scenario or reality."""
    __tablename__ = "worlds"

    scenario_id = Column(String(36), ForeignKey("scenarios.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(200), nullable=False)
    cosmos_type = Column(String(100), default="Single Realm", nullable=False)
    laws_of_physics = Column(Text, nullable=True)
    factions_overview = Column(JSON, default=list, nullable=False)
    lore_chronicle = Column(Text, nullable=False)
    world_metadata = Column(JSON, default=dict, nullable=False)

    # Relationships
    scenario = relationship("Scenario", back_populates="worlds")
    locations = relationship("Location", back_populates="world", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="world", cascade="all, delete-orphan")

class Location(Base, UUIDMixin, TimestampMixin):
    """Key spatial point in a world."""
    __tablename__ = "locations"

    world_id = Column(String(36), ForeignKey("worlds.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(200), nullable=False)
    realm_zone = Column(String(100), nullable=False) # e.g. 'Undercity', 'Orbital Ring', 'Monsoon Spires'
    description = Column(Text, nullable=False)
    atmosphere = Column(String(255), nullable=True)
    danger_rating = Column(Float, default=0.5, nullable=False)

    # Relationships
    world = relationship("World", back_populates="locations")

class Character(Base, UUIDMixin, TimestampMixin):
    """NPC or counterpart existing in a world."""
    __tablename__ = "characters"

    world_id = Column(String(36), ForeignKey("worlds.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(150), nullable=False)
    role = Column(String(100), nullable=False) # 'Mentor', 'Nemesis', 'Parallel Echo', 'Companion'
    faction = Column(String(100), nullable=True)
    backstory = Column(Text, nullable=False)
    psychological_profile = Column(JSON, default=dict, nullable=False)
    dialogue_style = Column(String(255), nullable=True)

    # Relationships
    world = relationship("World", back_populates="characters")
