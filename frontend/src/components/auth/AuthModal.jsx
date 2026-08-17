import React, { useState } from 'react';
import { Lock, Mail, User, X, Sparkles, LogIn, UserPlus } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';

export default function AuthModal({ onClose }) {
  const { login, register, isLoading } = useMultiverse();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [authError, setAuthError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAuthError(null);

    try {
      if (isRegister) {
        await register(email, password, fullName || 'Traveler');
      } else {
        await login(email, password);
      }
      onClose();
    } catch (err) {
      setAuthError(err.message || 'Authentication failed. Please check credentials.');
    }
  };

  return (
    <div className="modal-overlay">
      <div
        className="glass-panel-elevated animate-fade-in"
        style={{
          maxWidth: '440px',
          width: '100%',
          borderRadius: '14px',
          padding: '2.2rem',
          border: '1px solid var(--border-gold)',
          boxShadow: '0 0 50px var(--starlight-gold-glow)'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={20} color="var(--starlight-gold)" />
            <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#fff', margin: 0 }}>
              {isRegister ? 'QUANTUM REGISTRATION' : 'TRAVELER LOGIN'}
            </h2>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.4rem', borderRadius: '50%' }}>
            <X size={16} />
          </button>
        </div>

        {/* Tab switcher */}
        <div
          style={{
            display: 'flex',
            borderRadius: '6px',
            background: 'rgba(0, 0, 0, 0.4)',
            padding: '0.3rem',
            marginBottom: '1.5rem',
            border: '1px solid var(--border-glass)'
          }}
        >
          <button
            type="button"
            onClick={() => { setIsRegister(false); setAuthError(null); }}
            style={{
              flex: 1,
              padding: '0.6rem',
              borderRadius: '4px',
              border: 'none',
              cursor: 'pointer',
              background: !isRegister ? 'rgba(247, 200, 115, 0.15)' : 'transparent',
              color: !isRegister ? 'var(--starlight-gold)' : 'var(--text-muted)',
              fontWeight: 600,
              fontSize: '0.82rem'
            }}
          >
            SIGN IN
          </button>
          <button
            type="button"
            onClick={() => { setIsRegister(true); setAuthError(null); }}
            style={{
              flex: 1,
              padding: '0.6rem',
              borderRadius: '4px',
              border: 'none',
              cursor: 'pointer',
              background: isRegister ? 'rgba(247, 200, 115, 0.15)' : 'transparent',
              color: isRegister ? 'var(--starlight-gold)' : 'var(--text-muted)',
              fontWeight: 600,
              fontSize: '0.82rem'
            }}
          >
            NEW TRAVELER
          </button>
        </div>

        {authError && (
          <div
            style={{
              padding: '0.8rem',
              borderRadius: '6px',
              background: 'rgba(244, 63, 94, 0.1)',
              color: '#f43f5e',
              border: '1px solid var(--entropy-crimson)',
              fontSize: '0.85rem',
              marginBottom: '1.2rem'
            }}
          >
            {authError}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {isRegister && (
            <div>
              <label style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.4rem', display: 'block' }}>
                Full Name / Alias:
              </label>
              <div style={{ position: 'relative' }}>
                <User size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '12px' }} />
                <input
                  type="text"
                  required={isRegister}
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Srimanyu Vance"
                  style={{
                    width: '100%',
                    padding: '0.75rem 1rem 0.75rem 2.4rem',
                    borderRadius: '6px',
                    background: 'rgba(0, 0, 0, 0.6)',
                    border: '1px solid var(--border-glass)',
                    color: '#fff',
                    outline: 'none',
                    fontSize: '0.9rem'
                  }}
                />
              </div>
            </div>
          )}

          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.4rem', display: 'block' }}>
              Email Address:
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '12px' }} />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="voyager@kshan.ai"
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem 0.75rem 2.4rem',
                  borderRadius: '6px',
                  background: 'rgba(0, 0, 0, 0.6)',
                  border: '1px solid var(--border-glass)',
                  color: '#fff',
                  outline: 'none',
                  fontSize: '0.9rem'
                }}
              />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.4rem', display: 'block' }}>
              Secret Passkey:
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '12px' }} />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem 0.75rem 2.4rem',
                  borderRadius: '6px',
                  background: 'rgba(0, 0, 0, 0.6)',
                  border: '1px solid var(--border-glass)',
                  color: '#fff',
                  outline: 'none',
                  fontSize: '0.9rem'
                }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', marginTop: '0.8rem', padding: '0.9rem' }}
          >
            {isRegister ? <UserPlus size={16} /> : <LogIn size={16} />}
            {isRegister ? 'CREATE QUANTUM SIGNATURE' : 'AUTHENTICATE ACCESS'}
          </button>
        </form>
      </div>
    </div>
  );
}
