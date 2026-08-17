"""001_initial_multiverse_schema

Revision ID: 001_initial_multiverse_schema
Revises: 
Create Date: 2026-08-17 10:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from backend.app.core.config import settings

revision: str = '001_initial_multiverse_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Ensure vector extension is present
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 2. user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('bio', sa.String(length=500), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('sound_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('preferences', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_user_profiles_user_id'), 'user_profiles', ['user_id'], unique=True)

    # 3. scenarios table
    op.create_table(
        'scenarios',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('genre', sa.String(length=50), nullable=False),
        sa.Column('tagline', sa.String(length=255), nullable=False),
        sa.Column('premise', sa.Text(), nullable=False),
        sa.Column('initial_kshan_moment', sa.Text(), nullable=False),
        sa.Column('sensory_ambiance', sa.String(length=255), nullable=True),
        sa.Column('cover_image_url', sa.String(length=500), nullable=True),
        sa.Column('is_curated', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('metadata_payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scenarios_slug'), 'scenarios', ['slug'], unique=True)
    op.create_index(op.f('ix_scenarios_genre'), 'scenarios', ['genre'], unique=False)

    # 4. future_profiles table
    op.create_table(
        'future_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('scenario_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('archetype', sa.String(length=100), nullable=False),
        sa.Column('philosophical_alignment', sa.String(length=100), nullable=True),
        sa.Column('psychological_traits', sa.JSON(), nullable=False),
        sa.Column('custom_seed_prompt', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ondelete='SET NULL')
    )
    op.create_index(op.f('ix_future_profiles_user_id'), 'future_profiles', ['user_id'], unique=False)

    # 5. reality_branches table
    op.create_table(
        'reality_branches',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('future_profile_id', sa.String(length=36), nullable=True),
        sa.Column('parent_branch_id', sa.String(length=36), nullable=True),
        sa.Column('fork_node_id', sa.String(length=36), nullable=True),
        sa.Column('branch_name', sa.String(length=200), nullable=False),
        sa.Column('branch_code', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('entropy_level', sa.Float(), nullable=False, server_default='0.1'),
        sa.Column('resonance_score', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('regret_index', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('destiny_shift', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('branch_metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['future_profile_id'], ['future_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_branch_id'], ['reality_branches.id'], ondelete='SET NULL')
    )
    op.create_index(op.f('ix_reality_branches_user_id'), 'reality_branches', ['user_id'], unique=False)
    op.create_index(op.f('ix_reality_branches_branch_code'), 'reality_branches', ['branch_code'], unique=False)

    # 6. multiverse_states table
    op.create_table(
        'multiverse_states',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('branch_id', sa.String(length=36), nullable=False),
        sa.Column('active_node_id', sa.String(length=36), nullable=True),
        sa.Column('total_nodes_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('world_coherence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('timeline_era', sa.String(length=100), nullable=False, server_default='Genesis Moment'),
        sa.Column('state_variables', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['branch_id'], ['reality_branches.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_multiverse_states_branch_id'), 'multiverse_states', ['branch_id'], unique=True)

    # 7. timeline_nodes table
    op.create_table(
        'timeline_nodes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('branch_id', sa.String(length=36), nullable=False),
        sa.Column('parent_node_id', sa.String(length=36), nullable=True),
        sa.Column('depth_level', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('era_year', sa.String(length=50), nullable=False, server_default='Year 0'),
        sa.Column('story_text', sa.Text(), nullable=False),
        sa.Column('sensory_cue', sa.String(length=255), nullable=True),
        sa.Column('audio_ambiance', sa.String(length=100), nullable=False, server_default='cosmic_drone'),
        sa.Column('entropy_delta', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('resonance_delta', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('regret_delta', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('butterfly_impact', sa.String(length=255), nullable=True),
        sa.Column('node_metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['branch_id'], ['reality_branches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_node_id'], ['timeline_nodes.id'], ondelete='SET NULL')
    )
    op.create_index(op.f('ix_timeline_nodes_user_id'), 'timeline_nodes', ['user_id'], unique=False)
    op.create_index(op.f('ix_timeline_nodes_branch_id'), 'timeline_nodes', ['branch_id'], unique=False)

    # 8. choices table
    op.create_table(
        'choices',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('node_id', sa.String(length=36), nullable=False),
        sa.Column('choice_label', sa.String(length=255), nullable=False),
        sa.Column('choice_description', sa.Text(), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False, server_default='moderate'),
        sa.Column('philosophical_vector', sa.String(length=100), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['node_id'], ['timeline_nodes.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_choices_node_id'), 'choices', ['node_id'], unique=False)

    # 9. consequences table
    op.create_table(
        'consequences',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('choice_id', sa.String(length=36), nullable=False),
        sa.Column('predicted_outcome', sa.Text(), nullable=False),
        sa.Column('expected_entropy_shift', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('expected_resonance_shift', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('expected_regret_shift', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('world_effect_summary', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['choice_id'], ['choices.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_consequences_choice_id'), 'consequences', ['choice_id'], unique=True)

    # 10. decisions table
    op.create_table(
        'decisions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('node_id', sa.String(length=36), nullable=False),
        sa.Column('chosen_choice_id', sa.String(length=36), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('divergence_magnitude', sa.Float(), nullable=False, server_default='0.1'),
        sa.Column('decision_metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['node_id'], ['timeline_nodes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chosen_choice_id'], ['choices.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_decisions_user_id'), 'decisions', ['user_id'], unique=False)
    op.create_index(op.f('ix_decisions_node_id'), 'decisions', ['node_id'], unique=True)

    # 11. worlds table
    op.create_table(
        'worlds',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('scenario_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('cosmos_type', sa.String(length=100), nullable=False, server_default='Single Realm'),
        sa.Column('laws_of_physics', sa.Text(), nullable=True),
        sa.Column('factions_overview', sa.JSON(), nullable=False),
        sa.Column('lore_chronicle', sa.Text(), nullable=False),
        sa.Column('world_metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_worlds_scenario_id'), 'worlds', ['scenario_id'], unique=False)

    # 12. locations table
    op.create_table(
        'locations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('world_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('realm_zone', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('atmosphere', sa.String(length=255), nullable=True),
        sa.Column('danger_rating', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_locations_world_id'), 'locations', ['world_id'], unique=False)

    # 13. characters table
    op.create_table(
        'characters',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('world_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('faction', sa.String(length=100), nullable=True),
        sa.Column('backstory', sa.Text(), nullable=False),
        sa.Column('psychological_profile', sa.JSON(), nullable=False),
        sa.Column('dialogue_style', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_characters_world_id'), 'characters', ['world_id'], unique=False)

    # 14. memories table
    op.create_table(
        'memories',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('branch_id', sa.String(length=36), nullable=False),
        sa.Column('node_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('emotional_tone', sa.String(length=50), nullable=False, server_default='nostalgic'),
        sa.Column('memory_type', sa.String(length=50), nullable=False, server_default='event'),
        sa.Column('clarity_level', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('memory_metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['branch_id'], ['reality_branches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['node_id'], ['timeline_nodes.id'], ondelete='SET NULL')
    )
    op.create_index(op.f('ix_memories_user_id'), 'memories', ['user_id'], unique=False)
    op.create_index(op.f('ix_memories_branch_id'), 'memories', ['branch_id'], unique=False)

    # 15. media_items table
    op.create_table(
        'media_items',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('memory_id', sa.String(length=36), nullable=False),
        sa.Column('media_type', sa.String(length=50), nullable=False, server_default='image'),
        sa.Column('media_url', sa.String(length=500), nullable=False),
        sa.Column('caption', sa.String(length=255), nullable=True),
        sa.Column('generated_prompt', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['memory_id'], ['memories.id'], ondelete='CASCADE')
    )

    # 16. conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('branch_id', sa.String(length=36), nullable=False),
        sa.Column('persona_title', sa.String(length=150), nullable=False, server_default='Future You'),
        sa.Column('timeline_context_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['branch_id'], ['reality_branches.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    # 17. conversation_messages table
    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=False),
        sa.Column('sender_role', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('grounding_sources', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE')
    )

    # 18. embeddings table with dynamic vector dimension
    op.create_table(
        'embeddings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('branch_id', sa.String(length=36), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('document_content', sa.Text(), nullable=False),
        sa.Column('document_title', sa.String(length=255), nullable=True),
        sa.Column('metadata_payload', sa.JSON(), nullable=False),
        sa.Column('embedding_vector', Vector(settings.EMBEDDING_DIMENSION), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['branch_id'], ['reality_branches.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_embeddings_user_id'), 'embeddings', ['user_id'], unique=False)
    op.create_index(op.f('ix_embeddings_entity_type'), 'embeddings', ['entity_type'], unique=False)
    op.create_index(op.f('ix_embeddings_entity_id'), 'embeddings', ['entity_id'], unique=False)

def downgrade() -> None:
    op.drop_table('embeddings')
    op.drop_table('conversation_messages')
    op.drop_table('conversations')
    op.drop_table('media_items')
    op.drop_table('memories')
    op.drop_table('characters')
    op.drop_table('locations')
    op.drop_table('worlds')
    op.drop_table('decisions')
    op.drop_table('consequences')
    op.drop_table('choices')
    op.drop_table('timeline_nodes')
    op.drop_table('multiverse_states')
    op.drop_table('reality_branches')
    op.drop_table('future_profiles')
    op.drop_table('scenarios')
    op.drop_table('user_profiles')
    op.drop_table('users')
