<template>
  <div class="min-h-screen bg-theme-dark-bg flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8 border border-purple-100">

      <!-- Заголовок -->
      <div class="text-center mb-6">
        <h2 class="text-2xl font-black text-slate-900 tracking-tight">
          {{ titles[mode] }}
        </h2>
        <p class="text-xs text-slate-500 mt-1">
          {{ subtitles[mode] }}
        </p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">

        <!-- РЕЖИМ 1: СОЗДАНИЕ СЕМЬИ -->
        <template v-if="mode === 'register'">
          <div>
            <label class="block text-xs font-bold text-slate-700">Название семьи</label>
            <input
              v-model="form.familyName"
              required
              class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm !text-black bg-white placeholder-slate-400 outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Семья Ивановых"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700">Ваше имя</label>
            <input
              v-model="form.name"
              required
              class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm !text-black bg-white placeholder-slate-400 outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Алексей"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Роль в семье</label>
            <CustomSelect v-model="form.role" :options="roleOptions" />
          </div>
        </template>

        <!-- РЕЖИМ 2: ПРИСОЕДИНЕНИЕ К СЕМЬЕ (QR ИЛИ РУЧНОЙ ВВОД КОДА) -->
        <template v-if="mode === 'join'">
          <div>
            <label class="block text-xs font-bold text-slate-700">ID / Код семьи</label>
            <input
              v-model="form.familyGroupId"
              @input="checkFamilyInfo"
              required
              class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm font-mono font-bold !text-purple-700 bg-purple-50/50 placeholder-slate-400 outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="fam-xxxxxxxx"
            />
            <!-- Подтверждение найденной семьи -->
            <p v-if="verifiedFamilyName" class="text-xs text-emerald-600 font-bold mt-1.5 flex items-center gap-1">
              <span>✓ Найдена семья: <strong>{{ verifiedFamilyName }}</strong></span>
            </p>
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700">Ваше имя</label>
            <input
              v-model="form.name"
              required
              class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm !text-black bg-white placeholder-slate-400 outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Мария"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Роль в семье</label>
            <CustomSelect v-model="form.role" :options="roleOptions" />
          </div>
        </template>

        <!-- ОБЩИЕ ПОЛЯ: EMAIL (для всех режимов) -->
        <div>
          <label class="block text-xs font-bold text-slate-700">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm !text-black bg-white placeholder-slate-400 outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="user@family.ru"
          />
        </div>

        <!-- ОБЩИЕ ПОЛЯ: ПАРОЛЬ (для всех, кроме сброса пароля) -->
        <div v-if="mode !== 'forgot'">
          <div class="flex justify-between items-center">
            <label class="block text-xs font-bold text-slate-700">Пароль</label>
            <button
              v-if="mode === 'login'"
              type="button"
              @click="setMode('forgot')"
              class="text-xs font-semibold text-purple-600 hover:text-purple-800 transition"
            >
              Забыли пароль?
            </button>
          </div>
          <input
            v-model="form.password"
            type="password"
            required
            class="mt-1 w-full border border-slate-300 rounded-xl p-2.5 text-sm !text-black bg-white placeholder-slate-400 outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

<!-- Сообщения об ошибках и успехе -->
        <div v-if="error" class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-xs font-semibold">
          {{ error }}
        </div>

        <div v-if="successMsg" class="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold space-y-2">
          <p>{{ successMsg }}</p>
          <!-- Кнопка мгновенного перехода без почты -->
          <a
            v-if="devResetUrl"
            :href="devResetUrl"
            class="block text-center py-2 px-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold shadow-sm transition"
          >
            Сменить пароль прямо сейчас →
          </a>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-xl text-sm transition shadow-lg shadow-purple-500/25 active:scale-98 disabled:opacity-50"
        >
          {{ buttonLabels[mode] }}
        </button>
      </form>

      <!-- Переключение режимов внизу карточки -->
      <div class="mt-6 pt-4 border-t border-slate-100 flex flex-col gap-2 text-center text-xs">
        <template v-if="mode === 'login'">
          <button @click="setMode('join')" class="font-bold text-purple-600 hover:text-purple-800">
            Вступить в существующую семью (по коду/QR)
          </button>
          <button @click="setMode('register')" class="text-slate-500 hover:text-slate-700">
            Создать новую семью с нуля
          </button>
        </template>

        <template v-else-if="mode === 'register'">
          <button @click="setMode('login')" class="font-bold text-purple-600 hover:text-purple-800">
            Уже есть аккаунт? Войти
          </button>
          <button @click="setMode('join')" class="text-slate-500 hover:text-slate-700">
            Хотите вступить в созданную семью?
          </button>
        </template>

        <template v-else-if="mode === 'join'">
          <button @click="setMode('login')" class="font-bold text-purple-600 hover:text-purple-800">
            Уже есть аккаунт? Войти
          </button>
          <button @click="setMode('register')" class="text-slate-500 hover:text-slate-700">
            Создать свою семью
          </button>
        </template>

        <template v-else-if="mode === 'forgot'">
          <button @click="setMode('login')" class="font-bold text-purple-600 hover:text-purple-800">
            ← Вернуться ко входу
          </button>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import CustomSelect from '@/components/CustomSelect.vue';
import api from '@/api';

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

// Режимы: 'login' | 'register' | 'join' | 'forgot'
const mode = ref('login');
const loading = ref(false);
const error = ref('');
const successMsg = ref('');
const devResetUrl = ref('');
const verifiedFamilyName = ref('');

const titles = {
  login: 'Вход в аккаунт',
  register: 'Создание семьи',
  join: 'Вступить в семью',
  forgot: 'Восстановление доступа'
};

const subtitles = {
  login: 'Семейный учет финансов и инвестиций',
  register: 'Создайте новую семью и станьте первым участником',
  join: 'Введите ID семьи от супруга или присоединитесь по QR',
  forgot: 'Введите email, чтобы получить ссылку для сброса'
};

const buttonLabels = {
  login: 'Войти',
  register: 'Создать семью и войти',
  join: 'Присоединиться к семье',
  forgot: 'Отправить ссылку на почту'
};

const roleOptions = [
  { label: 'Любими Муж', value: 'HUSBAND' },
  { label: 'КошкоЖена', value: 'WIFE' }
];

const form = reactive({
  email: '',
  password: '',
  familyName: '',
  name: '',
  role: 'WIFE',
  familyGroupId: ''
});

function setMode(newMode) {
  mode.value = newMode;
  error.value = '';
  successMsg.value = '';
}

async function checkFamilyInfo() {
  const code = form.familyGroupId.trim();
  if (code.length < 8) {
    verifiedFamilyName.value = '';
    return;
  }
  try {
    const { data } = await api.get(`/auth/family-info/${code}`);
    verifiedFamilyName.value = data.name;
    error.value = '';
  } catch (e) {
    verifiedFamilyName.value = '';
  }
}

async function handleSubmit() {
  error.value = '';
  successMsg.value = '';
  loading.value = true;

  try {
    if (mode.value === 'login') {
      await auth.login(form.email, form.password);
      router.push('/');
    } else if (mode.value === 'register') {
      await auth.registerFamily({
        family_name: form.familyName,
        first_user_name: form.name,
        first_user_email: form.email,
        first_user_password: form.password,
        first_user_role: form.role,
      });
      router.push('/');
    } else if (mode.value === 'join') {
      const { data } = await api.post('/auth/join-family', {
        family_group_id: form.familyGroupId.trim(),
        name: form.name.trim(),
        email: form.email.trim(),
        password: form.password,
        role: form.role,
      });
      auth.token = data.access_token;
      localStorage.setItem('token', data.access_token);
      await auth.fetchProfile();
      router.push('/');
    } else if (mode.value === 'forgot') {
      const { data } = await api.post('/auth/forgot-password', { email: form.email });
      successMsg.value = data.message;

      // Если бэкенд передал ссылку в поле id — сохраняем её для отображения кнопки
      if (data.id && data.id.startsWith('http')) {
        devResetUrl.value = data.id;
      }
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Произошла непредвиденная ошибка';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (route.query.mode === 'join' || route.query.code) {
    mode.value = 'join';
    if (route.query.code) {
      form.familyGroupId = route.query.code;
      checkFamilyInfo();
    }
  }
});
</script>