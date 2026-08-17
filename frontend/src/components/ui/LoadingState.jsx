import React from 'react';
import { Sparkles } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';

export default function LoadingState() {
  const { isLoading, loadingMessage } = useMultiverse();

  if (!isLoading) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(6, 7, 10, 0.85)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '1.2rem',
        padding: '2rem',
        textAlign: 'center'
      }}
    >
      <div
        className="animate-float"
        style={{
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          border: '2px solid var(--starlight-gold)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 40px var(--starlight-gold-glow)'
        }}
      >
        <Sparkles size={28} color="var(--starlight-gold)" />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', letterSpacing: '0.08em' }}>
          {loadingMessage || 'Reconstructing spacetime coordinates...'}
        </h3>
        <span style={{ fontSize: '0.82rem', color: 'var(--temporal-cyan)' }}>
          Grounded via KSHAN Multiverse AI Engine
        </span>
      </div>
    </div>
  );
}
