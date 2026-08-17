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
    } catch (error) {
      console.error(`API Request Error [${endpoint}]:`, error);
      throw error;
    }
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
    const url = `${API_BASE_URL}/auth/register`;
    const safePayload = { ...payload, password: '[REDACTED]' };
    console.log("REGISTER REQUEST PAYLOAD:", safePayload);
    console.log("REGISTER REQUEST URL:", url);

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

export const api = new ApiClient();
