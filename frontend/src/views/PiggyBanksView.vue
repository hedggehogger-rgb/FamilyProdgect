<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-lg font-bold text-slate-800">Семейные копилки</h2>
      <button @click="showModal = true" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-4 py-2 rounded-lg font-medium transition shadow-sm">
        + Создать копилку
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="pb in piggyBanks" :key="pb.id" class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-bold text-slate-800 text-lg">{{ pb.name }}</h3>
            <span class="text-xs text-slate-400 font-mono">Привязана к: {{ pb.account_id }}</span>
          </div>
          <span :class="pb.is_completed ? 'bg-emerald-100 text-emerald-800' : 'bg-sky-100 text-sky-800'" class="text-xs px-2.5 py-1 rounded-full font-semibold">
            {{ pb.is_completed ? 'Цель достигнута 🎉' : 'Копим' }}
          </span>
        </div>

        <div>
          <div class="flex justify-between text-sm mb-1.5 font-mono">
            <span class="font-bold text-slate-800">{{ pb.current_amount }} {{ pb.currency }}</span>
            <span class="text-slate-400">из {{ pb.target_amount }} {{ pb.currency }}</span>
          </div>
          <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
            <div class="bg-emerald-500 h-full transition-all duration-500" :style="{ width: getPercent(pb) + '%' }"></div>
          </div>
        </div>

        <div class="flex items-center justify-between pt-2">
          <button @click="openDeposit(pb)" class="text-xs bg-emerald-50 text-emerald-700 hover:bg-emerald-100 font-semibold px-3 py-1.5 rounded-lg transition">
            Пополнить
          </button>
          <button @click="deletePiggy(pb.id)" class="text-xs text-rose-500 hover:text-rose-700">
            Разбить / Удалить
          </button>
        </div>
      </div>
    </div>

    <!-- Модалка создания -->
    <div v-if="showModal" class="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6">
        <h3 class="text-base font-bold text-slate-800 mb-4">Новая копилка</h3>
        <form @submit.prevent="createPiggy" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-slate-600">Название цели</label>
            <input v-model="createForm.name" required placeholder="На отпуск в горах" class="mt-1 w-full border rounded-lg p-2 text-sm" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-600">Целевая сумма</label>
            <input v-model.number="createForm.target_amount" type="number" step="100" min="1" required class="mt-1 w-full border rounded-lg p-2 text-sm" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-600">Счёт для списания</label>
            <select v-model="createForm.account_id" required class="mt-1 w-full border rounded-lg p-2 text-sm">
              <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
            </select>
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="showModal = false" class="px-4 py-2 text-xs border rounded-lg">Отмена</button>
            <button type="submit" class="px-4 py-2 text-xs bg-indigo-600 text-white rounded-lg">Создать</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '@/api';

const piggyBanks = ref([]);
const accounts = ref([]);
const showModal = ref(false);

const createForm = reactive({
  name: '',
  target_amount: 10000,
  account_id: '',
  currency: 'RUB'
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
  if (accounts.value.length) createForm.account_id = accounts.value[0].id;
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