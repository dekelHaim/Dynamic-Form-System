import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

const formService = {
  submitForm: async (data) => {
    try {
      const response = await api.post('/submissions/submit', { data });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // Get submissions with pagination and filtering
  getSubmissions: async (options = {}) => {
    try {
      const params = new URLSearchParams();
      params.append('skip', options.skip || 0);
      params.append('limit', Math.min(options.limit || 50, 1000));
      if (options.sort_by) params.append('sort_by', options.sort_by);
      if (options.order) params.append('order', options.order);
      if (options.is_duplicate !== undefined) params.append('is_duplicate', options.is_duplicate);

      const url = `/submissions/?${params.toString()}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('getSubmissions error:', error);
      throw error.response?.data || error;
    }
  },

  // NEW: Search submissions with advanced filtering
  searchSubmissions: async (options = {}) => {
    try {
      const params = new URLSearchParams();
      
      // Search query (searches across all fields: ID, name, email, age, gender)
      if (options.query) {
        params.append('query', options.query);
      }
      
      params.append('skip', options.skip || 0);
      params.append('limit', Math.min(options.limit || 50, 1000));
      
      if (options.is_duplicate !== undefined) {
        params.append('is_duplicate', options.is_duplicate);
      }

      const url = `/submissions/search?${params.toString()}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('searchSubmissions error:', error);
      throw error.response?.data || error;
    }
  },

  getSubmissionById: async (id) => {
    try {
      const response = await api.get(`/submissions/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  deleteSubmission: async (id) => {
    try {
      const response = await api.delete(`/submissions/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getDuplicateStats: async () => {
    try {
      const response = await api.get('/submissions/stats/duplicate-count');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getExistingEmails: async () => {
    try {
      const response = await api.get('/submissions/existing-emails');
      return response.data.emails;
    } catch (error) {
      console.error('getExistingEmails error:', error);
      throw error.response?.data || error;
    }
  },
};

export default formService;