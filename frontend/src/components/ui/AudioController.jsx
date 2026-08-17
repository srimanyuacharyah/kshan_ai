import React, { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import { audioEngine } from '../../services/audioEngine';

export default function AudioController() {
  const [isMuted, setIsMuted] = useState(audioEngine.isMuted);

  const handleToggle = () => {
    const nextMuted = audioEngine.toggleMute();
    setIsMuted(nextMuted);
    if (!nextMuted) {
      audioEngine.startAmbientDrone();
    }
  };

  return (
    <button
      onClick={handleToggle}
      className="btn-secondary"
      style={{
        padding: '0.5rem 0.9rem',
        fontSize: '0.8rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.4rem',
        borderRadius: '20px',
        border: '1px solid var(--border-gold)'
      }}
      title={isMuted ? 'Unmute Ambient Sound' : 'Mute Ambient Sound'}
      aria-label={isMuted ? 'Unmute Ambient Sound' : 'Mute Ambient Sound'}
    >
      {isMuted ? (
        <>
          <VolumeX size={15} color="var(--text-muted)" />
          <span style={{ color: 'var(--text-muted)' }}>SOUND OFF</span>
        </>
      ) : (
        <>
          <Volume2 size={15} color="var(--starlight-gold)" />
          <span style={{ color: 'var(--starlight-gold)' }}>SOUND ON</span>
        </>
      )}
    </button>
  );
}
