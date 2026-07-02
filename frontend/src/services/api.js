/**
 * API service module for communicating with the backend.
 *
 * Centralises all HTTP calls and provides consistent error handling.
 */
import axios from 'axios';

const API_BASE_URL =
  process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Interceptors ────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Could redirect to login in a real app
      console.warn('Unauthenticated request – redirecting to login');
    }
    return Promise.reject(error);
  }
);

// ── Profile API ─────────────────────────────────────────────────────

/**
 * Fetch a paginated list of public user profiles.
 * @param {string} [search] - Optional username search query.
 * @param {number} [page=1] - Page number.
 */
export const getProfiles = (search = '', page = 1) =>
  api.get('/profiles/', { params: { search, page } });

/**
 * Fetch a single profile by its ID.
 * @param {number} profileId
 */
export const getProfile = (profileId) => api.get(`/profiles/${profileId}/`);

/**
 * Fetch the authenticated user's own profile.
 */
export const getMyProfile = () => api.get('/profiles/me/');

/**
 * Update the authenticated user's profile.
 * @param {FormData|Object} data - Fields to update (supports multipart for avatar).
 */
export const updateMyProfile = (data) => {
  const isFormData = data instanceof FormData;
  return api.patch('/profiles/me/', data, {
    headers: isFormData ? { 'Content-Type': 'multipart/form-data' } : {},
  });
};

export default api;
