const TOKEN_KEY = 'sentinel_prime_token';
const USER_KEY = 'sentinel_prime_user';

function getApiBaseUrl() {
  if (typeof window === 'undefined') {
    return 'http://localhost:8000';
  }
  
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//${hostname}:8000`;
  }
  
  return `${protocol}//${hostname}:8000`;
}

const API_BASE_URL = getApiBaseUrl();

class ApiService {
  getToken() {
    if (typeof localStorage !== 'undefined') {
      return localStorage.getItem(TOKEN_KEY);
    }
    return null;
  }

  setToken(token) {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(TOKEN_KEY, token);
    }
  }

  clearToken() {
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
  }

  getUser() {
    if (typeof localStorage === 'undefined') return null;
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  }

  setUser(user) {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  }

  isAuthenticated() {
    return !!this.getToken();
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = this.getToken();
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      if (response.status === 401) {
        this.clearToken();
        if (typeof window !== 'undefined') {
          window.location.reload();
        }
        throw new Error('Unauthorized');
      }
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async register(username, password, email = null, fullName = null) {
    const data = await this.request('/auth/register', {
      method: 'POST',
      body: { username, password, email, full_name: fullName },
    });
    this.setToken(data.access_token);
    this.setUser(data.user);
    return data;
  }

  async login(username, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    this.setToken(data.access_token);
    this.setUser(data.user);
    return data;
  }

  async logout() {
    const token = this.getToken();
    if (token) {
      try {
        await this.request('/auth/logout', {
          method: 'POST',
          body: { token },
        });
      } catch (e) {
        console.error('Logout error:', e);
      }
    }
    this.clearToken();
  }

  async getMe() {
    return this.request('/auth/me');
  }

  async getDevices() {
    return this.request('/devices');
  }

  async getDevice(id) {
    return this.request(`/devices/${id}`);
  }

  async createDevice(device) {
    return this.request('/devices', {
      method: 'POST',
      body: device,
    });
  }

  async updateDevice(id, device) {
    return this.request(`/devices/${id}`, {
      method: 'PUT',
      body: device,
    });
  }

  async deleteDevice(id) {
    return this.request(`/devices/${id}`, {
      method: 'DELETE',
    });
  }

  async getDeviceByIp(ip) {
    return this.request(`/devices/by-ip/${ip}`);
  }

  async getDeviceByMac(mac) {
    return this.request(`/devices/by-mac/${mac}`);
  }

  async getScans() {
    return this.request('/scans');
  }

  async getScan(id) {
    return this.request(`/scans/${id}`);
  }

  async createScan(scan) {
    return this.request('/scans', {
      method: 'POST',
      body: scan,
    });
  }

  async updateScan(id, scan) {
    return this.request(`/scans/${id}`, {
      method: 'PUT',
      body: scan,
    });
  }

  async getAlerts(acknowledged = null) {
    let endpoint = '/alerts';
    if (acknowledged !== null) {
      endpoint += `?acknowledged=${acknowledged}`;
    }
    return this.request(endpoint);
  }

  async getAlert(id) {
    return this.request(`/alerts/${id}`);
  }

  async createAlert(alert) {
    return this.request('/alerts', {
      method: 'POST',
      body: alert,
    });
  }

  async acknowledgeAlert(id) {
    return this.request(`/alerts/${id}/acknowledge`, {
      method: 'PUT',
    });
  }

  async getHoneypotEvents() {
    return this.request('/honeypot/events');
  }

  async getHoneypotEvent(id) {
    return this.request(`/honeypot/events/${id}`);
  }

  async createHoneypotEvent(event) {
    return this.request('/honeypot/events', {
      method: 'POST',
      body: event,
    });
  }

  async getHealth() {
    return this.request('/health');
  }
}

export default new ApiService();
export { API_BASE_URL };
