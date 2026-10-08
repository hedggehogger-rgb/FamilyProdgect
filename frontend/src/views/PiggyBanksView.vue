<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-xl font-black text-slate-800 dark:text-purple-100">Семейные копилки</h2>
        <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted mt-1">Накопления на совместные цели</p>
      </div>
      <button
        @click="showModal = true"
        class="bg-theme-accent-primary hover:bg-theme-accent-hover text-white text-xs px-4 py-2.5 rounded-xl font-bold transition shadow-md shadow-purple-500/20 flex items-center gap-2"
      >
        <Plus class="w-4 h-4" />
        Создать копилку
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="pb in piggyBanks"
        :key="pb.id"
        class="bg-theme-light-card dark:bg-theme-dark-card p-6 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm space-y-4"
      >
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-black text-slate-800 dark:text-purple-100 text-lg">{{ pb.name }}</h3>
            <span class="text-xs text-theme-light-muted dark:text-theme-dark-muted font-mono">Привязана к: {{ pb.account_id }}</span>
          </div>
          <span :class="pb.is_completed ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-purple-100 text-purple-800 dark:bg-purple-900/60 dark:text-purple-200'" class="text-xs px-3 py-1 rounded-full font-bold">
            {{ pb.is_completed ? 'Цель достигнута 🎉' : 'Копим' }}
          </span>
        </div>

        <div>
          <div class="flex justify-between text-sm mb-1.5 font-mono">
            <span class="font-bold text-slate-800 dark:text-purple-100">{{ pb.current_amount }} {{ pb.currency }}</span>
            <span class="text-theme-light-muted dark:text-theme-dark-muted">из {{ pb.target_amount }} {{ pb.currency }}</span>
          </div>
          <div class="w-full bg-slate-200 dark:bg-purple-950 h-2.5 rounded-full overflow-hidden">
            <div class="bg-emerald-500 h-full transition-all duration-500" :style="{ width: getPercent(pb) + '%' }"></div>
          </div>
        </div>

        <div class="flex items-center justify-between pt-2">
          <button @click="openDeposit(pb)" class="text-xs bg-purple-100 dark:bg-purple-900/60 text-purple-700 dark:text-purple-300 hover:bg-purple-200 font-bold px-3 py-2 rounded-xl transition">
            Пополнить
          </button>
          <button @click="deletePiggy(pb.id)" class="text-xs text-rose-500 hover:text-rose-700 font-bold">
            Разбить / Удалить
          </button>
        </div>
      </div>
    </div>

    <!-- Модалка создания копилки -->
    <div v-if="showModal" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-4">Новая копилка</h3>
        <form @submit.prevent="createPiggy" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Название цели</label>
            <input v-model="createForm.name" required placeholder="На отпуск в горах" class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none text-slate-800 dark:text-purple-100" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Целевая сумма</label>
            <input v-model.number="createForm.target_amount" type="number" step="any" min="1" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none text-slate-800 dark:text-purple-100 font-mono font-bold" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Счёт для списания</label>
            <CustomSelect
              v-model="createForm.account_id"
              :options="accountOptions"
              placeholder="Выберите счёт"
            />
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="showModal = false" class="px-4 py-2 text-xs font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition">Отмена</button>
            <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary hover:bg-theme-accent-hover text-white rounded-xl shadow-md transition">Создать</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { Plus } from 'lucide-vue-next';
import api from '@/api';
import CustomSelect from '@/components/CustomSelect.vue';

const piggyBanks = ref([]);
const accounts = ref([]);
const showModal = ref(false);

const createForm = reactive({
  name: '',
  target_amount: 10000,
  account_id: '',
  currency: 'RUB'
});

const accountOptions = computed(() => {
  return accounts.value.map(a => ({
    label: `${a.name} (${a.currency})`,
    value: a.id
  }));
});

function getPercent(pb) {
  const p = (Number(pb.current_amount) / Number(pb.target_amount)) * 100;
  return Math.min(100, Math.round(p));
}

async function loadData() {
  const [pbRes, accRes] = await Promise.all([
    api.get('/piggy-banks'),
    api.get('/accounts')
  ]);
  piggyBanks.value = pbRes.data;
  accounts.value = accRes.data;
  if (accounts.value.length && !createForm.account_id) {
    createForm.account_id = accounts.value[0].id;
  }
}

async function createPiggy() {
  await api.post('/piggy-banks', createForm);
  showModal.value = false;
  createForm.name = '';
  await loadData();
}

async function openDeposit(pb) {
  const sum = prompt(`Сколько внести в копилку "${pb.name}"?`);
  if (!sum || isNaN(sum) || Number(sum) <= 0) return;
  await api.post(`/piggy-banks/${pb.id}/deposit`, { amount: Number(sum) });
  await loadData();
}

async function deletePiggy(id) {
  if (!confirm('Удалить копилку? Средства вернутся на связанный счёт.')) return;
  await api.delete(`/piggy-banks/${id}?return_funds=true`);
  await loadData();
}

onMounted(loadData);
</script>