<template>
  <div class="max-w-2xl space-y-6">
    <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-6 shadow-sm space-y-6">
      <h2 class="text-xl font-black text-slate-800 dark:text-purple-100 border-b border-theme-light-border dark:border-theme-dark-border pb-4">
        Настройки приложения
      </h2>

      <!-- 1. Валюта отображения -->
      <div class="flex items-center justify-between">
        <div>
          <p class="font-bold text-sm text-slate-800 dark:text-purple-100">Основная валюта</p>
          <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted">В этой валюте отображается баланс и общие отчеты</p>
        </div>
        <select
          v-model="settings.baseCurrency"
          @change="settings.setBaseCurrency(settings.baseCurrency)"
          class="bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-xs font-bold outline-none"
        >
          <option value="RUB">RUB (₽) — Российский рубль</option>
          <option value="USD">USD ($) — Доллар США</option>
          <option value="AMD">AMD (֏) — Армянский драм</option>
        </select>
      </div>

      <!-- 2. Смена темы -->
      <div class="flex items-center justify-between pt-4 border-t border-theme-light-border dark:border-theme-dark-border">
        <div>
          <p class="font-bold text-sm text-slate-800 dark:text-purple-100">Тема оформления</p>
          <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted">Переключение между светлой и ночной пурпурной палитрой</p>
        </div>
        <button
          @click="settings.toggleTheme()"
          class="flex items-center gap-2 bg-purple-100 dark:bg-purple-900/60 text-purple-800 dark:text-purple-200 px-4 py-2 rounded-xl text-xs font-bold transition"
        >
          <Sun v-if="settings.isDark" class="w-4 h-4" />
          <Moon v-else class="w-4 h-4" />
          {{ settings.isDark ? 'Тёмная тема' : 'Светлая тема' }}
        </button>
      </div>

      <!-- 3. Смена имени пользователя -->
      <div class="pt-4 border-t border-theme-light-border dark:border-theme-dark-border">
        <label class="block font-bold text-sm text-slate-800 dark:text-purple-100 mb-1">Имя пользователя</label>
        <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted mb-3">Отображается супругу/супруге в семейном бюджете</p>
        <div class="flex gap-3">
          <input
            v-model="newName"
            class="flex-1 bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none font-semibold"
          />
          <button
            @click="saveName"
            class="bg-theme-accent-primary hover:bg-theme-accent-hover text-white text-xs px-5 py-2.5 rounded-xl font-bold shadow-md transition"
          >
            Сохранить
          </button>
        </div>
      </div>

      <!-- 4. Выход из аккаунта -->
      <div class="pt-4 border-t border-theme-light-border dark:border-theme-dark-border flex justify-between items-center">
        <div>
          <p class="font-bold text-sm text-red-600 dark:text-red-400">Выход</p>
          <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted">Завершить текущий сеанс на этом устройстве</p>
        </div>
        <button
          @click="handleLogout"
          class="border border-red-300 dark:border-red-900/60 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 text-xs px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2"
        >
          <LogOut class="w-4 h-4" />
          Выйти из аккаунта
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { Sun, Moon, LogOut } from 'lucide-vue-next';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import api from '@/api';

const auth = useAuthStore();
const settings = useSettingsStore();
const router = useRouter();

const newName = ref(auth.user?.name || '');

async function saveName() {
  if (!newName.value.trim()) return;
  try {
    const { data } = await api.put('/auth/me', { name: newName.value });
    auth.user.name = data.name;
    localStorage.setItem('user', JSON.stringify(auth.user));
    alert('Имя успешно обновлено!');
  } catch (e) {
    alert('Ошибка сохранения имени');
  }
}

function handleLogout() {
  auth.logout();
  router.push('/login');
}
</script>