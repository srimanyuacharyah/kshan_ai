import React, { useState } from 'react';
import { Sparkles, Send, X, AlertTriangle, Lightbulb, Compass, UserCheck } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';
import { api } from '../../services/api';

export default function FutureYouDrawer({ onClose }) {
  const { activeNode, activeBranch } = useMultiverse();
  const [messages, setMessages] = useState([
    {
      role: 'future_you',
      future_reflection: "I am speaking to you across twenty divergent years. Every choice you are making right now is sculpting the scars and victories I carry.",
      wisdom_shard: "Look not only at the immediate flame, but what it burns to ash.",
      warning: "Do not let haste overpower your discernment at this Kshan.",
      destiny_coherence: 0.88
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userText = inputMessage.trim();
    setInputMessage('');
    setMessages(prev => [...prev, { role: 'user', content: userText }]);
    setLoading(true);
    setError(null);

    try {
      const res = await api.generateFutureYou({
        message: userText,
        timeline_node_id: activeNode?.id,
        conversation_history: messages.map(m => ({
          speaker: m.role === 'user' ? 'Traveler' : 'Future You',
          message: m.role === 'user' ? m.content : m.future_reflection
        }))
      });

      const futureData = res.data;
      setMessages(prev => [
        ...prev,
        {
          role: 'future_you',
          future_reflection: futureData.future_reflection,
          wisdom_shard: futureData.wisdom_shard,
          warning: futureData.warning,
          destiny_coherence: futureData.destiny_coherence
        }
      ]);
    } catch (err) {
      setError(err.message || 'Transmission failed across the quantum gulf.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div
        className="glass-panel-elevated animate-fade-in"
        style={{
          maxWidth: '750px',
          width: '100%',
          borderRadius: '14px',
          padding: '2rem',
          border: '1px solid var(--border-gold)',
          boxShadow: '0 0 50px var(--starlight-gold-glow)',
          height: '85vh',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                background: 'rgba(247, 200, 115, 0.15)',
                border: '1px solid var(--border-gold)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <UserCheck size={18} color="var(--starlight-gold)" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff', margin: 0 }}>
                FUTURE YOU (T+20Y COMM LINK)
              </h2>
              <span style={{ fontSize: '0.72rem', color: 'var(--starlight-gold)' }}>
                Grounded via MCP Multiverse Vector Tensors
              </span>
            </div>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.4rem', borderRadius: '50%' }}>
            <X size={16} />
          </button>
        </div>

        {/* Conversation Stream */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '1.2rem',
            paddingRight: '0.4rem',
            marginBottom: '1.2rem'
          }}
        >
          {messages.map((m, idx) => {
            if (m.role === 'user') {
              return (
                <div
                  key={idx}
                  style={{
                    alignSelf: 'flex-end',
                    maxWidth: '75%',
                    padding: '0.9rem 1.2rem',
                    borderRadius: '12px 12px 2px 12px',
                    background: 'rgba(255, 255, 255, 0.08)',
                    color: '#fff',
                    fontSize: '0.92rem',
                    lineHeight: 1.5
                  }}
                >
                  {m.content}
                </div>
              );
            }

            return (
              <div
                key={idx}
                className="glass-card animate-fade-in"
                style={{
                  alignSelf: 'flex-start',
                  maxWidth: '90%',
                  padding: '1.2rem',
                  borderRadius: '12px 12px 12px 2px',
                  borderLeft: '4px solid var(--starlight-gold)',
                  background: 'rgba(247, 200, 115, 0.04)'
                }}
              >
                <p style={{ fontSize: '0.95rem', color: '#fff', lineHeight: 1.6, marginBottom: '0.8rem' }}>
                  "{m.future_reflection}"
                </p>

                {m.wisdom_shard && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--starlight-gold)', fontSize: '0.82rem', marginBottom: '0.4rem' }}>
                    <Lightbulb size={14} />
                    <span><strong>Wisdom Shard:</strong> {m.wisdom_shard}</span>
                  </div>
                )}

                {m.warning && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--entropy-crimson)', fontSize: '0.82rem' }}>
                    <AlertTriangle size={14} />
                    <span><strong>Warning:</strong> {m.warning}</span>
                  </div>
                )}
              </div>
            );
          })}

          {loading && (
            <div style={{ color: 'var(--starlight-gold)', fontSize: '0.85rem', fontStyle: 'italic' }}>
              ✦ Future consciousness tuning to current spacetime coordinates...
            </div>
          )}

          {error && (
            <div style={{ padding: '0.8rem', borderRadius: '6px', background: 'rgba(244, 63, 94, 0.1)', color: '#f43f5e', fontSize: '0.85rem' }}>
              {error}
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '0.6rem' }}>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask Future You about consequences, regrets, or wisdom..."
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
          <button type="submit" disabled={loading || !inputMessage.trim()} className="btn-primary">
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
