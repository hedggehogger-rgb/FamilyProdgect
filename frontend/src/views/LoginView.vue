<template>
  <div class="min-h-screen bg-theme-dark-bg flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8 border border-purple-100">
      <div class="text-center mb-6">
        <h2 class="text-2xl font-black text-slate-900 tracking-tight">
          {{ isRegister ? 'Создание семейного бюджета' : 'Вход в аккаунт' }}
        </h2>
        <p class="text-xs text-slate-500 mt-1">Семейный учет финансов и инвестиций</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <template v-if="isRegister">
          <div>
            <label class="block text-xs font-bold text-slate-700">Название семьи</label>
            <input
              v-model="form.familyName"
              required
              class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm !text-black text-black bg-white placeholder-slate-400 outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Ивановы"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700">Ваше имя</label>
            <input
              v-model="form.name"
              required
              class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm !text-black text-black bg-white placeholder-slate-400 outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Алексей"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Роль</label>
            <CustomSelect
              v-model="form.role"
              :options="[
                { label: 'Любими Муж', value: 'HUSBAND' },
                { label: 'КошкоЖена', value: 'WIFE' }
              ]"
            />
          </div>
        </template>

        <div>
          <label class="block text-xs font-bold text-slate-700">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm !text-black text-black bg-white placeholder-slate-400 outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="user@family.ru"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700">Пароль</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm !text-black text-black bg-white placeholder-slate-400 outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div v-if="error" class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-xs font-semibold">
          {{ error }}
        </div>

        <button
          type="submit"
          class="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-xl text-sm transition shadow-lg shadow-purple-500/25 active:scale-98"
        >
          {{ isRegister ? 'Зарегистрироваться' : 'Войти' }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <button
          @click="isRegister = !isRegister"
          class="text-xs font-semibold text-purple-600 hover:text-purple-800 transition underline underline-offset-4"
        >
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
import CustomSelect from '@/components/CustomSelect.vue';

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