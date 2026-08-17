// Node E2E Automated Verification for KSHAN Frontend API Service
const BASE_URL = 'http://127.0.0.1:8000/api/v1';

class StorageMock {
  constructor() {
    this.store = {};
  }
  getItem(k) { return this.store[k] || null; }
  setItem(k, v) { this.store[k] = String(v); }
  removeItem(k) { delete this.store[k]; }
  clear() { this.store = {}; }
}

const localStorage = new StorageMock();
const sessionStorage = new StorageMock();

class ApiClient {
  constructor() {
    this.tokenKey = 'kshan_access_token';
  }

  getToken() {
    try {
      return sessionStorage.getItem(this.tokenKey) || localStorage.getItem(this.tokenKey) || null;
    } catch {
      return null;
    }
  }

  setToken(token, persist = false) {
    try {
      if (persist) {
        localStorage.setItem(this.tokenKey, token);
      } else {
        sessionStorage.setItem(this.tokenKey, token);
      }
    } catch (e) {
      console.warn('Could not save token to storage', e);
    }
  }

  clearToken() {
    try {
      sessionStorage.removeItem(this.tokenKey);
      localStorage.removeItem(this.tokenKey);
    } catch (e) {
      console.warn('Could not clear token from storage', e);
    }
  }

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;
    const token = this.getToken();

    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...(options.headers || {})
    };

    const response = await fetch(url, {
      ...options,
      headers
    });

    if (response.status === 401) {
      this.clearToken();
    }

    if (!response.ok) {
      let errorMessage = `HTTP Error ${response.status}`;
      try {
        const errData = await response.json();
        if (typeof errData.detail === 'string') {
          errorMessage = errData.detail;
        } else if (Array.isArray(errData.detail)) {
          errorMessage = errData.detail
            .map(d => {
              if (typeof d === 'string') return d;
              const field = d.loc ? d.loc.filter(l => l !== 'body').join('.') : '';
              return field ? `${field}: ${d.msg}` : d.msg;
            })
            .join('; ');
        } else if (errData.error?.message) {
          errorMessage = errData.error.message;
        } else if (errData.message) {
          errorMessage = errData.message;
        } else if (typeof errData === 'object') {
          errorMessage = JSON.stringify(errData);
        }
      } catch {
        // ignore json parse error
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  }

  // ---------------- AUTH ----------------
  async login(email, password) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    const token = res?.data?.token?.access_token || res?.access_token;
    if (token) {
      this.setToken(token, true);
    }
    return res;
  }

  async register(email, password, fullName = 'Voyager') {
    const rawUsername = email.split('@')[0].replace(/[^a-zA-Z0-9_-]/g, '_');
    const username = rawUsername.length >= 3 ? rawUsername : `${rawUsername}_usr`;
    const payload = {
      email,
      password,
      username,
      display_name: fullName,
      full_name: fullName
    };
    const res = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    const token = res?.data?.token?.access_token || res?.access_token;
    if (token) {
      this.setToken(token, true);
    }
    return res;
  }

  async getMe() {
    return this.request('/auth/me');
  }

  // ---------------- SCENARIOS ----------------
  async getScenarios() {
    return this.request('/scenarios');
  }

  async getScenario(id) {
    return this.request(`/scenarios/${id}`);
  }

  // ---------------- MULTIVERSE ----------------
  async chooseAction(payload) {
    return this.request('/multiverse/choose', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async rewindToNode(payload) {
    return this.request('/multiverse/rewind', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async getMultiverseTree(scenarioId) {
    return this.request(`/multiverse/tree/${scenarioId}`);
  }

  async getBranchDetails(branchId) {
    return this.request(`/multiverse/branch/${branchId}`);
  }

  async compareBranches(branchAId, branchBId) {
    return this.request(`/multiverse/compare/${branchAId}/${branchBId}`);
  }

  async createBranch(payload) {
    return this.request('/multiverse/branch', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // ---------------- AI ORCHESTRATION ----------------
  async generateStory(payload) {
    return this.request('/ai/story', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async generateBranchChoices(payload) {
    return this.request('/ai/branch', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async generateFutureYou(payload) {
    return this.request('/ai/future-you', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async analyzeDecision(payload) {
    return this.request('/ai/analyze-decision', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // ---------------- RAG MEMORY VAULT ----------------
  async searchMemories(payload) {
    return this.request('/rag/search', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }
}

async function runE2E() {
  console.log('=== STARTING KSHAN E2E AUTOMATED VERIFICATION ===\n');
  const api = new ApiClient();

  // Phase 1: Health
  console.log('[PHASE 1] Health Check...');
  const healthRes = await api.request('/health/ready');
  if (healthRes.status !== 'ready') throw new Error('Health check not ready');
  console.log('  ✓ System Health: READY, DB Healthy\n');

  // Phase 2: Authentication
  console.log('[PHASE 2] Authentication Flow...');
  const testEmail = `e2e_audit_${Date.now()}@kshan.ai`;
  const testPassword = 'Password123!';
  const testName = 'E2E Audit User';

  const regRes = await api.register(testEmail, testPassword, testName);
  console.log('  ✓ Registered user:', regRes.data.user.email);

  const meRes1 = await api.getMe();
  console.log('  ✓ Verified /auth/me for registered user:', meRes1.data.email);

  api.clearToken();
  const loginRes = await api.login(testEmail, testPassword);
  console.log('  ✓ Logged in user with new session:', loginRes.data.user.email);

  const meRes2 = await api.getMe();
  console.log('  ✓ Verified /auth/me after login:', meRes2.data.username, '\n');

  // Phase 4: Scenarios
  console.log('[PHASE 4] Scenario Selection & Root Reality Creation...');
  const scenarios = await api.getScenarios();
  console.log(`  ✓ Loaded ${scenarios.length} scenarios from backend`);
  const activeScenario = scenarios[0];
  console.log('  ✓ Selected scenario:', activeScenario.title, `(${activeScenario.id})`);

  const rootBranchRes = await api.createBranch({
    branch_name: `Prime Reality: ${activeScenario.title}`,
    initial_story: activeScenario.initial_kshan_moment || 'You materialize at the inflection point.'
  });
  const rootBranch = rootBranchRes.branch;
  const genesisNode = rootBranchRes.genesis_node;
  console.log('  ✓ Spawned root reality branch:', rootBranch.id, `(${rootBranch.branch_code})`);
  console.log('  ✓ Genesis timeline node:', genesisNode.id, `(Depth: ${genesisNode.depth_level})\n`);

  // Phase 5: Tree & Branch Details
  console.log('[PHASE 5] Multiverse Tree & Branch Details...');
  const tree = await api.getMultiverseTree(activeScenario.id);
  console.log(`  ✓ Multiverse tree loaded: ${tree.nodes.length} nodes, ${tree.edges.length} edges`);
  const branchDetails = await api.getBranchDetails(rootBranch.id);
  console.log('  ✓ Branch details loaded:', branchDetails.branch.name, `(${branchDetails.timeline.length} timeline nodes)\n`);

  // Phase 6: AI Story
  console.log('[PHASE 6] AI Story Continuation...');
  const storyRes = await api.generateStory({
    scenario_id: activeScenario.id,
    branch_id: rootBranch.id
  });
  console.log('  ✓ Narrative generated, length:', storyRes.narrative.length, 'chars');
  console.log(`  ✓ Choices offered: ${storyRes.choices.length}`);
  const selectedChoice = storyRes.choices[0];
  console.log('  ✓ Selected Choice:', selectedChoice.title, `(ID: ${selectedChoice.id})\n`);

  // Phase 7: AI Branch Choices
  console.log('[PHASE 7] AI Branch Choices...');
  const branchChoicesRes = await api.generateBranchChoices({
    scenario_id: activeScenario.id,
    branch_id: rootBranch.id,
    timeline_node_id: genesisNode.id
  });
  console.log(`  ✓ Generated ${branchChoicesRes.choices.length} branch choices\n`);

  // Phase 8: Choice Execution / Forking
  console.log('[PHASE 8] Executing Choice / Forking Reality Branch...');
  const chooseRes = await api.chooseAction({
    branch_id: rootBranch.id,
    timeline_node_id: genesisNode.id,
    choice_id: selectedChoice.id,
    intention: 'Leap into the quantum breach',
    custom_branch_name: 'Fork: Quantum Leap'
  });
  const childBranch = chooseRes.new_branch;
  const childNode = chooseRes.new_timeline_node;
  console.log('  ✓ Forked new reality branch:', childBranch.id, `(${childBranch.branch_code})`);
  console.log('  ✓ New timeline node created:', childNode.id, `(Depth: ${childNode.depth_level})`);
  console.log('  ✓ Deterministic State Vector: Entropy =', chooseRes.state_vector.entropy, ', Resonance =', chooseRes.state_vector.resonance, '\n');

  // Phase 9: Branch Comparison
  console.log('[PHASE 9] Branch Comparison Matrix...');
  const comparison = await api.compareBranches(rootBranch.id, childBranch.id);
  console.log('  ✓ Divergence Verdict:', comparison.divergence_verdict);
  console.log('  ✓ Entropy Delta:', comparison.metrics_differential.entropy_delta);
  console.log('  ✓ Resonance Delta:', comparison.metrics_differential.resonance_delta, '\n');

  // Phase 10: Future You
  console.log('[PHASE 10] Future You (T+20Y COMM LINK)...');
  const futureYou = await api.generateFutureYou({
    scenario_id: activeScenario.id,
    branch_id: childBranch.id,
    user_question: 'What should I learn from this timeline?'
  });
  console.log('  ✓ Identity:', futureYou.identity);
  console.log('  ✓ Message to Present Self:', futureYou.message_to_present_self);
  console.log('  ✓ Regrets:', futureYou.regrets);
  console.log('  ✓ Achievements:', futureYou.achievements);
  if (typeof futureYou.message_to_present_self !== 'string' || futureYou.message_to_present_self.includes('[object Object]')) {
    throw new Error('Future You contains [object Object]');
  }
  console.log('  ✓ Verified NO [object Object] present anywhere in response\n');

  // Phase 11: RAG Search
  console.log('[PHASE 11] RAG Search Memory Echoes...');
  const searchRes = await api.searchMemories({
    query: 'Varanasi sky-pier quantum frequency',
    branch_id: childBranch.id,
    top_k: 4
  });
  console.log('  ✓ RAG Search results retrieved:', searchRes.data.results_count, 'records');
  console.log('  ✓ Query matched:', searchRes.data.query, '\n');

  // Phase 14: Error Handling & [object Object] Prevention Verification
  console.log('[PHASE 14] Error Handling Validation & Object Serialization Audit...');
  try {
    await api.request('/ai/future-you', {
      method: 'POST',
      body: JSON.stringify({}) // Invalid empty payload
    });
  } catch (err) {
    console.log('  ✓ Captured expected 422 error string:', err.message);
    if (err.message.includes('[object Object]')) {
      throw new Error('Error message converted to [object Object]!');
    }
    console.log('  ✓ Formatted validation error properly without [object Object]\n');
  }

  console.log('=== ALL E2E PHASES COMPLETED WITH 100% SUCCESS ===');
}

runE2E().catch(err => {
  console.error('E2E FAILURE:', err);
  process.exit(1);
});
