<template>
  <div class="space-y-6">
    <div class="flex items-center gap-4 bg-white p-4 rounded-xl border border-slate-200">
      <span class="text-sm font-medium text-slate-700">Период анализа:</span>
      <select v-model="selectedMonth" @change="loadReport" class="border rounded-lg p-2 text-sm">
        <option v-for="m in 12" :key="m" :value="m">Месяц {{ m }}</option>
      </select>
      <select v-model="selectedYear" @change="loadReport" class="border rounded-lg p-2 text-sm">
        <option :value="2025">2025</option>
        <option :value="2026">2026</option>
      </select>
    </div>

    <div v-if="report" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Всего доходов</p>
        <p class="text-2xl font-black text-emerald-600 mt-2 font-mono">+{{ report.total_income }} {{ report.currency }}</p>
      </div>

      <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Всего расходов</p>
        <p class="text-2xl font-black text-rose-600 mt-2 font-mono">-{{ report.total_expense }} {{ report.currency }}</p>
      </div>

      <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Чистые накопления</p>
        <p class="text-2xl font-black mt-2 font-mono" :class="report.net_savings >= 0 ? 'text-slate-900' : 'text-rose-500'">
          {{ report.net_savings }} {{ report.currency }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api';

const now = new Date();
const selectedMonth = ref(now.getMonth() + 1);
const selectedYear = ref(now.getFullYear());
const report = ref(null);

async function loadReport() {
  try {
    const { data } = await api.get(`/analytics/monthly-report?year=${selectedYear.value}&month=${selectedMonth.value}&currency=RUB`);
    report.value = data;
  } catch (e) {
    report.value = null;
  }
}

onMounted(loadReport);
</script>