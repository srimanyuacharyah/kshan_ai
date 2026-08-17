import React from 'react';
import { Play, Sparkles, AlertTriangle, Compass, ArrowLeft } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';
import AudioController from '../ui/AudioController';

// Artwork gradients and ambient palettes mapped by scenario slug
const SCENARIO_ARTWORK_MAPPING = {
  'neo-kashi-2042': {
    backdrop: 'radial-gradient(circle at top right, rgba(139, 92, 246, 0.4) 0%, rgba(6, 7, 10, 0.95) 75%)',
    borderColor: 'var(--border-violet)',
    glowColor: 'var(--quantum-violet-glow)',
    accentGradient: 'linear-gradient(135deg, #8b5cf6, #22d3ee)',
    genreBadge: '#a855f7'
  },
  'aethelgard-2188': {
    backdrop: 'radial-gradient(circle at top right, rgba(34, 211, 238, 0.35) 0%, rgba(6, 7, 10, 0.95) 75%)',
    borderColor: 'var(--border-cyan)',
    glowColor: 'var(--temporal-cyan-glow)',
    accentGradient: 'linear-gradient(135deg, #22d3ee, #3b82f6)',
    genreBadge: '#06b6d4'
  },
  'the-obsidian-expanse': {
    backdrop: 'radial-gradient(circle at top right, rgba(247, 200, 115, 0.35) 0%, rgba(6, 7, 10, 0.95) 75%)',
    borderColor: 'var(--border-gold)',
    glowColor: 'var(--starlight-gold-glow)',
    accentGradient: 'linear-gradient(135deg, #f7c873, #f43f5e)',
    genreBadge: '#f59e0b'
  }
};

export default function ScenarioSelector({ onBack }) {
  const { scenarios, selectScenario, isAuthenticated, setActiveModal } = useMultiverse();

  const handleSelect = (scenario) => {
    if (!isAuthenticated) {
      setActiveModal('auth');
      return;
    }
    selectScenario(scenario);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        padding: '3rem 2rem',
        position: 'relative',
        zIndex: 1,
        maxWidth: '1350px',
        margin: '0 auto'
      }}
    >
      {/* Top Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '3rem'
        }}
      >
        <button onClick={onBack} className="btn-secondary">
          <ArrowLeft size={16} />
          <span>RETURN TO NEXUS</span>
        </button>
        <AudioController />
      </div>

      {/* Header Section */}
      <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
        <h1
          className="gold-gradient-text"
          style={{
            fontSize: 'clamp(2.4rem, 5vw, 3.8rem)',
            fontWeight: 800,
            marginBottom: '0.8rem'
          }}
        >
          SELECT AN INFLECTION POINT
        </h1>
        <p
          style={{
            color: 'var(--text-secondary)',
            fontSize: '1.1rem',
            maxWidth: '650px',
            margin: '0 auto',
            lineHeight: 1.6
          }}
        >
          Choose a Genesis moment. Your decisions will spawn divergent, persistent timelines across the multiverse.
        </p>
      </div>

      {/* Movie Poster Scenario Cards Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '2.5rem'
        }}
      >
        {scenarios.map((sc) => {
          const styling = SCENARIO_ARTWORK_MAPPING[sc.slug] || SCENARIO_ARTWORK_MAPPING['neo-kashi-2042'];
          const meta = sc.metadata || {};

          return (
            <div
              key={sc.id || sc.slug}
              className="glass-card animate-fade-in"
              style={{
                borderRadius: '12px',
                background: styling.backdrop,
                border: `1px solid ${styling.borderColor}`,
                padding: '2.2rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                minHeight: '480px',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              {/* Header Info */}
              <div>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '1.2rem'
                  }}
                >
                  <span
                    style={{
                      fontSize: '0.75rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.12em',
                      fontWeight: 700,
                      padding: '0.3rem 0.8rem',
                      borderRadius: '20px',
                      background: 'rgba(255, 255, 255, 0.08)',
                      color: styling.genreBadge,
                      border: `1px solid ${styling.borderColor}`
                    }}
                  >
                    {sc.genre}
                  </span>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#f43f5e', fontSize: '0.8rem', fontWeight: 600 }}>
                    <AlertTriangle size={14} />
                    <span>{meta.danger_rating?.toUpperCase() || 'MODERATE'} RISK</span>
                  </div>
                </div>

                {/* Poster Title */}
                <h2
                  style={{
                    fontSize: '1.9rem',
                    fontWeight: 700,
                    marginBottom: '0.5rem',
                    color: '#fff'
                  }}
                >
                  {sc.title}
                </h2>
                <p
                  style={{
                    fontStyle: 'italic',
                    color: 'var(--starlight-gold)',
                    fontSize: '0.95rem',
                    marginBottom: '1.2rem'
                  }}
                >
                  "{sc.tagline}"
                </p>

                {/* Premise */}
                <p
                  style={{
                    color: 'var(--text-secondary)',
                    fontSize: '0.92rem',
                    lineHeight: 1.6,
                    fontFamily: 'var(--font-body)',
                    marginBottom: '1.5rem'
                  }}
                >
                  {sc.premise}
                </p>
              </div>

              {/* Footer Meta & Button */}
              <div>
                {/* Meta details */}
                <div
                  style={{
                    padding: '0.9rem',
                    borderRadius: '6px',
                    background: 'rgba(0, 0, 0, 0.45)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    marginBottom: '1.5rem',
                    fontSize: '0.8rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.4rem'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Atmosphere</span>
                    <span style={{ color: 'var(--text-primary)' }}>{meta.atmosphere || 'Standard'}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Cosmos Type</span>
                    <span style={{ color: 'var(--temporal-cyan)' }}>{meta.cosmos_type || 'Parallel Axis'}</span>
                  </div>
                </div>

                <button
                  onClick={() => handleSelect(sc)}
                  className="btn-primary"
                  style={{
                    width: '100%',
                    justifyContent: 'center',
                    padding: '0.95rem'
                  }}
                >
                  <Play size={16} />
                  ENTER REALITY
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
