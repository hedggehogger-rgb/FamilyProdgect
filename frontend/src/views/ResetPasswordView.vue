<template>
  <div class="min-h-screen bg-theme-dark-bg flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8 border border-purple-100">
      <div class="text-center mb-6">
        <h2 class="text-2xl font-black text-slate-900 tracking-tight">Новый пароль</h2>
        <p class="text-xs text-slate-500 mt-1">Придумайте новый надёжный пароль для входа</p>
      </div>

      <div v-if="success" class="space-y-4 text-center">
        <div class="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold leading-relaxed">
          Пароль успешно обновлён! Теперь вы можете войти со своим новым паролем.
        </div>
        <RouterLink
          to="/login"
          class="block w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-xl text-sm transition shadow-lg shadow-purple-500/25"
        >
          Перейти ко входу
        </RouterLink>
      </div>

      <form v-else @submit.prevent="handleReset" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-700">Новый пароль (минимум 6 символов)</label>
          <input
            v-model="password"
            type="password"
            required
            minlength="6"
            class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm !text-black bg-white outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700">Повторите новый пароль</label>
          <input
            v-model="confirmPassword"
            type="password"
            required
            class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm !text-black bg-white outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div v-if="error" class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-xs font-semibold">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-xl text-sm transition shadow-lg shadow-purple-500/25 active:scale-98 disabled:opacity-50"
        >
          Сохранить пароль
        </button>

        <div class="text-center pt-2">
          <RouterLink to="/login" class="text-xs font-semibold text-purple-600 hover:underline">
            Вернуться ко входу
          </RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/api';

const route = useRoute();
const token = ref('');
const password = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const error = ref('');
const success = ref(false);

onMounted(() => {
  token.value = route.query.token || '';
  if (!token.value) {
    error.value = 'Токен сброса пароля отсутствует или ссылка повреждена.';
  }
});

async function handleReset() {
  if (password.value !== confirmPassword.value) {
    error.value = 'Пароли не совпадают';
    return;
  }
  error.value = '';
  loading.value = true;
  try {
    await api.post('/auth/reset-password', {
      token: token.value,
      new_password: password.value,
    });
    success.value = true;
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не удалось сбросить пароль';
  } finally {
    loading.value = false;
  }
}
</script>