// src/api/client.js
import axios from 'axios'

const API_BASE = '/api'

const client = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
})

export const authAPI = {
  login: (username, password, remember) =>
    client.post('/auth/login', { username, password, remember }),
  
  register: (username, email, password) =>
    client.post('/auth/register', { username, email, password }),
  
  logout: () =>
    client.post('/auth/logout'),
  
  me: () =>
    client.get('/auth/me'),
}

export const predictionAPI = {
  predict: (formData) =>
    client.post('/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  
  getResult: (id) =>
    client.get(`/result/${id}`),
  
  getHistory: () =>
    client.get('/history'),
  
  getAlerts: () =>
    client.get('/alerts'),
  
  markAlertsRead: () =>
    client.post('/alerts/read'),
}

export const adminAPI = {
  getDashboard: () =>
    client.get('/admin/dashboard'),
  
  getPredictions: (page = 1, crop = '', status = '') =>
    client.get('/admin/predictions', { params: { page, crop, status } }),
  
  getDataset: () =>
    client.get('/admin/dataset'),
  
  uploadDataset: (formData) =>
    client.post('/admin/dataset/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  
  getTrainHistory: () =>
    client.get('/admin/train'),
  
  startTraining: (config) =>
    client.post('/admin/train/start', config),
  
  getUsers: () =>
    client.get('/admin/users'),
  
  toggleUser: (userId) =>
    client.post(`/admin/users/${userId}/toggle`),
}

export default client
