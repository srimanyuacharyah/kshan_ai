import React, { useState, useEffect } from 'react';
import { MultiverseProvider, useMultiverse } from './context/MultiverseContext';
import CosmicCanvas from './components/cinematic/CosmicCanvas';
import LandingHero from './components/cinematic/LandingHero';
import ScenarioSelector from './components/cinematic/ScenarioSelector';
import KshanNexus from './components/story/KshanNexus';
import AuthModal from './components/auth/AuthModal';
import LoadingState from './components/ui/LoadingState';
import ErrorState from './components/ui/ErrorState';

function MainExperience() {
  const { activeScenario, activeBranch, activeModal, setActiveModal } = useMultiverse();
  const [currentView, setCurrentView] = useState('hero'); // 'hero' | 'scenarios' | 'nexus'

  useEffect(() => {
    if (activeScenario && activeBranch) {
      setCurrentView('nexus');
    }
  }, [activeScenario, activeBranch]);

  return (
    <>
      <CosmicCanvas />
      
      {currentView === 'hero' && (
        <LandingHero onEnter={() => setCurrentView('scenarios')} />
      )}

      {currentView === 'scenarios' && (
        <ScenarioSelector onBack={() => setCurrentView('hero')} />
      )}

      {currentView === 'nexus' && (
        <KshanNexus onBackToScenarios={() => setCurrentView('scenarios')} />
      )}

      {activeModal === 'auth' && (
        <AuthModal onClose={() => setActiveModal(null)} />
      )}

      <LoadingState />
      <ErrorState />
    </>
  );
}

export default function App() {
  return (
    <MultiverseProvider>
      <MainExperience />
    </MultiverseProvider>
  );
}
