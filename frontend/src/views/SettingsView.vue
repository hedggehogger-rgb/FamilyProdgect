<template>
  <div class="space-y-6 max-w-4xl pb-12">
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

      <div class="flex flex-wrap items-center justify-between gap-4 pt-2">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">Роль:</span>
            <span class="text-xs font-bold px-3 py-1 rounded-full bg-purple-100 dark:bg-purple-900/60 text-purple-800 dark:text-purple-200">
              {{ auth.user?.role === 'HUSBAND' ? 'Любими Муж 🦁' : 'КошкоЖена 🐱' }}
            </span>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">ID семьи:</span>
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

        <!-- Кнопка вызова QR-кода -->
        <button
          @click="openQrModal"
          class="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold shadow-md shadow-purple-500/20 transition"
        >
          <QrCode class="w-4 h-4" />
          Пригласить в семью (QR)
        </button>
      </div>
    </div>

    <!-- Параметры отображения и валюта -->
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

    <!-- Опасная зона: Удаление аккаунта -->
    <div class="bg-red-50/50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/60 rounded-2xl p-6 shadow-sm space-y-3">
      <div class="flex items-center gap-3">
        <AlertTriangle class="w-5 h-5 text-red-600" />
        <h3 class="font-black text-base text-red-700 dark:text-red-400">Опасная зона</h3>
      </div>
      <p class="text-xs text-slate-600 dark:text-red-300">
        Удаление аккаунта приведёт к выходу из семьи. Если вы единственный участник — все данные семьи и счета будут безвозвратно удалены.
      </p>
      <div class="pt-2">
        <button
          @click="showDeleteModal = true"
          class="px-4 py-2 text-xs font-bold bg-red-600 hover:bg-red-700 text-white rounded-xl shadow-md transition"
        >
          Удалить мой аккаунт
        </button>
      </div>
    </div>

    <!-- МОДАЛЬНОЕ ОКНО: QR-КОД ПРИГЛАШЕНИЯ -->
    <Teleport to="body">
      <div v-if="showQrModal" @click.self="showQrModal = false" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
        <div class="bg-white dark:bg-theme-dark-surface border border-purple-200 dark:border-purple-900 rounded-3xl p-6 shadow-2xl max-w-sm w-full text-center space-y-4">
          <div class="flex justify-between items-center pb-2 border-b border-slate-100 dark:border-purple-900/50">
            <h3 class="font-black text-base text-slate-900 dark:text-white">Пригласить в семью</h3>
            <button @click="showQrModal = false" class="text-slate-400 hover:text-slate-600 dark:hover:text-white">
              <X class="w-5 h-5" />
            </button>
          </div>

          <p class="text-xs text-slate-600 dark:text-purple-200 leading-relaxed">
            Наведите камеру смартфона на QR-код или скопируйте ссылку, чтобы второй член семьи сразу открыл регистрацию:
          </p>

          <div class="flex justify-center p-3 bg-white rounded-2xl shadow-inner border border-purple-100 max-w-[220px] mx-auto">
            <img v-if="qrImageSrc" :src="qrImageSrc" alt="QR Code" class="w-48 h-48 rounded-lg" />
            <div v-else class="w-48 h-48 flex items-center justify-center text-xs text-slate-400">Генерация QR...</div>
          </div>

          <div class="space-y-2 text-left pt-2">
            <label class="block text-[11px] font-bold text-slate-500 dark:text-purple-300">Прямая ссылка для вступления:</label>
            <div class="flex gap-2">
              <input :value="inviteLink" readonly class="w-full text-xs font-mono bg-slate-50 dark:bg-theme-dark-card border border-purple-200 dark:border-purple-800 rounded-xl px-3 py-2 text-slate-800 dark:text-purple-200 outline-none truncate" />
              <button @click="copyInviteLink" class="px-3 py-2 bg-purple-600 text-white rounded-xl text-xs font-bold shrink-0">
                <Check v-if="linkCopied" class="w-4 h-4" />
                <Copy v-else class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- МОДАЛЬНОЕ ОКНО: ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ АККАУНТА -->
    <Teleport to="body">
      <div v-if="showDeleteModal" @click.self="showDeleteModal = false" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
        <div class="bg-white dark:bg-theme-dark-surface border border-red-200 dark:border-red-900/60 rounded-3xl p-6 shadow-2xl max-w-sm w-full space-y-4">
          <div class="flex justify-between items-center pb-2 border-b border-red-100">
            <h3 class="font-black text-base text-red-600">Удаление аккаунта</h3>
            <button @click="showDeleteModal = false" class="text-slate-400 hover:text-slate-600">
              <X class="w-5 h-5" />
            </button>
          </div>

          <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            Это действие необратимо. Для подтверждения введите текущий пароль от вашего аккаунта:
          </p>

          <div>
            <label class="block text-xs font-bold text-slate-700 dark:text-purple-200 mb-1">Ваш пароль</label>
            <input
              v-model="deletePassword"
              type="password"
              placeholder="••••••••"
              class="w-full border border-slate-300 dark:border-purple-800 bg-white dark:bg-theme-dark-card rounded-xl p-2.5 text-sm !text-black dark:!text-white outline-none focus:ring-2 focus:ring-red-500"
            />
          </div>

          <div v-if="deleteError" class="p-2.5 rounded-xl bg-red-50 text-red-600 text-xs font-semibold">
            {{ deleteError }}
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button
              type="button"
              @click="showDeleteModal = false"
              class="px-4 py-2 text-xs font-bold rounded-xl border border-slate-200 dark:border-purple-800 hover:bg-slate-100 transition"
            >
              Отмена
            </button>
            <button
              type="button"
              @click="confirmDeleteAccount"
              :disabled="deleteLoading || !deletePassword"
              class="px-4 py-2 text-xs font-bold bg-red-600 hover:bg-red-700 text-white rounded-xl shadow-md transition disabled:opacity-50"
            >
              Удалить навсегда
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import CustomSelect from '@/components/CustomSelect.vue';
import api from '@/api';
import QRCode from 'qrcode';
import {
  User,
  Coins,
  Copy,
  Check,
  Sun,
  Moon,
  RefreshCw,
  QrCode,
  AlertTriangle,
  X
} from 'lucide-vue-next';

const router = useRouter();
const auth = useAuthStore();
const settings = useSettingsStore();

const userName = ref(auth.user?.name || '');
const copied = ref(false);
const ratesLoading = ref(false);

// Модалка QR
const showQrModal = ref(false);
const qrImageSrc = ref('');
const linkCopied = ref(false);

// Модалка Удаления
const showDeleteModal = ref(false);
const deletePassword = ref('');
const deleteLoading = ref(false);
const deleteError = ref('');

const currencyOptions = [
  { label: 'Российский рубль (RUB, ₽)', value: 'RUB' },
  { label: 'Доллар США (USD, $)', value: 'USD' },
  { label: 'Армянский драм (AMD, ֏)', value: 'AMD' }
];

const inviteLink = computed(() => {
  return `${window.location.origin}/join?code=${auth.user?.family_group_id}`;
});

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

async function openQrModal() {
  showQrModal.value = true;
  try {
    qrImageSrc.value = await QRCode.toDataURL(inviteLink.value, {
      width: 250,
      margin: 1,
      color: {
        dark: '#4c1d95',
        light: '#ffffff'
      }
    });
  } catch (err) {
    console.error('Ошибка создания QR:', err);
  }
}

async function copyInviteLink() {
  await navigator.clipboard.writeText(inviteLink.value);
  linkCopied.value = true;
  setTimeout(() => (linkCopied.value = false), 2000);
}

async function confirmDeleteAccount() {
  deleteError.value = '';
  deleteLoading.value = true;
  try {
    await api.delete('/auth/me', { data: { password: deletePassword.value } });
    auth.logout();
    router.push('/login');
  } catch (err) {
    deleteError.value = err.response?.data?.detail || 'Ошибка при удалении аккаунта';
  } finally {
    deleteLoading.value = false;
  }
}

async function refreshRates() {
  ratesLoading.value = true;
  await settings.fetchRates();
  ratesLoading.value = false;
}
</script>