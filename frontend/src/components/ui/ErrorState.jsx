import React from 'react';
import { AlertCircle, X } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';

export default function ErrorState() {
  const { error, setError } = useMultiverse();

  if (!error) return null;

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '2rem',
        right: '2rem',
        maxWidth: '420px',
        padding: '1rem 1.4rem',
        borderRadius: '8px',
        background: 'rgba(244, 63, 94, 0.15)',
        border: '1px solid var(--entropy-crimson)',
        backdropFilter: 'blur(16px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        gap: '0.8rem',
        boxShadow: '0 8px 30px var(--entropy-glow)'
      }}
      className="animate-fade-in"
    >
      <AlertCircle size={20} color="var(--entropy-crimson)" style={{ flexShrink: 0 }} />
      <p style={{ fontSize: '0.88rem', color: '#fff', margin: 0, flex: 1, lineHeight: 1.4 }}>
        {error}
      </p>
      <button
        onClick={() => setError(null)}
        style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', padding: '0.2rem' }}
      >
        <X size={16} />
      </button>
    </div>
  );
}
