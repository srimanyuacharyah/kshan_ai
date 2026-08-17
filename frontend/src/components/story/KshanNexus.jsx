import React, { useState, useEffect } from 'react';
import {
  RotateCcw, GitCompare, Database, UserCheck, Globe, Users,
  ArrowLeft, Sparkles, BookOpen, Clock, Activity, LogOut
} from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';
import StateHUD from '../ui/StateHUD';
import ChoiceCards from './ChoiceCards';
import TimelineCanvas from '../timeline/TimelineCanvas';
import AudioController from '../ui/AudioController';
import RewindModal from '../timeline/RewindModal';
import BranchCompareModal from '../multiverse/BranchCompareModal';
import MemoryVault from '../memory/MemoryVault';
import FutureYouDrawer from '../assistant/FutureYouDrawer';
import WorldExplorer from '../world/WorldExplorer';
import CharacterConstellation from '../characters/CharacterConstellation';
import ButterflySequence from './ButterflySequence';

export default function KshanNexus({ onBackToScenarios }) {
  const {
    activeScenario,
    activeBranch,
    activeNode,
    timelineNodes,
    user,
    logout,
    activeModal,
    setActiveModal
  } = useMultiverse();

  // Typewriter effect for latest node story
  const fullText = activeNode?.story_text || activeScenario?.initial_kshan_moment || "You stand at the threshold of the multiverse.";
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    let index = 0;
    setDisplayedText('');
    const interval = setInterval(() => {
      index++;
      setDisplayedText(fullText.slice(0, index));
      if (index >= fullText.length) {
        clearInterval(interval);
      }
    }, 14);

    return () => clearInterval(interval);
  }, [fullText]);

  return (
    <div
      style={{
        minHeight: '100vh',
        padding: '1.5rem 2rem',
        position: 'relative',
        zIndex: 1,
        maxWidth: '1600px',
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem'
      }}
    >
      {/* Top Navigation Bar */}
      <header
        className="glass-panel"
        style={{
          borderRadius: '10px',
          padding: '0.8rem 1.4rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button onClick={onBackToScenarios} className="btn-secondary" style={{ padding: '0.5rem 0.9rem', fontSize: '0.8rem' }}>
            <ArrowLeft size={15} />
            <span>EXIT SCENARIO</span>
          </button>
          <div>
            <h1 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff', margin: 0 }}>
              <span className="gold-gradient-text">KSHAN</span> • {activeScenario?.title?.toUpperCase()}
            </h1>
            <span style={{ fontSize: '0.72rem', color: 'var(--temporal-cyan)' }}>
              Branch: {activeBranch?.branch_code || 'PRIME'} • Depth Level: {activeNode?.depth_level ?? 0}
            </span>
          </div>
        </div>

        {/* Right Tools Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
          <button
            onClick={() => setActiveModal('future_you')}
            className="btn-secondary"
            style={{
              padding: '0.5rem 0.9rem',
              fontSize: '0.8rem',
              border: '1px solid var(--border-gold)',
              color: 'var(--starlight-gold)'
            }}
          >
            <UserCheck size={14} />
            <span>FUTURE YOU</span>
          </button>

          <button
            onClick={() => setActiveModal('rewind')}
            className="btn-secondary"
            style={{
              padding: '0.5rem 0.9rem',
              fontSize: '0.8rem',
              border: '1px solid var(--border-cyan)',
              color: 'var(--temporal-cyan)'
            }}
          >
            <RotateCcw size={14} />
            <span>REWIND</span>
          </button>

          <button
            onClick={() => setActiveModal('compare')}
            className="btn-secondary"
            style={{ padding: '0.5rem 0.9rem', fontSize: '0.8rem' }}
          >
            <GitCompare size={14} />
            <span>DIFF</span>
          </button>

          <AudioController />

          {/* User profile */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginLeft: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {user?.full_name || 'Voyager'}
            </span>
            <button
              onClick={logout}
              className="btn-secondary"
              style={{ padding: '0.4rem', borderRadius: '50%' }}
              title="Logout"
            >
              <LogOut size={13} />
            </button>
          </div>
        </div>
      </header>

      {/* Main 3-Column Studio Grid */}
      <main
        style={{
          display: 'grid',
          gridTemplateColumns: '320px 1fr 340px',
          gap: '1.5rem',
          flex: 1
        }}
      >
        {/* Left Column: Timeline Tree Canvas */}
        <aside style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <TimelineCanvas />
        </aside>

        {/* Center Column: Narrative Prose & Choice Cards */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Story Prose Card */}
          <div
            className="glass-panel"
            style={{
              borderRadius: '12px',
              padding: '2.2rem',
              minHeight: '280px',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              position: 'relative'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.2rem' }}>
              <span
                style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  letterSpacing: '0.12em',
                  textTransform: 'uppercase',
                  color: 'var(--starlight-gold)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem'
                }}
              >
                <Sparkles size={14} />
                REALITY UNFOLDING — KSHAN #{activeNode?.depth_level ?? 0}
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {activeNode?.era_year || 'Current Era'}
              </span>
            </div>

            {/* Prose Text */}
            <p
              style={{
                fontSize: '1.15rem',
                lineHeight: 1.8,
                color: '#f8fafc',
                fontFamily: 'var(--font-body)',
                whiteSpace: 'pre-line'
              }}
            >
              {displayedText}
              <span style={{ animation: 'pulse-slow 1s infinite', color: 'var(--starlight-gold)' }}> ▍</span>
            </p>

            {/* Sensory Ambiance Note */}
            {activeScenario?.sensory_ambiance && (
              <div
                style={{
                  marginTop: '1.8rem',
                  padding: '0.8rem 1rem',
                  borderRadius: '6px',
                  background: 'rgba(255, 255, 255, 0.02)',
                  borderLeft: '3px solid var(--border-gold)',
                  fontSize: '0.82rem',
                  fontStyle: 'italic',
                  color: 'var(--text-secondary)'
                }}
              >
                ✦ Ambiance: {activeScenario.sensory_ambiance}
              </div>
            )}
          </div>

          {/* Choice Cards */}
          <ChoiceCards choices={activeNode?.choices || []} />
        </section>

        {/* Right Column: 7D State HUD & Multiverse Drawers */}
        <aside style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
          <StateHUD />

          {/* Multiverse Tools Panels */}
          <div
            className="glass-panel"
            style={{
              borderRadius: '12px',
              padding: '1.2rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.6rem'
            }}
          >
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              Multiverse Shards & Atlas
            </span>

            <button
              onClick={() => setActiveModal('memories')}
              className="btn-secondary"
              style={{ width: '100%', justifyContent: 'flex-start', padding: '0.75rem' }}
            >
              <Database size={15} color="var(--temporal-cyan)" />
              <span>RAG Memory Vault</span>
            </button>

            <button
              onClick={() => setActiveModal('characters')}
              className="btn-secondary"
              style={{ width: '100%', justifyContent: 'flex-start', padding: '0.75rem' }}
            >
              <Users size={15} color="var(--quantum-violet)" />
              <span>Character Constellation</span>
            </button>

            <button
              onClick={() => setActiveModal('world')}
              className="btn-secondary"
              style={{ width: '100%', justifyContent: 'flex-start', padding: '0.75rem' }}
            >
              <Globe size={15} color="var(--starlight-gold)" />
              <span>World Atlas</span>
            </button>
          </div>
        </aside>
      </main>

      {/* Dynamic Overlays & Modals */}
      {activeModal === 'rewind' && <RewindModal onClose={() => setActiveModal(null)} />}
      {activeModal === 'compare' && <BranchCompareModal onClose={() => setActiveModal(null)} />}
      {activeModal === 'memories' && <MemoryVault onClose={() => setActiveModal(null)} />}
      {activeModal === 'future_you' && <FutureYouDrawer onClose={() => setActiveModal(null)} />}
      {activeModal === 'world' && <WorldExplorer onClose={() => setActiveModal(null)} />}
      {activeModal === 'characters' && <CharacterConstellation onClose={() => setActiveModal(null)} />}

      {/* 4-Tier Butterfly Ripple Sequence */}
      <ButterflySequence />
    </div>
  );
}
