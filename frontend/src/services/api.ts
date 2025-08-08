import axios from 'axios';
import {
  Bounty,
  User,
  UserRegister,
  UserLogin,
  BountyCreate,
  BountyAccept,
  BountyClaim,
  BountyStatistics,
  PlatformStatistics,
  UserStatistics,
} from '../types/api';

const API_BASE_URL = 'http://18.222.139.25:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// User Management
export const userApi = {
  register: async (userData: UserRegister) => {
    const response = await api.post('/register', userData);
    return response.data;
  },

  login: async (userData: UserLogin) => {
    const response = await api.post('/login', userData);
    return response.data;
  },

  getUser: async (userId: number) => {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  },

  listUsers: async () => {
    const response = await api.get('/users');
    return response.data;
  },

  getUserStatistics: async (userId: number) => {
    const response = await api.get(`/users/${userId}/statistics`);
    return response.data;
  },

  updateBalance: async (userId: number, newBalance: number) => {
    const response = await api.put(`/users/${userId}/balance`, { new_balance: newBalance });
    return response.data;
  },

  fundWallet: async (userId: number) => {
    const response = await api.post(`/users/${userId}/fund`);
    return response.data;
  },
};

// Bounty Management
export const bountyApi = {
  createBounty: async (bountyData: BountyCreate) => {
    const response = await api.post('/bounties/', bountyData);
    return response.data;
  },

  listBounties: async () => {
    const response = await api.get('/bounties/');
    return response.data;
  },

  getBounty: async (bountyId: number) => {
    const response = await api.get(`/bounties/${bountyId}`);
    return response.data;
  },

  searchBounties: async (name?: string, githubUrl?: string) => {
    const params = new URLSearchParams();
    if (name) params.append('name', name);
    if (githubUrl) params.append('github_url', githubUrl);
    
    const response = await api.get(`/bounties/search/?${params.toString()}`);
    return response.data;
  },

  getBountiesByStatus: async (status: string) => {
    const response = await api.get(`/bounties/status/${status}`);
    return response.data;
  },

  getBountiesByFunder: async (funderId: number) => {
    const response = await api.get(`/bounties/funder/${funderId}`);
    return response.data;
  },

  getBountiesByDeveloper: async (developerAddress: string) => {
    const response = await api.get(`/bounties/developer/${developerAddress}`);
    return response.data;
  },

  acceptBounty: async (bountyId: number, acceptData: BountyAccept) => {
    const response = await api.post(`/bounties/${bountyId}/accept`, acceptData);
    return response.data;
  },

  claimBounty: async (bountyId: number, claimData: BountyClaim) => {
    const response = await api.post(`/bounties/${bountyId}/claim`, claimData);
    return response.data;
  },

  cancelBounty: async (bountyId: number) => {
    const response = await api.post(`/bounties/${bountyId}/cancel`);
    return response.data;
  },

  getBountyStatistics: async () => {
    const response = await api.get('/bounties/statistics');
    return response.data;
  },

  getPlatformStatistics: async (): Promise<PlatformStatistics> => {
    const response = await api.get('/platform/statistics');
    return response.data;
  },

  recalculateStatistics: async () => {
    const response = await api.post('/platform/statistics/recalculate');
    return response.data;
  },
};

export default api; 