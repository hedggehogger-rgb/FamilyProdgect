<template>
  <div class="space-y-6">
    <!-- Шапка календаря -->
    <div class="flex flex-wrap items-center justify-between gap-4 bg-theme-light-surface dark:bg-theme-dark-surface p-4 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm">
      <div class="flex items-center gap-3">
        <button @click="prevMonth" class="p-2 rounded-xl hover:bg-theme-light-hover dark:hover:bg-theme-dark-hover transition">
          <ChevronLeft class="w-5 h-5 text-purple-600 dark:text-purple-400" />
        </button>
        <span class="text-base font-black text-slate-800 dark:text-purple-100 min-w-36 text-center">
          {{ MONTH_NAMES[currentMonth - 1] }} {{ currentYear }}
        </span>
        <button @click="nextMonth" class="p-2 rounded-xl hover:bg-theme-light-hover dark:hover:bg-theme-dark-hover transition">
          <ChevronRight class="w-5 h-5 text-purple-600 dark:text-purple-400" />
        </button>
      </div>

      <div class="flex gap-2">
        <button @click="openPlanModal" class="bg-white dark:bg-theme-dark-card text-slate-700 dark:text-purple-200 border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-50 dark:hover:bg-theme-dark-hover text-xs px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 shadow-sm">
          <Target class="w-4 h-4" /> Запланировать расходы
        </button>
        <button @click="showAnalyticsModal = true" class="bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-200 border border-purple-200 dark:border-purple-800 hover:bg-purple-200 text-xs px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 shadow-sm">
          <BarChart3 class="w-4 h-4" /> Аналитика за {{ MONTH_NAMES[currentMonth - 1] }}
        </button>
      </div>
    </div>

    <!-- Календарная сетка -->
    <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-4 shadow-sm">
      <div class="grid grid-cols-7 gap-2 mb-2 text-center text-xs font-black uppercase text-theme-light-muted dark:text-theme-dark-muted">
        <div v-for="w in WEEK_DAYS" :key="w">{{ w }}</div>
      </div>
      <div class="grid grid-cols-7 gap-2">
        <div
          v-for="(cell, idx) in calendarCells"
          :key="idx"
          @click="cell.isCurrentMonth && (selectedDay = cell.day)"
          :class="[
            cell.isCurrentMonth
              ? 'bg-theme-light-card dark:bg-theme-dark-card border-theme-light-border dark:border-theme-dark-border cursor-pointer hover:border-purple-500 relative overflow-hidden'
              : 'opacity-25 pointer-events-none border-transparent',
            selectedDay === cell.day ? 'ring-2 ring-purple-600' : ''
          ]"
          class="border rounded-xl min-h-24 p-2 flex flex-col justify-between transition-all"
        >
          <div class="flex justify-between items-start z-10">
            <span class="text-xs font-bold" :class="cell.isToday ? 'bg-theme-accent-primary text-white w-5 h-5 rounded-full flex items-center justify-center' : 'text-slate-700 dark:text-purple-300'">
              {{ cell.day }}
            </span>
            <div v-if="cell.hasPlanned" class="w-2 h-2 rounded-full bg-purple-500 animate-pulse" title="Есть запланированные операции"></div>
          </div>
          <div v-if="cell.isCurrentMonth && cell.totals" class="space-y-1 font-mono text-[11px] leading-tight mt-1 z-10 relative">
            <p v-if="cell.totals.income > 0" class="text-emerald-600 font-bold truncate">
              +{{ Math.round(cell.totals.income) }} {{ settings.getSymbol(settings.baseCurrency) }}
            </p>
            <p v-if="cell.totals.expense > 0" class="text-rose-600 font-bold truncate">
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
      @close="selectedDay = null"
      @ask-delete="askDelete"
    />

    <BudgetPlanModal
      :show="showPlanModal"
      :loading="isForecastLoading"
      :categories="expenseCategories"
      :forecasts="forecasts"
      :monthName="MONTH_NAMES[currentMonth - 1]"
      :year="currentYear"
      :getSpentForCat="getSpentInCurrentMonthForCat"
      @close="showPlanModal = false"
    />

    <MonthAnalyticsModal
      :show="showAnalyticsModal"
      :monthName="MONTH_NAMES[currentMonth - 1]"
      :year="currentYear"
      :totalIncome="monthTotalIncome"
      :totalExpense="monthTotalExpense"
      :savings="monthSavings"
      :categoryStats="categoryStats"
      @close="showAnalyticsModal = false"
      @select-category="detailCategory = $event"
    />

    <CategoryDetailModal
      :category="detailCategory"
      :monthName="MONTH_NAMES[currentMonth - 1]"
      :transactions="categoryTransactions"
      @close="detailCategory = null"
    />

    <!-- Модальное окно удаления операции с проверкой наличия счёта -->
    <Teleport to="body">
      <div
        v-if="deleteTxId"
        @click.self="cancelDelete"
        class="fixed inset-0 bg-slate-950/60 backdrop-blur-md flex items-center justify-center p-4 z-[70]"
      >
        <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-md p-6">

          <!-- Случай 1: Счёт был удалён -->
          <div v-if="isAccountMissing" class="text-center">
            <div class="w-12 h-12 rounded-2xl bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center mx-auto mb-3 shadow-sm">
              <AlertTriangle class="w-6 h-6" />
            </div>

            <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-2">
              Счёт операции был удалён
            </h3>

            <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted mb-4 leading-relaxed">
              Счёт, с которого списывалась эта операция, больше не существует.
              Куда зачислить отменяемые средства
              <strong class="font-mono text-purple-600 dark:text-purple-300">
                ({{ formatMoney(txToDelete?.amount) }} {{ settings.getSymbol(txToDelete?.currency) }})
              </strong>?
            </p>

            <div class="text-left mb-6">
              <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1.5">
                Выберите действующий счёт для возврата:
              </label>
              <CustomSelect
                v-model="selectedRefundAccountId"
                :options="accountOptions"
                placeholder="Выберите счёт"
              />
            </div>

            <div class="flex flex-col sm:flex-row justify-end gap-2 text-xs font-bold">
              <button
                type="button"
                @click="cancelDelete"
                class="px-4 py-2.5 rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition text-slate-700 dark:text-purple-200"
              >
                Отмена
              </button>
              <button
                type="button"
                @click="confirmDelete(false)"
                class="px-4 py-2.5 rounded-xl border border-rose-300 dark:border-rose-900/60 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition"
              >
                Удалить без зачисления
              </button>
              <button
                type="button"
                @click="confirmDelete(true)"
                :disabled="!selectedRefundAccountId"
                class="px-4 py-2.5 bg-theme-accent-primary hover:bg-theme-accent-hover text-white rounded-xl shadow-md transition disabled:opacity-50"
              >
                Зачислить и удалить
              </button>
            </div>
          </div>

          <!-- Случай 2: Счёт существует (стандартное удаление) -->
          <div v-else class="text-center">
            <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-2">
              Удалить операцию?
            </h3>
            <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted mb-6">
              Средства будут возвращены на счёт
              <strong class="text-purple-600 dark:text-purple-300">
                "{{ getAccountName(txToDelete?.account_id) }}"
              </strong>.
            </p>

            <div class="flex justify-center gap-3">
              <button
                type="button"
                @click="cancelDelete"
                class="px-5 py-2.5 text-xs font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition"
              >
                Отмена
              </button>
              <button
                type="button"
                @click="confirmDelete(true)"
                class="px-5 py-2.5 text-xs font-bold bg-rose-500 hover:bg-rose-600 text-white rounded-xl shadow-md transition"
              >
                Удалить
              </button>
            </div>
          </div>

        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ChevronLeft, ChevronRight, BarChart3, Target, AlertTriangle } from 'lucide-vue-next';
import api from '@/api';
import { useSettingsStore } from '@/stores/settings';
import { MONTH_NAMES, WEEK_DAYS, getExactDay, getExactMonth, getExactYear } from '@/utils/formatters';
import CustomSelect from '@/components/CustomSelect.vue';

import DayTransactionsModal from './transactions/DayTransactionsModal.vue';
import BudgetPlanModal from './transactions/BudgetPlanModal.vue';
import MonthAnalyticsModal from './transactions/MonthAnalyticsModal.vue';
import CategoryDetailModal from './transactions/CategoryDetailModal.vue';

const settings = useSettingsStore();
const now = new Date();
const currentYear = ref(now.getFullYear());
const currentMonth = ref(now.getMonth() + 1);
const selectedDay = ref(null);
const showAnalyticsModal = ref(false);
const showPlanModal = ref(false);
const detailCategory = ref(null);

// Состояния удаления
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

function isIncomeType(type) { return type.startsWith('INCOME'); }

const expenseCategories = computed(() => categories.value.filter(c => c.group === 'EXPENSE'));

const accountOptions = computed(() =>
  accounts.value.map(a => ({
    label: `${a.name} (${settings.getSymbol(a.currency)})`,
    value: a.id
  }))
);

const isAccountMissing = computed(() => {
  if (!txToDelete.value) return false;
  return !accounts.value.some(a => a.id === txToDelete.value.account_id);
});

function getAccountName(id) {
  if (!id) return 'Неизвестный счёт';
  const acc = accounts.value.find(a => a.id === id);
  return acc ? acc.name : 'Удалённый счёт';
}

function formatMoney(val) {
  if (val === null || val === undefined || isNaN(val)) return '0';
  return Number(val).toLocaleString('ru-RU');
}

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
        if (d === 0) d = 7;
        if (d === cat.day_of_week) days.push(i);
      }
    } else if (cat.frequency === 'MONTHLY') {
      days.push(cat.day_of_month <= daysInMonth ? cat.day_of_month : daysInMonth);
    } else if (cat.frequency === 'QUARTERLY') {
      if (currentMonth.value % 3 === (cat.recurrence_month || 1) % 3) {
        days.push(cat.day_of_month <= daysInMonth ? cat.day_of_month : daysInMonth);
      }
    } else if (cat.frequency === 'ANNUALLY') {
      if (currentMonth.value === cat.recurrence_month) {
        days.push(cat.day_of_month <= daysInMonth ? cat.day_of_month : daysInMonth);
      }
    }

    const acc = accounts.value.find(a => a.id === cat.default_account_id);
    days.forEach(d => {
      planned.push({
        id: `plan-cat-${cat.id}-${d}`,
        type: cat.group === 'INCOME' ? 'INCOME_PLANNED' : 'EXPENSE_PLANNED',
        category_id: cat.id,
        amount: cat.default_amount,
        currency: acc ? acc.currency : 'RUB',
        date: `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}T12:00:00`,
        isPlanned: true,
        is_executed: false,
        note: `План: ${cat.name}`
      });
    });
  });

  piggyBanks.value.forEach(pb => {
    if (!pb.is_auto_replenish || pb.is_completed) return;
    const currentYM = `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}`;
    if (pb.skip_until_month === currentYM) return;
    let d = pb.auto_replenish_day || 1;
    if (d <= daysInMonth) {
      planned.push({
        id: `plan-pb-${pb.id}-${d}`,
        type: 'EXPENSE_PLANNED',
        category_id: null,
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
  const firstDayIndex = (new Date(currentYear.value, currentMonth.value - 1, 1).getDay() + 6) % 7;
  const cells = [];
  for (let i = 0; i < firstDayIndex; i++) cells.push({ day: 0, isCurrentMonth: false });

  for (let d = 1; d <= daysInMonth; d++) {
    const realDayTxs = transactions.value.filter(t => getExactDay(t.date) === d);
    const planDayTxs = plannedTransactions.value.filter(t => getExactDay(t.date) === d);
    let inc = 0, exp = 0;

    [...realDayTxs, ...planDayTxs].forEach(t => {
      const converted = settings.convert(t.amount, t.currency);
      if (isIncomeType(t.type)) inc += converted; else exp += converted;
    });
    const isToday = (now.getFullYear() === currentYear.value && now.getMonth() + 1 === currentMonth.value && now.getDate() === d);
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
  const real = transactions.value.filter(t => getExactDay(t.date) === selectedDay.value);
  const plan = plannedTransactions.value.filter(t => getExactDay(t.date) === selectedDay.value);
  return [...real, ...plan];
});

const monthTotalIncome = computed(() => {
  let sum = 0;
  transactions.value.forEach(t => {
    if (isIncomeType(t.type) && t.is_executed !== false) sum += settings.convert(t.amount, t.currency);
  });
  return Math.round(sum);
});

const monthTotalExpense = computed(() => {
  let sum = 0;
  transactions.value.forEach(t => {
    if (!isIncomeType(t.type) && t.type !== 'TRANSFER' && t.is_executed !== false) sum += settings.convert(t.amount, t.currency);
  });
  return Math.round(sum);
});

const monthSavings = computed(() => monthTotalIncome.value - monthTotalExpense.value);

const categoryStats = computed(() => {
  const totalExp = monthTotalExpense.value || 1;
  const res = [];
  expenseCategories.value.forEach(cat => {
    let spent = 0;
    transactions.value.forEach(t => {
      if (t.category_id === cat.id && !isIncomeType(t.type) && t.is_executed !== false) {
        spent += settings.convert(t.amount, t.currency);
      }
    });
    if (spent > 0) {
      res.push({
        cat,
        spent: Math.round(spent),
        pct: Math.min(100, Math.round((spent / totalExp) * 100)),
        limit: limitsMap.value[cat.id] || null
      });
    }
  });
  return res.sort((a, b) => b.spent - a.spent);
});

const categoryTransactions = computed(() => {
  if (!detailCategory.value) return [];
  return transactions.value.filter(t => t.category_id === detailCategory.value.id);
});

function getSpentInCurrentMonthForCat(catId) {
  let sum = 0;
  transactions.value.forEach(t => {
    if (t.category_id === catId && !isIncomeType(t.type) && t.is_executed !== false) {
      sum += settings.convert(t.amount, t.currency);
    }
  });
  return Math.round(sum);
}

function prevMonth() {
  if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value--; }
  else { currentMonth.value--; }
  loadMonthData();
}

function nextMonth() {
  if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++; }
  else { currentMonth.value++; }
  loadMonthData();
}

async function openPlanModal() {
  showPlanModal.value = true;
  isForecastLoading.value = true;
  const promises = expenseCategories.value.map(c =>
    api.get(`/budget/forecast/${c.id}?target_currency=${settings.baseCurrency}`)
      .then(res => forecasts.value[c.id] = res.data)
      .catch(() => {})
  );
  await Promise.all(promises);
  isForecastLoading.value = false;
}

async function loadMonthData() {
  try {
    const [txRes, catRes, accRes, pbRes] = await Promise.all([
      api.get('/transactions?limit=500&offset=0'),
      api.get('/categories'),
      api.get('/accounts'),
      api.get('/piggy-banks')
    ]);
    categories.value = catRes.data;
    accounts.value = accRes.data;
    piggyBanks.value = pbRes.data;

    transactions.value = txRes.data.items.filter(t =>
      getExactYear(t.date) === currentYear.value &&
      getExactMonth(t.date) === currentMonth.value
    );

    for (const c of categories.value) {
      if (c.group === 'EXPENSE') {
        try {
          const { data: lim } = await api.get(`/limits/status/${c.id}?year=${currentYear.value}&month=${currentMonth.value}`);
          limitsMap.value[c.id] = lim;
        } catch (e) {
          limitsMap.value[c.id] = null;
        }
      }
    }
  } catch (err) {
    console.error('Ошибка загрузки данных за месяц:', err);
  }
}

function askDelete(id) {
  deleteTxId.value = id;
  const tx = transactions.value.find(t => t.id === id);
  txToDelete.value = tx || null;

  if (accounts.value.length > 0) {
    selectedRefundAccountId.value = accounts.value[0].id;
  }
}

function cancelDelete() {
  deleteTxId.value = null;
  txToDelete.value = null;
}

async function confirmDelete(withRefund = true) {
  if (!deleteTxId.value) return;
  try {
    let url = `/transactions/${deleteTxId.value}`;
    if (isAccountMissing.value && withRefund && selectedRefundAccountId.value) {
      url += `?target_account_id=${selectedRefundAccountId.value}`;
    }

    await api.delete(url);
    cancelDelete();
    await loadMonthData();
  } catch (err) {
    alert(err.response?.data?.detail || 'Не удалось удалить операцию');
  }
}

onMounted(loadMonthData);
</script>