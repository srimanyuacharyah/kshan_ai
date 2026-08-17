import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowDown, Users, Globe, Lock, Unlock, CheckCircle2 } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';

export default function ButterflySequence() {
  const { butterflyRipple, setButterflyRipple } = useMultiverse();
  const [step, setStep] = useState(1);

  useEffect(() => {
    if (!butterflyRipple) return;
    const timer1 = setTimeout(() => setStep(2), 600);
    const timer2 = setTimeout(() => setStep(3), 1200);
    const timer3 = setTimeout(() => setStep(4), 1800);
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [butterflyRipple]);

  if (!butterflyRipple) return null;

  return (
    <div className="modal-overlay">
      <div
        className="glass-panel-elevated animate-fade-in"
        style={{
          maxWidth: '750px',
          width: '100%',
          borderRadius: '14px',
          padding: '2.2rem',
          border: '1px solid var(--border-gold)',
          boxShadow: '0 0 50px rgba(247, 200, 115, 0.2)',
          maxHeight: '90vh',
          overflowY: 'auto'
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '1.8rem' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.35rem 0.9rem',
              borderRadius: '20px',
              background: 'rgba(247, 200, 115, 0.1)',
              border: '1px solid var(--border-gold)',
              color: 'var(--starlight-gold)',
              fontSize: '0.8rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              marginBottom: '0.6rem'
            }}
          >
            <Sparkles size={14} />
            Deterministic Butterfly Effect Cascade
          </div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff' }}>
            CAUSAL REPERCUSSIONS UNLOCKED
          </h2>
        </div>

        {/* 4-Tier Cascade Chain */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'center' }}>
          {/* Tier 1: Immediate */}
          <div
            className="glass-card animate-fade-in"
            style={{
              width: '100%',
              padding: '1.2rem',
              borderRadius: '8px',
              borderLeft: '4px solid var(--starlight-gold)'
            }}
          >
            <span style={{ fontSize: '0.72rem', color: 'var(--starlight-gold)', fontWeight: 700, textTransform: 'uppercase' }}>
              Tier 1 — Immediate Consequence
            </span>
            <p style={{ fontSize: '0.95rem', color: '#fff', marginTop: '0.3rem', lineHeight: 1.5 }}>
              {butterflyRipple.immediate_effect}
            </p>
          </div>

          {step >= 2 && <ArrowDown size={18} color="var(--starlight-gold)" />}

          {/* Tier 2: Secondary Characters */}
          {step >= 2 && (
            <div
              className="glass-card animate-fade-in"
              style={{
                width: '100%',
                padding: '1.2rem',
                borderRadius: '8px',
                borderLeft: '4px solid var(--quantum-violet)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.4rem' }}>
                <Users size={14} color="var(--quantum-violet)" />
                <span style={{ fontSize: '0.72rem', color: 'var(--quantum-violet)', fontWeight: 700, textTransform: 'uppercase' }}>
                  Tier 2 — Character Allegiance Shard
                </span>
              </div>
              {butterflyRipple.secondary_effects?.map((eff, i) => (
                <div key={i} style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
                  • <strong style={{ color: '#fff' }}>{eff.character_name}</strong>: {eff.notes} ({eff.trust_delta > 0 ? `+${eff.trust_delta * 100}% Trust` : `${eff.trust_delta * 100}% Trust`})
                </div>
              ))}
            </div>
          )}

          {step >= 3 && <ArrowDown size={18} color="var(--starlight-gold)" />}

          {/* Tier 3: Tertiary World State */}
          {step >= 3 && (
            <div
              className="glass-card animate-fade-in"
              style={{
                width: '100%',
                padding: '1.2rem',
                borderRadius: '8px',
                borderLeft: '4px solid var(--temporal-cyan)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.4rem' }}>
                <Globe size={14} color="var(--temporal-cyan)" />
                <span style={{ fontSize: '0.72rem', color: 'var(--temporal-cyan)', fontWeight: 700, textTransform: 'uppercase' }}>
                  Tier 3 — World State Shift
                </span>
              </div>
              {butterflyRipple.tertiary_effects?.map((weff, i) => (
                <div key={i} style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.3rem' }}>
                  • <strong style={{ color: '#fff' }}>{weff.variable_name}</strong>: {weff.description}
                </div>
              ))}
            </div>
          )}

          {step >= 4 && <ArrowDown size={18} color="var(--starlight-gold)" />}

          {/* Tier 4: Long-Term Pathways */}
          {step >= 4 && (
            <div
              className="glass-card animate-fade-in"
              style={{
                width: '100%',
                padding: '1.2rem',
                borderRadius: '8px',
                borderLeft: '4px solid var(--entropy-crimson)'
              }}
            >
              <span style={{ fontSize: '0.72rem', color: '#f43f5e', fontWeight: 700, textTransform: 'uppercase' }}>
                Tier 4 — Future Timeline Pathways
              </span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginTop: '0.5rem' }}>
                {butterflyRipple.unlocked_pathways?.map((path, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#10b981', fontSize: '0.86rem' }}>
                    <Unlock size={14} /> Unlocked: {path}
                  </div>
                ))}
                {butterflyRipple.locked_pathways?.map((path, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#f43f5e', fontSize: '0.86rem' }}>
                    <Lock size={14} /> Locked: {path}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Continue Action */}
        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <button
            onClick={() => setButterflyRipple(null)}
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center' }}
          >
            <CheckCircle2 size={18} />
            ENTER DIVERGENT REALITY
          </button>
        </div>
      </div>
    </div>
  );
}
