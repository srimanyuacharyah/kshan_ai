import React from 'react';
import { Users, X, Heart, ShieldAlert, Sparkles } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';

const DEFAULT_CHARACTERS = [
  {
    name: 'Aria Vance',
    role: 'Memory Cipher Operative',
    archetype: 'The Reluctant Rebel',
    trust_level: 0.72,
    status: 'Cautious Ally',
    last_interaction: 'Assisted you in bypassing the Sky-Pier perimeter, but suspects your true identity.'
  },
  {
    name: 'Kaelen Voss',
    role: 'Syndicate Enforcer Commander',
    archetype: 'The Technocratic Enforcer',
    trust_level: 0.15,
    status: 'Active Pursuer',
    last_interaction: 'Issued an arrest warrant following the decryption breach at dawn.'
  },
  {
    name: 'Archon Veda',
    role: 'Keeper of the Akashic Node',
    archetype: 'The Silent Witness',
    trust_level: 0.88,
    status: 'Spiritual Guide',
    last_interaction: 'Imparted the ancient Sanskrit harmonic frequencies before dissolving into quantum mist.'
  }
];

export default function CharacterConstellation({ onClose }) {
  return (
    <div className="modal-overlay">
      <div
        className="glass-panel-elevated animate-fade-in"
        style={{
          maxWidth: '750px',
          width: '100%',
          borderRadius: '14px',
          padding: '2.2rem',
          border: '1px solid var(--border-violet)',
          boxShadow: '0 0 50px var(--quantum-violet-glow)',
          maxHeight: '90vh',
          overflowY: 'auto'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Users size={22} color="var(--quantum-violet)" />
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', margin: 0 }}>
              CHARACTER CONSTELLATION & RELATIONSHIPS
            </h2>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.4rem', borderRadius: '50%' }}>
            <X size={16} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
          {DEFAULT_CHARACTERS.map((char, idx) => (
            <div
              key={idx}
              className="glass-card"
              style={{
                padding: '1.4rem',
                borderRadius: '10px',
                borderLeft: `4px solid ${char.trust_level > 0.5 ? 'var(--temporal-cyan)' : 'var(--entropy-crimson)'}`
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.6rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', margin: 0 }}>
                    {char.name}
                  </h3>
                  <span style={{ fontSize: '0.78rem', color: 'var(--quantum-violet)', fontWeight: 600 }}>
                    {char.role} • {char.archetype}
                  </span>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <span
                    style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      padding: '0.2rem 0.6rem',
                      borderRadius: '4px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      color: char.trust_level > 0.5 ? 'var(--temporal-cyan)' : 'var(--entropy-crimson)'
                    }}
                  >
                    {char.status}
                  </span>
                  <div style={{ fontSize: '0.8rem', color: '#fff', fontWeight: 700, marginTop: '0.3rem' }}>
                    {Math.round(char.trust_level * 100)}% Trust
                  </div>
                </div>
              </div>

              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                {char.last_interaction}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
