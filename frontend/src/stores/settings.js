import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSettingsStore = defineStore('settings', () => {
  const isDark = ref(localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches));
  const baseCurrency = ref(localStorage.getItem('base_currency') || 'RUB');

  function initTheme() {
    applyTheme(isDark.value);
  }

  function toggleTheme() {
    isDark.value = !isDark.value;
    applyTheme(isDark.value);
  }

  function setBaseCurrency(curr) {
    baseCurrency.value = curr;
    localStorage.setItem('base_currency', curr);
  }

  function applyTheme(dark) {
    if (dark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }

  return { isDark, baseCurrency, initTheme, toggleTheme, setBaseCurrency };
});