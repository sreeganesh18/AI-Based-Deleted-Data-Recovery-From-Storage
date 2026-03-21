import axios from 'axios';

const API_BASE_URL = 'https://keratose-delena-unalphabetical.ngrok-free.dev/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (credentials) => api.post('/login', credentials),
  register: (userData) => api.post('/register', userData),
};

export const recoveryAPI = {
  uploadImage: (investigationId, file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/upload-image?investigation_id=${investigationId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  },
  startRecovery: (imageId) => api.post(`/recover/${imageId}`),
  getTaskStatus: (taskId) => api.get(`/task-status/${taskId}`),
  getFragments: (imageId) => api.get(`/fragments/${imageId}`),
  getRecoveredFiles: (imageId) => api.get(`/recovered-files/${imageId}`),
};

export const getDownloadUrl = (fileId) => `${API_BASE_URL}/download/${fileId}`;

export default api;
