import React from 'react';
import { useMultiverse } from '../../context/MultiverseContext';
import { Shield, Zap, Flame, Compass, Activity, Globe, Users } from 'lucide-react';

function RadialGauge({ label, value, color, icon: Icon, unit = "%" }) {
  const radius = 32;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (value * circumference);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '0.4rem',
        padding: '0.8rem 0.5rem',
        background: 'rgba(255, 255, 255, 0.02)',
        borderRadius: '8px',
        border: '1px solid rgba(255, 255, 255, 0.05)'
      }}
    >
      <div style={{ position: 'relative', width: '74px', height: '74px' }}>
        <svg width="74" height="74" style={{ transform: 'rotate(-90deg)' }}>
          {/* Background circle */}
          <circle
            cx="37"
            cy="37"
            r={radius}
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth="5"
            fill="transparent"
          />
          {/* Active arc */}
          <circle
            cx="37"
            cy="37"
            r={radius}
            stroke={color}
            strokeWidth="5"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{
              transition: 'stroke-dashoffset 0.8s cubic-bezier(0.16, 1, 0.3, 1), stroke 0.4s ease'
            }}
          />
        </svg>

        {/* Center Readout */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          {Icon && <Icon size={14} color={color} style={{ marginBottom: '2px' }} />}
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff' }}>
            {Math.round(value * 100)}{unit}
          </span>
        </div>
      </div>

      <span
        style={{
          fontSize: '0.7rem',
          fontWeight: 600,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: 'var(--text-secondary)'
        }}
      >
        {label}
      </span>
    </div>
  );
}

export default function StateHUD() {
  const { stateVector, activeBranch } = useMultiverse();

  return (
    <div
      className="glass-panel"
      style={{
        borderRadius: '12px',
        padding: '1.4rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.2rem'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3
          style={{
            fontSize: '0.88rem',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'var(--starlight-gold)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          <Activity size={16} />
          REALITY STATE HUD
        </h3>
        <span
          style={{
            fontSize: '0.72rem',
            padding: '0.2rem 0.6rem',
            borderRadius: '4px',
            background: 'rgba(34, 211, 238, 0.1)',
            color: 'var(--temporal-cyan)',
            border: '1px solid var(--border-cyan)'
          }}
        >
          {activeBranch?.branch_code || 'PRIME'}
        </span>
      </div>

      {/* Primary Radial Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '0.8rem'
        }}
      >
        <RadialGauge
          label="Entropy"
          value={stateVector.entropy}
          color="var(--entropy-crimson)"
          icon={Flame}
        />
        <RadialGauge
          label="Resonance"
          value={stateVector.resonance}
          color="var(--starlight-gold)"
          icon={Zap}
        />
        <RadialGauge
          label="Regret"
          value={stateVector.regret}
          color="var(--quantum-violet)"
          icon={Shield}
        />
        <RadialGauge
          label="Destiny Shift"
          value={stateVector.destiny_shift}
          color="var(--temporal-cyan)"
          icon={Compass}
        />
      </div>

      {/* Secondary Metrics Bar */}
      <div
        style={{
          padding: '0.9rem',
          borderRadius: '8px',
          background: 'rgba(0, 0, 0, 0.35)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.6rem',
          fontSize: '0.78rem'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Globe size={13} /> World Coherence
          </span>
          <span style={{ fontWeight: 600, color: '#fff' }}>
            {Math.round((stateVector.world_stability || 0.85) * 100)}%
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Users size={13} /> Social Stability
          </span>
          <span style={{ fontWeight: 600, color: '#fff' }}>
            {Math.round((stateVector.social_stability || 0.80) * 100)}%
          </span>
        </div>
      </div>
    </div>
  );
}
