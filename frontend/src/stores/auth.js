import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null);
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));

  const isAuthenticated = computed(() => !!token.value);

  async function login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const { data } = await api.post('/auth/login', formData);
    token.value = data.access_token;
    localStorage.setItem('token', data.access_token);

    await fetchProfile();
    return data;
  }

  async function registerFamily(payload) {
    const { data } = await api.post('/auth/register-family', payload);
    token.value = data.access_token;
    localStorage.setItem('token', data.access_token);
    await fetchProfile();
    return data;
  }

  async function fetchProfile() {
    try {
      const { data } = await api.get('/auth/me');
      user.value = data;
      localStorage.setItem('user', JSON.stringify(data));
    } catch (e) {
      logout();
    }
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  return { token, user, isAuthenticated, login, registerFamily, fetchProfile, logout };
});