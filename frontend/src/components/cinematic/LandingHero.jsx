import React from 'react';
import { Sparkles, Compass, ShieldCheck } from 'lucide-react';
import { audioEngine } from '../../services/audioEngine';
import AudioController from '../ui/AudioController';

export default function LandingHero({ onEnter }) {
  const handleEnterClick = () => {
    audioEngine.startAmbientDrone();
    audioEngine.playChime();
    onEnter();
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: '2rem',
        position: 'relative',
        zIndex: 1
      }}
    >
      {/* Top Bar Controls */}
      <div
        style={{
          position: 'absolute',
          top: '2rem',
          right: '2rem',
          display: 'flex',
          gap: '1rem',
          alignItems: 'center'
        }}
      >
        <AudioController />
      </div>

      {/* Main Hero Card */}
      <div
        className="animate-fade-in"
        style={{
          maxWidth: '850px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '1.8rem'
        }}
      >
        {/* Emblem */}
        <div
          className="animate-float"
          style={{
            width: '72px',
            height: '72px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(247, 200, 115, 0.25) 0%, rgba(6, 7, 10, 0.8) 70%)',
            border: '1px solid var(--border-gold)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 35px var(--starlight-gold-glow)'
          }}
        >
          <Sparkles size={32} color="var(--starlight-gold)" />
        </div>

        {/* Title */}
        <h1
          style={{
            fontSize: 'clamp(3.2rem, 7vw, 5.5rem)',
            fontWeight: 900,
            letterSpacing: '0.18em',
            margin: 0,
            lineHeight: 1.1
          }}
        >
          <span className="gold-gradient-text">KSHAN</span>
        </h1>

        {/* Tagline */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <h2
            style={{
              fontSize: 'clamp(1.2rem, 2.8vw, 2.0rem)',
              fontWeight: 600,
              letterSpacing: '0.12em',
              color: '#fff',
              textTransform: 'uppercase'
            }}
          >
            ONE MOMENT. INFINITE LIVES.
          </h2>
          <p
            style={{
              fontSize: 'clamp(0.95rem, 1.6vw, 1.25rem)',
              color: 'var(--text-secondary)',
              fontFamily: 'var(--font-body)',
              maxWidth: '600px',
              margin: '0 auto',
              lineHeight: 1.6
            }}
          >
            Your choices create worlds that never existed. An authoritative generative AI multiverse simulation.
          </p>
        </div>

        {/* Enter CTA */}
        <div style={{ marginTop: '1.2rem' }}>
          <button
            onClick={handleEnterClick}
            className="btn-primary"
            style={{
              fontSize: '1.1rem',
              padding: '1.1rem 2.8rem',
              borderRadius: '6px'
            }}
          >
            <Compass size={20} />
            ENTER THE MULTIVERSE
          </button>
        </div>

        {/* Feature Badges */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: '1.5rem',
            marginTop: '2.5rem',
            color: 'var(--text-muted)',
            fontSize: '0.85rem',
            fontFamily: 'var(--font-sans)',
            letterSpacing: '0.05em'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ color: 'var(--starlight-gold)' }}>✦</span>
            <span>Deterministic 4-Tier Butterfly Engine</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ color: 'var(--temporal-cyan)' }}>✦</span>
            <span>Persistent pgvector RAG Grounding</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ color: 'var(--quantum-violet)' }}>✦</span>
            <span>Non-Destructive Spacetime Rewind</span>
          </div>
        </div>
      </div>
    </div>
  );
}
