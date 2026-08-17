import React, { useState, useEffect } from 'react';
import { GitCompare, X, Activity, ArrowRight, ShieldCheck, Flame, Zap, Shield, Compass } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';
import { api } from '../../services/api';

export default function BranchCompareModal({ onClose }) {
  const { branchTree, activeBranch } = useMultiverse();
  const nodes = branchTree?.nodes || [];

  const [branchAId, setBranchAId] = useState(activeBranch?.id || nodes[0]?.branch_id || null);
  const [branchBId, setBranchBId] = useState(nodes[1]?.branch_id || nodes[0]?.branch_id || null);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchDiff() {
      if (!branchAId || !branchBId || branchAId === branchBId) {
        setComparisonResult(null);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const diff = await api.compareBranches(branchAId, branchBId);
        setComparisonResult(diff);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchDiff();
  }, [branchAId, branchBId]);

  return (
    <div className="modal-overlay">
      <div
        className="glass-panel-elevated animate-fade-in"
        style={{
          maxWidth: '850px',
          width: '100%',
          borderRadius: '14px',
          padding: '2.2rem',
          border: '1px solid var(--border-gold)',
          boxShadow: '0 0 50px var(--starlight-gold-glow)',
          maxHeight: '90vh',
          overflowY: 'auto'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.8rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <GitCompare size={22} color="var(--starlight-gold)" />
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', margin: 0 }}>
              MULTIVERSE REALITY COMPARISON MATRIX
            </h2>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.4rem', borderRadius: '50%' }}>
            <X size={16} />
          </button>
        </div>

        {/* Branch Selectors */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.2rem', marginBottom: '1.8rem' }}>
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.4rem', display: 'block' }}>
              Reality Branch Alpha (A):
            </label>
            <select
              value={branchAId || ''}
              onChange={(e) => setBranchAId(e.target.value)}
              style={{
                width: '100%',
                padding: '0.8rem',
                borderRadius: '6px',
                background: 'rgba(0, 0, 0, 0.6)',
                border: '1px solid var(--border-cyan)',
                color: 'var(--temporal-cyan)',
                fontWeight: 600
              }}
            >
              {nodes.map(n => (
                <option key={n.branch_id || n.id} value={n.branch_id || n.id}>
                  {n.label || n.branch_code} (Depth: {n.depth})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.4rem', display: 'block' }}>
              Reality Branch Beta (B):
            </label>
            <select
              value={branchBId || ''}
              onChange={(e) => setBranchBId(e.target.value)}
              style={{
                width: '100%',
                padding: '0.8rem',
                borderRadius: '6px',
                background: 'rgba(0, 0, 0, 0.6)',
                border: '1px solid var(--border-gold)',
                color: 'var(--starlight-gold)',
                fontWeight: 600
              }}
            >
              {nodes.map(n => (
                <option key={n.branch_id || n.id} value={n.branch_id || n.id}>
                  {n.label || n.branch_code} (Depth: {n.depth})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Comparison Output */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            Comparing timeline tensors...
          </div>
        )}

        {error && (
          <div style={{ padding: '1rem', borderRadius: '6px', background: 'rgba(244, 63, 94, 0.1)', color: '#f43f5e', border: '1px solid var(--entropy-crimson)' }}>
            {error}
          </div>
        )}

        {comparisonResult && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
            {/* Verdict Card */}
            <div
              style={{
                padding: '1rem',
                borderRadius: '8px',
                background: 'rgba(247, 200, 115, 0.08)',
                border: '1px solid var(--border-gold)',
                textAlign: 'center'
              }}
            >
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                Multiverse Divergence Verdict
              </span>
              <h3 style={{ fontSize: '1.2rem', color: 'var(--starlight-gold)', fontWeight: 800, marginTop: '0.2rem' }}>
                {comparisonResult.divergence_verdict}
              </h3>
            </div>

            {/* Differential Metrics Table */}
            <div className="glass-card" style={{ padding: '1.2rem', borderRadius: '8px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.08)', color: 'var(--text-muted)', textAlign: 'left' }}>
                    <th style={{ padding: '0.6rem' }}>State Metric</th>
                    <th style={{ padding: '0.6rem', color: 'var(--temporal-cyan)' }}>{comparisonResult.branch_a?.name}</th>
                    <th style={{ padding: '0.6rem', color: 'var(--starlight-gold)' }}>{comparisonResult.branch_b?.name}</th>
                    <th style={{ padding: '0.6rem' }}>Delta (B - A)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Flame size={14} color="var(--entropy-crimson)" /> Entropy
                    </td>
                    <td style={{ padding: '0.7rem' }}>{Math.round((comparisonResult.branch_a?.entropy || 0) * 100)}%</td>
                    <td style={{ padding: '0.7rem' }}>{Math.round((comparisonResult.branch_b?.entropy || 0) * 100)}%</td>
                    <td style={{ padding: '0.7rem', fontWeight: 700 }}>
                      {comparisonResult.metrics_differential?.entropy_delta > 0 ? `+${comparisonResult.metrics_differential?.entropy_delta * 100}%` : `${comparisonResult.metrics_differential?.entropy_delta * 100}%`}
                    </td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Zap size={14} color="var(--starlight-gold)" /> Resonance
                    </td>
                    <td style={{ padding: '0.7rem' }}>{Math.round((comparisonResult.branch_a?.resonance || 0) * 100)}%</td>
                    <td style={{ padding: '0.7rem' }}>{Math.round((comparisonResult.branch_b?.resonance || 0) * 100)}%</td>
                    <td style={{ padding: '0.7rem', fontWeight: 700 }}>
                      {comparisonResult.metrics_differential?.resonance_delta > 0 ? `+${comparisonResult.metrics_differential?.resonance_delta * 100}%` : `${comparisonResult.metrics_differential?.resonance_delta * 100}%`}
                    </td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Shield size={14} color="var(--quantum-violet)" /> Regret
                    </td>
                    <td style={{ padding: '0.7rem' }}>{Math.round((comparisonResult.branch_a?.regret || 0) * 100)}%</td>
                    <td style={{ padding: '0.7rem' }}>{Math.round((comparisonResult.branch_b?.regret || 0) * 100)}%</td>
                    <td style={{ padding: '0.7rem', fontWeight: 700 }}>
                      {comparisonResult.metrics_differential?.regret_delta > 0 ? `+${comparisonResult.metrics_differential?.regret_delta * 100}%` : `${comparisonResult.metrics_differential?.regret_delta * 100}%`}
                    </td>
                  </tr>
                  <tr>
                    <td style={{ padding: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Compass size={14} color="var(--temporal-cyan)" /> Destiny Shift
                    </td>
                    <td style={{ padding: '0.7rem' }}>{Math.round((comparisonResult.branch_a?.destiny_shift || 0) * 100)}%</td>
                    <td style={{ padding: '0.7rem' }}>{Math.round((comparisonResult.branch_b?.destiny_shift || 0) * 100)}%</td>
                    <td style={{ padding: '0.7rem', fontWeight: 700 }}>
                      {comparisonResult.metrics_differential?.destiny_shift_delta > 0 ? `+${comparisonResult.metrics_differential?.destiny_shift_delta * 100}%` : `${comparisonResult.metrics_differential?.destiny_shift_delta * 100}%`}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div style={{ marginTop: '2rem', textAlign: 'right' }}>
          <button onClick={onClose} className="btn-secondary">
            CLOSE MATRIX
          </button>
        </div>
      </div>
    </div>
  );
}
