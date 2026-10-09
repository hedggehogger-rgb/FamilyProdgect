import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/api';

export const useSettingsStore = defineStore('settings', () => {
  const isDark = ref(localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches));
  const baseCurrency = ref(localStorage.getItem('base_currency') || 'RUB');
  const rates = ref({ RUB: 92, USD: 1, AMD: 390 }); // дефолтные

  function initTheme() { applyTheme(isDark.value); }

  function toggleTheme() {
    isDark.value = !isDark.value;
    applyTheme(isDark.value);
  }

  function setBaseCurrency(curr) {
    baseCurrency.value = curr;
    localStorage.setItem('base_currency', curr);
  }

  function applyTheme(dark) {
    if (dark) { document.documentElement.classList.add('dark'); localStorage.setItem('theme', 'dark'); }
    else { document.documentElement.classList.remove('dark'); localStorage.setItem('theme', 'light'); }
  }

  async function fetchRates() {
    try {
      const { data } = await api.get('/analytics/rates');
      rates.value = data;
    } catch(e) { console.warn("Не удалось загрузить курсы валют"); }
  }

  function convert(amount, fromCur, toCur = baseCurrency.value) {
    if (fromCur === toCur) return Number(amount);
    const rateFrom = Number(rates.value[fromCur] || 1);
    const rateTo = Number(rates.value[toCur] || 1);
    return (Number(amount) / rateFrom) * rateTo;
  }

  return { isDark, baseCurrency, rates, initTheme, toggleTheme, setBaseCurrency, fetchRates, convert };
});