<template>
  <div class="space-y-6">
    <div class="flex items-center gap-4 bg-theme-light-surface dark:bg-theme-dark-surface p-4 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm">
      <span class="text-sm font-bold text-slate-700 dark:text-purple-200">Период анализа:</span>
      <div class="w-40">
        <CustomSelect v-model="selectedMonth" :options="monthOptions" @change="loadReport" size="sm" />
      </div>
      <div class="w-32">
        <CustomSelect v-model="selectedYear" :options="yearOptions" @change="loadReport" size="sm" />
      </div>
    </div>

    <div v-if="report" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-theme-light-card dark:bg-theme-dark-card p-6 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm">
        <p class="text-xs font-semibold text-theme-light-muted dark:text-theme-dark-muted uppercase tracking-wider">Всего доходов</p>
        <p class="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-2 font-mono">+{{ report.total_income }} {{ report.currency }}</p>
      </div>

      <div class="bg-theme-light-card dark:bg-theme-dark-card p-6 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm">
        <p class="text-xs font-semibold text-theme-light-muted dark:text-theme-dark-muted uppercase tracking-wider">Всего расходов</p>
        <p class="text-2xl font-black text-rose-600 dark:text-rose-400 mt-2 font-mono">-{{ report.total_expense }} {{ report.currency }}</p>
      </div>

      <div class="bg-theme-light-card dark:bg-theme-dark-card p-6 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm">
        <p class="text-xs font-semibold text-theme-light-muted dark:text-theme-dark-muted uppercase tracking-wider">Чистые накопления</p>
        <p class="text-2xl font-black mt-2 font-mono" :class="report.net_savings >= 0 ? 'text-purple-600 dark:text-purple-300' : 'text-rose-500'">
          {{ report.net_savings }} {{ report.currency }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api';
import CustomSelect from '@/components/CustomSelect.vue';

const now = new Date();
const selectedMonth = ref(now.getMonth() + 1);
const selectedYear = ref(now.getFullYear());
const report = ref(null);

const monthOptions = Array.from({ length: 12 }, (_, i) => ({
  label: `Месяц ${i + 1}`,
  value: i + 1
}));

const yearOptions = [
  { label: '2025', value: 2025 },
  { label: '2026', value: 2026 },
  { label: '2027', value: 2027 }
];

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