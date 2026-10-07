<template>
  <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
    <div class="p-6 border-b border-slate-100 flex justify-between items-center">
      <h2 class="text-base font-bold text-slate-800">Журнал операций</h2>
      <span class="text-xs text-slate-500">Всего записей: {{ total }}</span>
    </div>

    <table class="w-full text-left border-collapse text-sm">
      <thead class="bg-slate-50 text-slate-500 text-xs font-semibold uppercase">
        <tr>
          <th class="p-4">Дата</th>
          <th class="p-4">Тип</th>
          <th class="p-4">Счёт</th>
          <th class="p-4">Автор</th>
          <th class="p-4 text-right">Сумма</th>
          <th class="p-4 text-center">Действие</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        <tr v-for="t in transactions" :key="t.id" class="hover:bg-slate-50/50 transition">
          <td class="p-4 text-xs text-slate-500 font-mono">{{ formatDate(t.date) }}</td>
          <td class="p-4">
            <span :class="badgeClass(t.type)" class="px-2 py-0.5 rounded text-xs font-medium">
              {{ t.type }}
            </span>
          </td>
          <td class="p-4 font-mono text-xs">{{ t.account_id }}</td>
          <td class="p-4 text-xs">{{ t.author }}</td>
          <td class="p-4 font-bold font-mono text-right" :class="t.type === 'INCOME' ? 'text-emerald-600' : 'text-slate-900'">
            {{ t.type === 'INCOME' ? '+' : '-' }}{{ t.amount }} {{ t.currency }}
          </td>
          <td class="p-4 text-center">
            <button @click="deleteTx(t.id)" class="text-rose-500 hover:text-rose-700 text-xs font-medium">
              Удалить
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api';

const transactions = ref([]);
const total = ref(0);

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' });
}

function badgeClass(type) {
  if (type === 'INCOME') return 'bg-emerald-100 text-emerald-800';
  if (type === 'EXPENSE_IMPULSE') return 'bg-rose-100 text-rose-800';
  if (type === 'TRANSFER') return 'bg-sky-100 text-sky-800';
  return 'bg-slate-100 text-slate-800';
}

async function fetchTx() {
  const { data } = await api.get('/transactions?limit=50&offset=0');
  transactions.value = data.items;
  total.value = data.total;
}

async function deleteTx(id) {
  if (!confirm('Удалить транзакцию и вернуть средства на счёт?')) return;
  await api.delete(`/transactions/${id}`);
  await fetchTx();
}

onMounted(fetchTx);
</script>