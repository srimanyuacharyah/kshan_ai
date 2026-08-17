import React from 'react';
import { GitBranch, Sparkles, CheckCircle, Clock } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';

export default function TimelineCanvas({ onSelectBranch }) {
  const { branchTree, activeBranch, loadBranchDetails } = useMultiverse();
  const nodes = branchTree?.nodes || [];

  return (
    <div
      className="glass-panel"
      style={{
        borderRadius: '12px',
        padding: '1.4rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        height: '100%'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3
          style={{
            fontSize: '0.88rem',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'var(--temporal-cyan)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          <GitBranch size={16} />
          MULTIVERSE BRANCH TREE
        </h3>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {nodes.length} Realities
        </span>
      </div>

      {/* Interactive Branch Node List / Tree */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.8rem',
          overflowY: 'auto',
          maxHeight: '400px',
          paddingRight: '0.4rem'
        }}
      >
        {nodes.map((n) => {
          const isActive = activeBranch?.id === n.branch_id || activeBranch?.id === n.id;
          const depth = n.depth || 0;

          return (
            <div
              key={n.id || n.branch_id}
              onClick={() => {
                loadBranchDetails(n.branch_id || n.id);
                if (onSelectBranch) onSelectBranch(n);
              }}
              className="glass-card"
              style={{
                padding: '0.9rem',
                borderRadius: '8px',
                cursor: 'pointer',
                marginLeft: `${Math.min(depth * 14, 42)}px`,
                border: isActive ? '1px solid var(--starlight-gold)' : '1px solid var(--border-glass)',
                background: isActive ? 'rgba(247, 200, 115, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                boxShadow: isActive ? '0 0 15px var(--starlight-gold-glow)' : 'none',
                position: 'relative',
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                <span
                  style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    color: isActive ? 'var(--starlight-gold)' : 'var(--temporal-cyan)'
                  }}
                >
                  {n.branch_code || `DEPTH ${depth}`}
                </span>
                {isActive && (
                  <span
                    style={{
                      fontSize: '0.65rem',
                      color: 'var(--starlight-gold)',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      padding: '0.1rem 0.4rem',
                      borderRadius: '3px',
                      background: 'rgba(247, 200, 115, 0.15)'
                    }}
                  >
                    ACTIVE
                  </span>
                )}
              </div>

              <div style={{ fontSize: '0.86rem', fontWeight: 600, color: '#fff' }}>
                {n.label || n.branch_name || 'Parallel Branch'}
              </div>

              {/* State Pills */}
              <div style={{ display: 'flex', gap: '0.6rem', marginTop: '0.5rem', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                <span>Entropy: {Math.round((n.entropy || 0.1) * 100)}%</span>
                <span>•</span>
                <span>Resonance: {Math.round((n.resonance || 0.7) * 100)}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
