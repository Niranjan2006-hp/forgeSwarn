import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const projectApi = {
  createProject: (data) => api.post('/projects', data),
  getProjects: () => api.get('/projects'),
  getProject: (id) => api.get(`/projects/${id}`),
  startProject: (id) => api.post(`/projects/${id}/start`),
  getAgents: (id) => api.get(`/projects/${id}/agents`),
  getEvents: (id) => api.get(`/projects/${id}/events`),
  getMessages: (id) => api.get(`/projects/${id}/messages`),
  getRequirements: (id) => api.get(`/projects/${id}/requirements`),
  addRequirement: (id, data) => api.post(`/projects/${id}/requirements`, data),
  getContract: (id) => api.get(`/projects/${id}/contract`),
  getArtifacts: (id) => api.get(`/projects/${id}/artifacts`),
  getArtifactContent: (id, filename) => api.get(`/projects/${id}/artifacts/${filename}`),
  getTests: (id) => api.get(`/projects/${id}/tests`),
  getBugs: (id) => api.get(`/projects/${id}/bugs`),
  getRepairs: (id) => api.get(`/projects/${id}/repairs`),
  getDecisions: (id) => api.get(`/projects/${id}/decisions`),
  getDeployment: (id) => api.get(`/projects/${id}/deployment`),
  approveGate: (id, approved, comment) => api.post(`/projects/${id}/approve`, { approved, comment }),
  stopProject: (id) => api.post(`/projects/${id}/stop`),
  getHealth: () => api.get('/health'),
};

export default api;
