import React from 'react';
import { Globe, X, Shield, MapPin, Compass } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';

export default function WorldExplorer({ onClose }) {
  const { activeScenario, activeBranch } = useMultiverse();

  const locations = [
    {
      name: 'Manikarnika Sky-Pier',
      type: 'Floating Quantum Dock',
      faction: 'Independent Smugglers',
      danger: 'High',
      description: 'Suspended 2,000 meters above the ancient sacred river. Charged plasma cables hum in harmony with Vedic chants broadcast on encrypted frequencies.'
    },
    {
      name: 'The Citadel of Harmonic Glass',
      type: 'Governmental Seat',
      faction: 'The Technocratic Syndicate',
      danger: 'Extreme',
      description: 'A crystalline spire housing the consciousness archive. Only high-resonance souls are permitted past the outer temporal perimeter.'
    },
    {
      name: 'Sub-Ghat Memory Bazaar',
      type: 'Black Market Underbelly',
      faction: 'Memory Weavers',
      danger: 'Moderate',
      description: 'Hidden beneath flooded ruins where illicit neural shards and ancient bio-relics are bartered under bioluminescent moss.'
    }
  ];

  return (
    <div className="modal-overlay">
      <div
        className="glass-panel-elevated animate-fade-in"
        style={{
          maxWidth: '780px',
          width: '100%',
          borderRadius: '14px',
          padding: '2.2rem',
          border: '1px solid var(--border-cyan)',
          boxShadow: '0 0 50px var(--temporal-cyan-glow)',
          maxHeight: '90vh',
          overflowY: 'auto'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Globe size={22} color="var(--temporal-cyan)" />
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', margin: 0 }}>
              WORLD ATLAS: {activeScenario?.title || 'PRIME REALITY'}
            </h2>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.4rem', borderRadius: '50%' }}>
            <X size={16} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
          {locations.map((loc, idx) => (
            <div
              key={idx}
              className="glass-card"
              style={{
                padding: '1.4rem',
                borderRadius: '10px',
                borderLeft: '4px solid var(--temporal-cyan)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.6rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', margin: 0 }}>
                    {loc.name}
                  </h3>
                  <span style={{ fontSize: '0.78rem', color: 'var(--temporal-cyan)', fontWeight: 600 }}>
                    {loc.type} • Controlled by {loc.faction}
                  </span>
                </div>

                <span
                  style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    padding: '0.2rem 0.6rem',
                    borderRadius: '4px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    color: loc.danger === 'Extreme' ? 'var(--entropy-crimson)' : 'var(--starlight-gold)'
                  }}
                >
                  {loc.danger} Danger
                </span>
              </div>

              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                {loc.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
