<template>
  <div class="min-h-screen bg-slate-900 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
      <h2 class="text-2xl font-bold text-center text-slate-800 mb-6">
        {{ isRegister ? 'Создание семейного бюджета' : 'Вход в аккаунт' }}
      </h2>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <template v-if="isRegister">
          <div>
            <label class="block text-xs font-medium text-slate-700">Название семьи</label>
            <input v-model="form.familyName" required class="mt-1 w-full border rounded-lg p-2.5 text-sm" placeholder="Ивановы" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700">Ваше имя</label>
            <input v-model="form.name" required class="mt-1 w-full border rounded-lg p-2.5 text-sm" placeholder="Алексей" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700">Роль</label>
            <select v-model="form.role" class="mt-1 w-full border rounded-lg p-2.5 text-sm">
              <option value="HUSBAND">Муж (HUSBAND)</option>
              <option value="WIFE">Жена (WIFE)</option>
            </select>
          </div>
        </template>

        <div>
          <label class="block text-xs font-medium text-slate-700">Email</label>
          <input v-model="form.email" type="email" required class="mt-1 w-full border rounded-lg p-2.5 text-sm" placeholder="user@family.ru" />
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-700">Пароль</label>
          <input v-model="form.password" type="password" required class="mt-1 w-full border rounded-lg p-2.5 text-sm" />
        </div>

        <p v-if="error" class="text-rose-500 text-xs">{{ error }}</p>

        <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2.5 rounded-lg text-sm transition shadow-md">
          {{ isRegister ? 'Зарегистрироваться' : 'Войти' }}
        </button>
      </form>

      <div class="mt-4 text-center">
        <button @click="isRegister = !isRegister" class="text-xs text-slate-500 hover:text-slate-800 underline">
          {{ isRegister ? 'Уже есть семья? Войти' : 'Создать новую семью' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const auth = useAuthStore();

const isRegister = ref(false);
const error = ref('');

const form = reactive({
  email: '',
  password: '',
  familyName: '',
  name: '',
  role: 'HUSBAND'
});

async function handleSubmit() {
  error.value = '';
  try {
    if (isRegister.value) {
      await auth.registerFamily({
        family_name: form.familyName,
        first_user_name: form.name,
        first_user_email: form.email,
        first_user_password: form.password,
        first_user_role: form.role,
      });
    } else {
      await auth.login(form.email, form.password);
    }
    router.push('/');
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка авторизации';
  }
}
</script>