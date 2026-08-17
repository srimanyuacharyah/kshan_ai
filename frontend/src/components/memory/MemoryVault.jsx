import React, { useState } from 'react';
import { Database, Search, X, Sparkles, BookOpen, Layers } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';
import { api } from '../../services/api';

export default function MemoryVault({ onClose }) {
  const { activeBranch } = useMultiverse();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await api.searchMemories({
        query: query.trim(),
        branch_id: activeBranch?.id,
        top_k: 5
      });
      setResults(res.data?.results || []);
    } catch (err) {
      setError(err.message || 'Could not retrieve memory echoes.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div
        className="glass-panel-elevated animate-fade-in"
        style={{
          maxWidth: '800px',
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
            <Database size={22} color="var(--temporal-cyan)" />
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', margin: 0 }}>
              KSHAN RAG MEMORY VAULT
            </h2>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.4rem', borderRadius: '50%' }}>
            <X size={16} />
          </button>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.8rem', marginBottom: '1.8rem' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search memory shards across timelines... (e.g. 'Why does Aria distrust me?')"
            style={{
              flex: 1,
              padding: '0.85rem 1.2rem',
              borderRadius: '6px',
              background: 'rgba(0, 0, 0, 0.6)',
              border: '1px solid var(--border-glass)',
              color: '#fff',
              outline: 'none',
              fontSize: '0.92rem'
            }}
          />
          <button type="submit" disabled={loading} className="btn-primary">
            <Search size={16} />
            RECALL
          </button>
        </form>

        {loading && (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            Scanning pgvector cosine memory shards...
          </div>
        )}

        {error && (
          <div style={{ padding: '1rem', borderRadius: '6px', background: 'rgba(244, 63, 94, 0.1)', color: '#f43f5e', marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        {/* Results List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {results.map((item, idx) => (
            <div
              key={idx}
              className="glass-card"
              style={{
                padding: '1.2rem',
                borderRadius: '8px',
                borderLeft: '3px solid var(--temporal-cyan)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--temporal-cyan)', textTransform: 'uppercase' }}>
                  {item.document_type || 'Memory Echo'}
                </span>
                <span
                  style={{
                    fontSize: '0.7rem',
                    padding: '0.15rem 0.5rem',
                    borderRadius: '4px',
                    background: 'rgba(34, 211, 238, 0.1)',
                    color: 'var(--temporal-cyan)'
                  }}
                >
                  Match: {Math.round(item.score * 100)}%
                </span>
              </div>
              <p style={{ fontSize: '0.92rem', color: '#fff', lineHeight: 1.5 }}>
                {item.content}
              </p>
            </div>
          ))}

          {results.length === 0 && !loading && !error && (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
              <Layers size={36} style={{ opacity: 0.3, marginBottom: '0.8rem' }} />
              <p>Type an inquiry above to semantically query memories and timeline echoes.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
