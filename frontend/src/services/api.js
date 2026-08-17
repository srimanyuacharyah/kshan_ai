const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) ? import.meta.env.VITE_API_URL : '/api/v1';

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
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
    const token = this.getToken();

    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (response.status === 401) {
        // Token invalid or expired
        this.clearToken();
      }

      if (!response.ok) {
        let errorMessage = `HTTP Error ${response.status}`;
        try {
          const errData = await response.json();
          errorMessage = errData.detail || errData.message || errorMessage;
        } catch {
          // ignore json parse error
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Request Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // ---------------- AUTH ----------------
  async login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Login failed. Please check credentials.');
    }

    const data = await res.json();
    if (data.access_token) {
      this.setToken(data.access_token, true);
    }
    return data;
  }

  async register(email, password, fullName = 'Voyager') {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName })
    });
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

export const api = new ApiClient();
