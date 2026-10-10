<template>
  <div class="space-y-6">
    <!-- Шапка календаря -->
    <div class="flex flex-wrap items-center justify-between gap-4 bg-theme-light-surface dark:bg-theme-dark-surface p-4 rounded-2xl border border-slate-200/70 dark:border-white/[0.08] shadow-sm">
      <div class="flex items-center gap-3">
        <button @click="prevMonth" class="p-2 rounded-xl hover:bg-theme-light-hover dark:hover:bg-theme-dark-hover transition">
          <ChevronLeft class="w-5 h-5 text-purple-600 dark:text-purple-300" />
        </button>
        <span class="text-base font-black text-slate-800 dark:text-white min-w-36 text-center">
          {{ MONTH_NAMES[currentMonth - 1] }} {{ currentYear }}
        </span>
        <button @click="nextMonth" class="p-2 rounded-xl hover:bg-theme-light-hover dark:hover:bg-theme-dark-hover transition">
          <ChevronRight class="w-5 h-5 text-purple-600 dark:text-purple-300" />
        </button>
      </div>

      <div class="flex gap-2">
        <button @click="openPlanModal" class="bg-white dark:bg-theme-dark-card text-slate-700 dark:text-purple-200 border border-slate-200/80 dark:border-white/10 hover:bg-slate-50 text-xs px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 shadow-sm">
          <Target class="w-4 h-4" /> Запланировать расходы
        </button>
        <button @click="showAnalyticsModal = true" class="bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-200 border border-purple-200/70 dark:border-purple-800/60 hover:bg-purple-200 text-xs px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 shadow-sm">
          <BarChart3 class="w-4 h-4" /> Аналитика за {{ MONTH_NAMES[currentMonth - 1] }}
        </button>
      </div>
    </div>

    <!-- Календарная сетка -->
    <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-slate-200/70 dark:border-white/[0.08] rounded-2xl p-4 shadow-sm">
      <div class="grid grid-cols-7 gap-2 mb-2 text-center text-xs font-black uppercase text-theme-light-muted dark:text-purple-300">
        <div v-for="w in WEEK_DAYS" :key="w">{{ w }}</div>
      </div>
      <div class="grid grid-cols-7 gap-2">
        <div
          v-for="(cell, idx) in calendarCells"
          :key="idx"
          @click="cell.isCurrentMonth && (selectedDay = cell.day)"
          :class="[
            cell.isCurrentMonth
              ? 'bg-theme-light-card dark:bg-theme-dark-card border-slate-200/80 dark:border-white/[0.08] cursor-pointer hover:border-purple-400 dark:hover:border-purple-500/60 relative overflow-hidden'
              : 'opacity-0 pointer-events-none border-transparent',
            selectedDay === cell.day ? 'ring-2 ring-purple-500' : ''
          ]"
          class="border rounded-2xl min-h-24 p-2.5 flex flex-col justify-between transition-all"
        >
          <div class="flex justify-between items-start z-10">
            <span
              v-if="cell.isCurrentMonth"
              class="text-xs font-bold"
              :class="cell.isToday ? 'bg-theme-accent-primary text-white w-6 h-6 rounded-full flex items-center justify-center shadow-sm' : 'text-slate-700 dark:text-white'"
            >
              {{ cell.day }}
            </span>
            <span v-else></span>
            <div v-if="cell.hasPlanned" class="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></div>
          </div>
          <div v-if="cell.isCurrentMonth && cell.totals" class="space-y-1 font-mono text-[11px] leading-tight mt-1 z-10 relative">
            <p v-if="cell.totals.income > 0" class="text-emerald-600 dark:text-emerald-400 font-bold truncate">
              +{{ Math.round(cell.totals.income) }} {{ settings.getSymbol(settings.baseCurrency) }}
            </p>
            <p v-if="cell.totals.expense > 0" class="text-rose-600 dark:text-rose-400 font-bold truncate">
              -{{ Math.round(cell.totals.expense) }} {{ settings.getSymbol(settings.baseCurrency) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальные окна -->
    <DayTransactionsModal
      :day="selectedDay"
      :monthName="MONTH_NAMES[currentMonth - 1]"
      :transactions="dayTransactions"
      :categories="categories"
      :accounts="accounts"
      @close="selectedDay = null"
      @ask-delete="askDelete"
    />
    <BudgetPlanModal :show="showPlanModal" :loading="isForecastLoading" :categories="expenseCategories" :forecasts="forecasts" :monthName="MONTH_NAMES[currentMonth - 1]" :year="currentYear" :getSpentForCat="getSpentInCurrentMonthForCat" @close="showPlanModal = false" />
    <MonthAnalyticsModal :show="showAnalyticsModal" :monthName="MONTH_NAMES[currentMonth - 1]" :year="currentYear" :totalIncome="monthTotalIncome" :totalExpense="monthTotalExpense" :savings="monthSavings" :categoryStats="categoryStats" @close="showAnalyticsModal = false" @select-category="detailCategory = $event" />
    <CategoryDetailModal :category="detailCategory" :monthName="MONTH_NAMES[currentMonth - 1]" :transactions="categoryTransactions" @close="detailCategory = null" />
    <TransactionDeleteModal :targetId="deleteTxId" :tx="txToDelete" :isAccountMissing="isAccountMissing" v-model:refundAccountId="selectedRefundAccountId" :accountOptions="accountOptions" :accountName="getAccountName(txToDelete?.account_id)" @cancel="cancelDelete" @confirm="confirmDelete" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ChevronLeft, ChevronRight, BarChart3, Target } from 'lucide-vue-next';
import api from '@/api';
import { useSettingsStore } from '@/stores/settings';
import { MONTH_NAMES, WEEK_DAYS, getExactDay, getExactMonth, getExactYear } from '@/utils/formatters';

import DayTransactionsModal from './transactions/DayTransactionsModal.vue';
import BudgetPlanModal from './transactions/BudgetPlanModal.vue';
import MonthAnalyticsModal from './transactions/MonthAnalyticsModal.vue';
import CategoryDetailModal from './transactions/CategoryDetailModal.vue';
import TransactionDeleteModal from './transactions/TransactionDeleteModal.vue';

const settings = useSettingsStore();
const now = new Date();
const currentYear = ref(now.getFullYear());
const currentMonth = ref(now.getMonth() + 1);
const selectedDay = ref(null);
const showAnalyticsModal = ref(false);
const showPlanModal = ref(false);
const detailCategory = ref(null);

const deleteTxId = ref(null);
const txToDelete = ref(null);
const selectedRefundAccountId = ref('');

const transactions = ref([]);
const categories = ref([]);
const accounts = ref([]);
const piggyBanks = ref([]);
const limitsMap = ref({});
const forecasts = ref({});
const isForecastLoading = ref(false);

function isIncomeType(t) { return t.startsWith('INCOME'); }

const expenseCategories = computed(() => categories.value.filter(c => c.group === 'EXPENSE'));
const accountOptions = computed(() => accounts.value.map(a => ({ label: `${a.name} (${settings.getSymbol(a.currency)})`, value: a.id })));
const isAccountMissing = computed(() => txToDelete.value ? !accounts.value.some(a => a.id === txToDelete.value.account_id) : false);

function getAccountName(id) { const a = accounts.value.find(acc => acc.id === id); return a ? a.name : '—'; }

const plannedTransactions = computed(() => {
  const planned = [];
  const daysInMonth = new Date(currentYear.value, currentMonth.value, 0).getDate();

  categories.value.forEach(cat => {
    if (!cat.default_amount || cat.frequency === 'NONE') return;
    const days = [];
    if (cat.frequency === 'DAILY') {
      for (let i = 1; i <= daysInMonth; i++) days.push(i);
    } else if (cat.frequency === 'WEEKLY') {
      for (let i = 1; i <= daysInMonth; i++) {
        let d = new Date(currentYear.value, currentMonth.value - 1, i).getDay();
        if ((d === 0 ? 7 : d) === cat.day_of_week) days.push(i);
      }
    } else if (cat.frequency === 'MONTHLY') {
      days.push(Math.min(cat.day_of_month || 1, daysInMonth));
    } else if (cat.frequency === 'QUARTERLY' && (currentMonth.value % 3 === (cat.recurrence_month || 1) % 3)) {
      days.push(Math.min(cat.day_of_month || 1, daysInMonth));
    } else if (cat.frequency === 'ANNUALLY' && currentMonth.value === cat.recurrence_month) {
      days.push(Math.min(cat.day_of_month || 1, daysInMonth));
    }

    const acc = accounts.value.find(a => a.id === cat.default_account_id);
    const effectiveCurrency = cat.default_currency || (acc ? acc.currency : 'RUB');

    days.forEach(d => {
      planned.push({
        id: `plan-cat-${cat.id}-${d}`,
        type: cat.group === 'INCOME' ? 'INCOME_PLANNED' : 'EXPENSE_PLANNED',
        category_id: cat.id,
        account_id: cat.default_account_id,
        amount: cat.default_amount,
        currency: effectiveCurrency,
        date: `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}T12:00:00`,
        isPlanned: true,
        is_executed: false,
        note: `План: ${cat.name}`
      });
    });
  });

  piggyBanks.value.forEach(pb => {
    if (!pb.is_auto_replenish || pb.is_completed) return;
    if (pb.skip_until_month === `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}`) return;
    const d = pb.auto_replenish_day || 1;
    if (d <= daysInMonth) {
      planned.push({
        id: `plan-pb-${pb.id}-${d}`,
        type: 'EXPENSE_PLANNED',
        category_id: null,
        account_id: pb.account_id,
        amount: pb.auto_replenish_amount,
        currency: pb.currency,
        date: `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}T12:00:00`,
        isPlanned: true,
        is_executed: false,
        note: `План: В копилку '${pb.name}'`
      });
    }
  });
  return planned;
});

const calendarCells = computed(() => {
  const daysInMonth = new Date(currentYear.value, currentMonth.value, 0).getDate();
  const firstDay = (new Date(currentYear.value, currentMonth.value - 1, 1).getDay() + 6) % 7;
  const cells = [];
  for (let i = 0; i < firstDay; i++) cells.push({ day: 0, isCurrentMonth: false });

  for (let d = 1; d <= daysInMonth; d++) {
    const realDayTxs = transactions.value.filter(t => t.type !== 'TRANSFER' && getExactDay(t.date) === d);
    const planDayTxs = plannedTransactions.value.filter(t => getExactDay(t.date) === d);
    let inc = 0, exp = 0;

    [...realDayTxs, ...planDayTxs].forEach(t => {
      const val = settings.convert(t.amount, t.currency);
      if (isIncomeType(t.type)) inc += val; else exp += val;
    });

    const isToday = now.getFullYear() === currentYear.value && now.getMonth() + 1 === currentMonth.value && now.getDate() === d;
    cells.push({
      day: d,
      isCurrentMonth: true,
      isToday,
      hasPlanned: planDayTxs.length > 0 || realDayTxs.some(t => t.is_executed === false),
      totals: { income: inc, expense: exp }
    });
  }
  return cells;
});

const dayTransactions = computed(() => {
  if (!selectedDay.value) return [];
  const real = transactions.value.filter(t => t.type !== 'TRANSFER' && getExactDay(t.date) === selectedDay.value);
  const plan = plannedTransactions.value.filter(t => getExactDay(t.date) === selectedDay.value);
  return [...real, ...plan];
});

const monthTotalIncome = computed(() => {
  return Math.round(transactions.value.reduce((acc, t) => (isIncomeType(t.type) && t.is_executed !== false) ? acc + settings.convert(t.amount, t.currency) : acc, 0));
});

const monthTotalExpense = computed(() => {
  return Math.round(transactions.value.reduce((acc, t) => (!isIncomeType(t.type) && t.type !== 'TRANSFER' && t.is_executed !== false) ? acc + settings.convert(t.amount, t.currency) : acc, 0));
});

const monthSavings = computed(() => monthTotalIncome.value - monthTotalExpense.value);

const categoryStats = computed(() => {
  const totalExp = monthTotalExpense.value || 1;
  const res = [];
  expenseCategories.value.forEach(cat => {
    let spent = 0;
    transactions.value.forEach(t => {
      if (t.category_id === cat.id && !isIncomeType(t.type) && t.type !== 'TRANSFER' && t.is_executed !== false) {
        spent += settings.convert(t.amount, t.currency);
      }
    });
    if (spent > 0) {
      res.push({ cat, spent: Math.round(spent), pct: Math.min(100, Math.round((spent / totalExp) * 100)), limit: limitsMap.value[cat.id] || null });
    }
  });
  return res.sort((a, b) => b.spent - a.spent);
});

const categoryTransactions = computed(() => detailCategory.value ? transactions.value.filter(t => t.category_id === detailCategory.value.id && t.type !== 'TRANSFER') : []);

function getSpentInCurrentMonthForCat(id) {
  return Math.round(transactions.value.reduce((acc, t) => (t.category_id === id && !isIncomeType(t.type) && t.type !== 'TRANSFER' && t.is_executed !== false) ? acc + settings.convert(t.amount, t.currency) : acc, 0));
}

function prevMonth() { if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value--; } else currentMonth.value--; loadMonthData(); }
function nextMonth() { if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++; } else currentMonth.value++; loadMonthData(); }

async function openPlanModal() {
  showPlanModal.value = true; isForecastLoading.value = true;
  await Promise.all(expenseCategories.value.map(c => api.get(`/budget/forecast/${c.id}?target_currency=${settings.baseCurrency}`).then(res => forecasts.value[c.id] = res.data).catch(() => {})));
  isForecastLoading.value = false;
}

async function loadMonthData() {
  try {
    const [txRes, catRes, accRes, pbRes] = await Promise.all([
      api.get('/transactions?limit=500&offset=0&exclude_transfers=true'),
      api.get('/categories'), api.get('/accounts'), api.get('/piggy-banks')
    ]);
    categories.value = catRes.data; accounts.value = accRes.data; piggyBanks.value = pbRes.data;
    transactions.value = txRes.data.items.filter(t => t.type !== 'TRANSFER' && getExactYear(t.date) === currentYear.value && getExactMonth(t.date) === currentMonth.value);

    for (const c of categories.value) {
      if (c.group === 'EXPENSE') {
        try {
          const { data: lim } = await api.get(`/limits/status/${c.id}?year=${currentYear.value}&month=${currentMonth.value}`);
          limitsMap.value[c.id] = lim;
        } catch { limitsMap.value[c.id] = null; }
      }
    }
  } catch (err) { console.error(err); }
}

function askDelete(id) {
  deleteTxId.value = id;
  txToDelete.value = transactions.value.find(t => t.id === id) || null;
  if (accounts.value.length > 0) selectedRefundAccountId.value = accounts.value[0].id;
}
function cancelDelete() { deleteTxId.value = null; txToDelete.value = null; }

async function confirmDelete(withRefund = true) {
  if (!deleteTxId.value) return;
  try {
    let url = `/transactions/${deleteTxId.value}`;
    if (isAccountMissing.value && withRefund && selectedRefundAccountId.value) url += `?target_account_id=${selectedRefundAccountId.value}`;
    await api.delete(url);
    cancelDelete();
    await loadMonthData();
  } catch (err) { alert(err.response?.data?.detail || 'Ошибка при удалении'); }
}

onMounted(loadMonthData);
</script>