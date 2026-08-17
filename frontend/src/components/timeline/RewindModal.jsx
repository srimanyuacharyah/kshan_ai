import React, { useState } from 'react';
import { RotateCcw, Clock, AlertCircle, X, Compass } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';

export default function RewindModal({ onClose }) {
  const { timelineNodes, rewindBranch, isLoading } = useMultiverse();
  const [selectedNodeId, setSelectedNodeId] = useState(timelineNodes[0]?.id || null);
  const [intention, setIntention] = useState('');

  const handleRewind = async () => {
    if (!selectedNodeId) return;
    await rewindBranch(selectedNodeId, intention);
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div
        className="glass-panel-elevated animate-fade-in"
        style={{
          maxWidth: '680px',
          width: '100%',
          borderRadius: '14px',
          padding: '2.2rem',
          border: '1px solid var(--border-cyan)',
          boxShadow: '0 0 45px var(--temporal-cyan-glow)'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <RotateCcw size={22} color="var(--temporal-cyan)" />
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', margin: 0 }}>
              SPACETIME REWIND CHRONOMETER
            </h2>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.4rem', borderRadius: '50%' }}>
            <X size={16} />
          </button>
        </div>

        {/* Multiverse Rule Explanation */}
        <div
          style={{
            padding: '1rem',
            borderRadius: '8px',
            background: 'rgba(34, 211, 238, 0.08)',
            border: '1px solid var(--border-cyan)',
            marginBottom: '1.5rem',
            fontSize: '0.88rem',
            lineHeight: 1.5,
            color: 'var(--text-primary)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--temporal-cyan)', fontWeight: 700, marginBottom: '0.3rem' }}>
            <AlertCircle size={15} />
            <span>Non-Destructive Multiverse Rule</span>
          </div>
          Returning to an earlier Kshan will create a <strong>brand new parallel reality fork</strong>. Your current reality branch will remain completely preserved and accessible in the multiverse tree.
        </div>

        {/* Historical Nodes List */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.6rem', display: 'block' }}>
            Select Historical Anchor Node:
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: '220px', overflowY: 'auto' }}>
            {timelineNodes.map((node, i) => {
              const isSelected = selectedNodeId === node.id;
              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNodeId(node.id)}
                  className="glass-card"
                  style={{
                    padding: '0.8rem 1rem',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    border: isSelected ? '1px solid var(--temporal-cyan)' : '1px solid var(--border-glass)',
                    background: isSelected ? 'rgba(34, 211, 238, 0.12)' : 'rgba(255, 255, 255, 0.02)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--temporal-cyan)', fontWeight: 700 }}>
                    <span>NODE #{node.depth_level ?? i} — {node.era_year || 'Origin Moment'}</span>
                  </div>
                  <p style={{ fontSize: '0.85rem', color: '#fff', marginTop: '0.2rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {node.story_text}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Intention Input */}
        <div style={{ marginBottom: '2rem' }}>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.4rem', display: 'block' }}>
            Rewind Intention (Optional):
          </label>
          <input
            type="text"
            value={intention}
            onChange={(e) => setIntention(e.target.value)}
            placeholder="e.g. Try a quiet infiltration instead of attacking..."
            style={{
              width: '100%',
              padding: '0.8rem 1rem',
              borderRadius: '6px',
              background: 'rgba(0, 0, 0, 0.5)',
              border: '1px solid var(--border-glass)',
              color: '#fff',
              outline: 'none',
              fontSize: '0.9rem'
            }}
          />
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
          <button onClick={onClose} className="btn-secondary">
            CANCEL
          </button>
          <button
            onClick={handleRewind}
            disabled={!selectedNodeId || isLoading}
            className="btn-primary"
            style={{
              background: 'linear-gradient(135deg, var(--temporal-cyan), var(--temporal-cyan-dark))',
              boxShadow: '0 0 20px var(--temporal-cyan-glow)'
            }}
          >
            <Compass size={16} />
            CREATE FORK REALITY
          </button>
        </div>
      </div>
    </div>
  );
}
