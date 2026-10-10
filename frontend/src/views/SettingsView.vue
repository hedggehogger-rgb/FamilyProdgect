<template>
  <div class="space-y-6 max-w-4xl">
    <!-- Карточка профиля пользователя -->
    <div class="bg-theme-light-card dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-6 shadow-sm space-y-4">
      <div class="flex items-center gap-3 pb-3 border-b border-theme-light-border dark:border-theme-dark-border">
        <User class="w-5 h-5 text-purple-600 dark:text-purple-400" />
        <h3 class="font-black text-base text-slate-800 dark:text-purple-100">Профиль пользователя</h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Имя</label>
          <div class="flex gap-2">
            <input
              v-model="userName"
              class="w-full bg-white dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-xl px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-purple-500 text-slate-800 dark:text-white font-medium"
            />
            <button
              @click="saveProfileName"
              class="px-4 py-2 text-xs font-bold bg-theme-accent-primary hover:bg-theme-accent-hover text-white rounded-xl shadow-sm transition"
            >
              Сохранить
            </button>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Email</label>
          <input
            :value="auth.user?.email"
            disabled
            class="w-full bg-slate-100 dark:bg-theme-dark-surface/60 border border-theme-light-border dark:border-theme-dark-border rounded-xl px-3 py-2 text-sm text-slate-600 dark:text-purple-200 outline-none cursor-not-allowed font-mono"
          />
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-4 pt-2">
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">Роль в семье:</span>
          <span class="text-xs font-bold px-3 py-1 rounded-full bg-purple-100 dark:bg-purple-900/60 text-purple-800 dark:text-purple-200">
            {{ auth.user?.role === 'HUSBAND' ? 'Любими Муж 🦁' : 'КошкоЖена 🐱' }}
          </span>
        </div>

        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">ID семейной группы:</span>
          <button
            @click="copyFamilyId"
            class="text-xs font-mono font-bold px-2.5 py-1 rounded-lg border border-purple-300 dark:border-purple-700 hover:bg-purple-50 dark:hover:bg-purple-950/40 text-purple-700 dark:text-purple-200 flex items-center gap-1.5 transition"
            title="Нажмите, чтобы скопировать"
          >
            <span>{{ auth.user?.family_group_id }}</span>
            <Check v-if="copied" class="w-3.5 h-3.5 text-emerald-400" />
            <Copy v-else class="w-3.5 h-3.5 text-purple-400" />
          </button>
        </div>
      </div>
    </div>

    <!-- Общие настройки системы -->
    <div class="bg-theme-light-card dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-6 shadow-sm space-y-4">
      <div class="flex items-center gap-3 pb-3 border-b border-theme-light-border dark:border-theme-dark-border">
        <Coins class="w-5 h-5 text-purple-600 dark:text-purple-400" />
        <h3 class="font-black text-base text-slate-800 dark:text-purple-100">Параметры отображения</h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        <div>
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1.5">
            Базовая валюта пересчёта
          </label>
          <CustomSelect
            :modelValue="settings.baseCurrency"
            :options="currencyOptions"
            @change="handleCurrencyChange"
          />
          <p class="text-[11px] text-theme-light-muted dark:text-theme-dark-muted mt-1.5">
            Все балансы и аналитика будут конвертироваться в эту валюту
          </p>
        </div>

        <div>
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1.5">
            Тема интерфейса
          </label>
          <button
            type="button"
            @click="settings.toggleTheme()"
            class="w-full flex items-center justify-between px-4 py-2.5 rounded-xl border border-theme-light-border dark:border-theme-dark-border bg-white dark:bg-theme-dark-surface font-bold text-sm text-slate-800 dark:text-purple-100 hover:border-purple-400 transition"
          >
            <span class="flex items-center gap-2">
              <Sun v-if="!settings.isDark" class="w-4 h-4 text-amber-500" />
              <Moon v-else class="w-4 h-4 text-purple-400" />
              {{ settings.isDark ? 'Тёмная тема' : 'Светлая тема' }}
            </span>
            <span class="text-xs text-purple-600 dark:text-purple-300 font-bold">Сменить</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Курсы валют -->
    <div class="bg-theme-light-card dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-6 shadow-sm space-y-4">
      <div class="flex justify-between items-center pb-3 border-b border-theme-light-border dark:border-theme-dark-border">
        <h3 class="font-black text-base text-slate-800 dark:text-purple-100">Текущие курсы валют к USD</h3>
        <button
          @click="refreshRates"
          :disabled="ratesLoading"
          class="text-xs font-bold text-purple-600 dark:text-purple-300 hover:underline flex items-center gap-1.5 disabled:opacity-50"
        >
          <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': ratesLoading }" />
          Обновить
        </button>
      </div>

      <div class="grid grid-cols-3 gap-4 text-center font-mono">
        <div class="p-3 rounded-xl bg-purple-50/50 dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border">
          <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted font-bold font-sans">USD ($)</p>
          <p class="text-base font-black text-purple-700 dark:text-purple-200 mt-1">1.00</p>
        </div>
        <div class="p-3 rounded-xl bg-purple-50/50 dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border">
          <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted font-bold font-sans">RUB (₽)</p>
          <p class="text-base font-black text-purple-700 dark:text-purple-200 mt-1">{{ settings.rates.RUB }}</p>
        </div>
        <div class="p-3 rounded-xl bg-purple-50/50 dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border">
          <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted font-bold font-sans">AMD (֏)</p>
          <p class="text-base font-black text-purple-700 dark:text-purple-200 mt-1">{{ settings.rates.AMD }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import CustomSelect from '@/components/CustomSelect.vue';
import api from '@/api';
import { User, Coins, Copy, Check, Sun, Moon, RefreshCw } from 'lucide-vue-next';

const auth = useAuthStore();
const settings = useSettingsStore();

const userName = ref(auth.user?.name || '');
const copied = ref(false);
const ratesLoading = ref(false);

const currencyOptions = [
  { label: 'Российский рубль (RUB, ₽)', value: 'RUB' },
  { label: 'Доллар США (USD, $)', value: 'USD' },
  { label: 'Армянский драм (AMD, ֏)', value: 'AMD' }
];

function handleCurrencyChange(val) {
  settings.setBaseCurrency(val);
}

async function saveProfileName() {
  if (!userName.value.trim()) return;
  try {
    const { data } = await api.put('/auth/me', { name: userName.value.trim() });
    auth.user = data;
    localStorage.setItem('user', JSON.stringify(data));
    alert('Имя успешно сохранено');
  } catch (err) {
    alert('Не удалось обновить имя');
  }
}

async function copyFamilyId() {
  if (!auth.user?.family_group_id) return;
  await navigator.clipboard.writeText(auth.user.family_group_id);
  copied.value = true;
  setTimeout(() => (copied.value = false), 2000);
}

async function refreshRates() {
  ratesLoading.value = true;
  await settings.fetchRates();
  ratesLoading.value = false;
}
</script>