import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { audioEngine } from '../services/audioEngine';

const MultiverseContext = createContext(null);

export function MultiverseProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);

  // Gameplay State
  const [scenarios, setScenarios] = useState([]);
  const [activeScenario, setActiveScenario] = useState(null);
  const [activeBranch, setActiveBranch] = useState(null);
  const [activeNode, setActiveNode] = useState(null);
  const [timelineNodes, setTimelineNodes] = useState([]);
  const [branchTree, setBranchTree] = useState({ nodes: [], edges: [] });
  const [stateVector, setStateVector] = useState({
    entropy: 0.10,
    resonance: 0.70,
    regret: 0.00,
    destiny_shift: 0.00,
    world_stability: 0.85,
    social_stability: 0.80,
    technology_level: 0.50
  });

  // Modals & Overlays
  const [activeModal, setActiveModal] = useState(null); // 'rewind' | 'compare' | 'memories' | 'future_you' | 'world' | 'characters' | 'auth'
  const [compareBranchesData, setCompareBranchesData] = useState({ branchAId: null, branchBId: null });
  const [butterflyRipple, setButterflyRipple] = useState(null);

  // Loading & Error States
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('Reconstructing reality...');
  const [error, setError] = useState(null);

  // Check auth session on startup
  useEffect(() => {
    async function checkAuth() {
      const token = api.getToken();
      if (token) {
        try {
          const userData = await api.getMe();
          setUser(userData);
          setIsAuthenticated(true);
        } catch {
          api.clearToken();
          setIsAuthenticated(false);
        }
      }
      setAuthLoading(false);
    }
    checkAuth();
  }, []);

  // Fetch scenarios on mount
  useEffect(() => {
    async function fetchScenarios() {
      try {
        const scList = await api.getScenarios();
        setScenarios(scList);
      } catch (err) {
        console.warn('Could not load scenarios from API, fallback to default seed', err);
      }
    }
    fetchScenarios();
  }, []);

  // Auth Handlers
  const login = useCallback(async (email, password) => {
    setIsLoading(true);
    setLoadingMessage('Authenticating traveler consciousness...');
    try {
      const authRes = await api.login(email, password);
      const me = await api.getMe();
      setUser(me);
      setIsAuthenticated(true);
      setActiveModal(null);
      setError(null);
      return me;
    } catch (err) {
      setError(err.message || 'Login failed.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (email, password, fullName) => {
    setIsLoading(true);
    setLoadingMessage('Binding new quantum soul signature...');
    try {
      await api.register(email, password, fullName);
      return await login(email, password);
    } catch (err) {
      setError(err.message || 'Registration failed.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [login]);

  const logout = useCallback(() => {
    api.clearToken();
    setUser(null);
    setIsAuthenticated(false);
    setActiveBranch(null);
    setActiveNode(null);
    setTimelineNodes([]);
  }, []);

  // Select a scenario & initialize or restore active reality
  const selectScenario = useCallback(async (scenario) => {
    setActiveScenario(scenario);
    setIsLoading(true);
    setLoadingMessage(`Materializing reality for ${scenario.title}...`);
    audioEngine.playChime();

    try {
      if (!isAuthenticated) {
        setActiveModal('auth');
        setIsLoading(false);
        return;
      }

      // Check existing tree or create root reality
      const treeData = await api.getMultiverseTree(scenario.id).catch(() => ({ nodes: [], edges: [] }));
      setBranchTree(treeData);

      if (treeData.nodes && treeData.nodes.length > 0) {
        // Load latest active branch
        const latest = treeData.nodes[treeData.nodes.length - 1];
        await loadBranchDetails(latest.branch_id);
      } else {
        // Create brand new root branch for this scenario
        const branchRes = await api.createBranch({
          branch_name: `Prime Reality: ${scenario.title}`,
          initial_story: scenario.initial_kshan_moment || "You materialize at the inflection point."
        });
        const rootBranch = branchRes.branch;
        const genesisNode = branchRes.genesis_node;
        setActiveBranch(rootBranch);
        setActiveNode(genesisNode);
        setTimelineNodes([genesisNode]);
        setStateVector({
          entropy: rootBranch.entropy,
          resonance: rootBranch.resonance,
          regret: 0.00,
          destiny_shift: 0.00,
          world_stability: 0.85,
          social_stability: 0.80,
          technology_level: 0.50
        });
        await loadTree(scenario.id);
      }
    } catch (err) {
      console.error('Error starting scenario:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  const loadTree = useCallback(async (scenarioId) => {
    if (!scenarioId) return;
    try {
      const tree = await api.getMultiverseTree(scenarioId);
      setBranchTree(tree);
    } catch (e) {
      console.warn('Could not load tree:', e);
    }
  }, []);

  const loadBranchDetails = useCallback(async (branchId) => {
    setIsLoading(true);
    setLoadingMessage('Loading timeline branch coordinates...');
    try {
      const details = await api.getBranchDetails(branchId);
      const b = details.branch;
      setActiveBranch(b);
      setTimelineNodes(details.timeline || []);
      if (details.timeline && details.timeline.length > 0) {
        setActiveNode(details.timeline[details.timeline.length - 1]);
      }
      setStateVector({
        entropy: b.entropy,
        resonance: b.resonance,
        regret: b.regret,
        destiny_shift: b.destiny_shift,
        world_stability: details.state?.state_variables?.world_stability ?? 0.85,
        social_stability: details.state?.state_variables?.social_stability ?? 0.80,
        technology_level: details.state?.state_variables?.technology_level ?? 0.50
      });
      audioEngine.playChime();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Execute a choice at current timeline node
  const executeChoice = useCallback(async (choice, intention = null) => {
    if (!activeBranch || !activeNode) return;
    setIsLoading(true);
    setLoadingMessage('Calculating butterfly effect & divergent state...');
    audioEngine.playChoicePulse();

    try {
      const payload = {
        branch_id: activeBranch.id,
        timeline_node_id: activeNode.id,
        choice_id: choice.id || choice.choice_id,
        intention: intention || choice.choice_label,
        custom_branch_name: `Divergence: ${choice.choice_label?.slice(0, 30)}`
      };

      const res = await api.chooseAction(payload);
      const newB = res.new_branch;
      const newN = res.new_timeline_node;

      setActiveBranch(newB);
      setActiveNode(newN);
      setTimelineNodes(prev => [...prev, newN]);

      if (res.state_vector) {
        setStateVector(res.state_vector);
      }

      // Show butterfly ripple modal
      if (res.butterfly_ripple) {
        setButterflyRipple(res.butterfly_ripple);
      }

      if (activeScenario) {
        await loadTree(activeScenario.id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [activeBranch, activeNode, activeScenario, loadTree]);

  // Rewind to historical node
  const rewindBranch = useCallback(async (historicalNodeId, rewindIntention = null) => {
    setIsLoading(true);
    setLoadingMessage('Folding timeline spacetime coordinates...');
    audioEngine.playRewindWarp();

    try {
      const res = await api.rewindToNode({
        historical_node_id: historicalNodeId,
        rewind_intention: rewindIntention
      });

      const forkBranch = res.fork_branch;
      setActiveModal(null);
      await loadBranchDetails(forkBranch.id);
      if (activeScenario) {
        await loadTree(activeScenario.id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [activeScenario, loadBranchDetails, loadTree]);

  return (
    <MultiverseContext.Provider
      value={{
        user,
        isAuthenticated,
        authLoading,
        scenarios,
        activeScenario,
        activeBranch,
        activeNode,
        timelineNodes,
        branchTree,
        stateVector,
        activeModal,
        compareBranchesData,
        butterflyRipple,
        isLoading,
        loadingMessage,
        error,
        login,
        register,
        logout,
        selectScenario,
        executeChoice,
        rewindBranch,
        loadBranchDetails,
        loadTree,
        setActiveModal,
        setCompareBranchesData,
        setButterflyRipple,
        setError
      }}
    >
      {children}
    </MultiverseContext.Provider>
  );
}

export function useMultiverse() {
  const ctx = useContext(MultiverseContext);
  if (!ctx) {
    throw new Error('useMultiverse must be used within a MultiverseProvider');
  }
  return ctx;
}
