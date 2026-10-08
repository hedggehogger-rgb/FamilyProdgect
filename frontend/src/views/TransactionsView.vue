<template>
  <div class="space-y-6">
    <!-- Верхняя панель: Месяц + кнопка Аналитики -->
    <div class="flex flex-wrap items-center justify-between gap-4 bg-theme-light-surface dark:bg-theme-dark-surface p-4 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm">
      <div class="flex items-center gap-3">
        <button @click="prevMonth" class="p-2 rounded-xl hover:bg-theme-light-hover dark:hover:bg-theme-dark-hover transition">
          <ChevronLeft class="w-5 h-5 text-purple-600 dark:text-purple-400" />
        </button>
        <span class="text-base font-black text-slate-800 dark:text-purple-100 min-w-36 text-center">
          {{ monthNames[currentMonth - 1] }} {{ currentYear }}
        </span>
        <button @click="nextMonth" class="p-2 rounded-xl hover:bg-theme-light-hover dark:hover:bg-theme-dark-hover transition">
          <ChevronRight class="w-5 h-5 text-purple-600 dark:text-purple-400" />
        </button>
      </div>

      <button
        @click="showAnalyticsModal = true"
        class="bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-200 border border-purple-200 dark:border-purple-800 hover:bg-purple-200 text-xs px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2"
      >
        <BarChart3 class="w-4 h-4" />
        Аналитика за месяц
      </button>
    </div>

    <!-- Сетка Календаря -->
    <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-4 shadow-sm">
      <!-- Заголовки дней недели -->
      <div class="grid grid-cols-7 gap-2 mb-2 text-center text-xs font-black uppercase text-theme-light-muted dark:text-theme-dark-muted">
        <div v-for="w in weekDays" :key="w">{{ w }}</div>
      </div>

      <!-- Ячейки календаря -->
      <div class="grid grid-cols-7 gap-2">
        <div
          v-for="(cell, idx) in calendarCells"
          :key="idx"
          @click="cell.isCurrentMonth && selectDay(cell.day)"
          :class="[
            cell.isCurrentMonth
              ? 'bg-theme-light-card dark:bg-theme-dark-card border-theme-light-border dark:border-theme-dark-border cursor-pointer hover:border-purple-500 dark:hover:border-purple-400'
              : 'opacity-25 pointer-events-none border-transparent',
            selectedDay === cell.day ? 'ring-2 ring-purple-600 dark:ring-purple-400' : ''
          ]"
          class="border rounded-xl min-h-24 p-2 flex flex-col justify-between transition-all"
        >
          <div class="flex justify-between items-start">
            <span class="text-xs font-bold" :class="cell.isToday ? 'bg-theme-accent-primary text-white w-5 h-5 rounded-full flex items-center justify-center' : 'text-slate-700 dark:text-purple-300'">
              {{ cell.day }}
            </span>
          </div>

          <!-- Сводные индикаторы дня -->
          <div v-if="cell.isCurrentMonth && cell.totals" class="space-y-1 font-mono text-[11px] leading-tight mt-1">
            <p v-if="cell.totals.income > 0" class="text-emerald-600 dark:text-emerald-400 font-bold truncate">
              +{{ Math.round(cell.totals.income) }}
            </p>
            <p v-if="cell.totals.expense > 0" class="text-rose-600 dark:text-rose-400 font-bold truncate">
              -{{ Math.round(cell.totals.expense) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка/Панель операций выбранного дня -->
    <div v-if="selectedDay" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-lg p-6 max-h-[85vh] flex flex-col">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-theme-light-border dark:border-theme-dark-border">
          <h3 class="font-black text-base text-slate-800 dark:text-purple-100">
            Операции за {{ selectedDay }} {{ monthNames[currentMonth - 1] }}
          </h3>
          <button @click="selectedDay = null" class="text-xs font-bold px-2 py-1 rounded hover:bg-purple-100 dark:hover:bg-purple-900/60">Закрыть</button>
        </div>

        <div class="flex-1 overflow-y-auto divide-y divide-theme-light-border dark:divide-theme-dark-border">
          <div v-if="dayTransactions.length === 0" class="py-8 text-center text-xs text-theme-light-muted dark:text-theme-dark-muted">
            В этот день операций не было
          </div>

          <div v-for="t in dayTransactions" :key="t.id" class="py-3 flex justify-between items-center text-sm">
            <div>
              <p class="font-bold text-slate-800 dark:text-purple-200">
                {{ translateType(t.type) }}
              </p>
              <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted">
                Счёт: {{ t.account_id }} • {{ t.author === 'HUSBAND' ? 'Любими Муж' : 'КошкоЖена' }}
              </p>
            </div>
            <div class="text-right">
              <p class="font-mono font-bold" :class="isIncomeType(t.type) ? 'text-emerald-500' : 'text-rose-500'">
                {{ isIncomeType(t.type) ? '+' : '-' }}{{ t.amount }} {{ t.currency }}
              </p>
              <button @click="deleteTx(t.id)" class="text-[11px] text-red-500 hover:underline">
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка Аналитики -->
    <div v-if="showAnalyticsModal" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-xl p-6">
        <div class="flex justify-between items-center mb-6">
          <h3 class="font-black text-lg text-slate-800 dark:text-purple-100">
            📊 Аналитика: {{ monthNames[currentMonth - 1] }} {{ currentYear }}
          </h3>
          <button @click="showAnalyticsModal = false" class="text-xs font-bold px-2 py-1">Закрыть</button>
        </div>

        <div v-if="analyticsData" class="space-y-4">
          <div class="grid grid-cols-3 gap-3">
            <div class="p-4 rounded-xl bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800 text-center">
              <span class="text-xs text-theme-light-muted dark:text-theme-dark-muted font-bold">Доходы</span>
              <p class="text-base font-black text-emerald-500 mt-1 font-mono">+{{ analyticsData.total_income }}</p>
            </div>
            <div class="p-4 rounded-xl bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800 text-center">
              <span class="text-xs text-theme-light-muted dark:text-theme-dark-muted font-bold">Расходы</span>
              <p class="text-base font-black text-rose-500 mt-1 font-mono">-{{ analyticsData.total_expense }}</p>
            </div>
            <div class="p-4 rounded-xl bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800 text-center">
              <span class="text-xs text-theme-light-muted dark:text-theme-dark-muted font-bold">Остаток</span>
              <p class="text-base font-black mt-1 font-mono" :class="analyticsData.net_savings >= 0 ? 'text-purple-600' : 'text-rose-500'">
                {{ analyticsData.net_savings }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ChevronLeft, ChevronRight, BarChart3 } from 'lucide-vue-next';
import api from '@/api';

const now = new Date();
const currentYear = ref(now.getFullYear());
const currentMonth = ref(now.getMonth() + 1);
const selectedDay = ref(null);
const showAnalyticsModal = ref(false);
const analyticsData = ref(null);

const transactions = ref([]);

const monthNames = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];
const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

function isIncomeType(type) {
  return type.startsWith('INCOME');
}

function translateType(type) {
  const map = {
    EXPENSE_PLANNED: 'Плановый расход',
    EXPENSE_IMPULSE: 'Внеплановый расход',
    INCOME_PLANNED: 'Плановый доход',
    INCOME_UNPLANNED: 'Внеплановый доход',
    INCOME: 'Доход',
    INVESTMENT: 'Инвестиции',
    TRANSFER: 'Перевод'
  };
  return map[type] || type;
}

const calendarCells = computed(() => {
  const daysInMonth = new Date(currentYear.value, currentMonth.value, 0).getDate();
  const firstDayIndex = (new Date(currentYear.value, currentMonth.value - 1, 1).getDay() + 6) % 7;
  const cells = [];

  for (let i = 0; i < firstDayIndex; i++) {
    cells.push({ day: 0, isCurrentMonth: false });
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const dayTxs = transactions.value.filter(t => new Date(t.date).getDate() === d);
    let inc = 0, exp = 0;
    dayTxs.forEach(t => {
      if (isIncomeType(t.type)) inc += Number(t.amount);
      else exp += Number(t.amount);
    });

    const isToday = (
      now.getFullYear() === currentYear.value &&
      now.getMonth() + 1 === currentMonth.value &&
      now.getDate() === d
    );

    cells.push({
      day: d,
      isCurrentMonth: true,
      isToday,
      totals: { income: inc, expense: exp }
    });
  }

  return cells;
});

const dayTransactions = computed(() => {
  if (!selectedDay.value) return [];
  return transactions.value.filter(t => new Date(t.date).getDate() === selectedDay.value);
});

function selectDay(d) {
  selectedDay.value = d;
}

function prevMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12;
    currentYear.value--;
  } else {
    currentMonth.value--;
  }
  loadMonthData();
}

function nextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1;
    currentYear.value++;
  } else {
    currentMonth.value++;
  }
  loadMonthData();
}

async function loadMonthData() {
  const { data } = await api.get('/transactions?limit=100&offset=0');
  transactions.value = data.items.filter(t => {
    const dt = new Date(t.date);
    return dt.getFullYear() === currentYear.value && dt.getMonth() + 1 === currentMonth.value;
  });

  try {
    const { data: rep } = await api.get(`/analytics/monthly-report?year=${currentYear.value}&month=${currentMonth.value}&currency=RUB`);
    analyticsData.value = rep;
  } catch (e) {
    analyticsData.value = null;
  }
}

async function deleteTx(id) {
  if (!confirm('Удалить операцию?')) return;
  await api.delete(`/transactions/${id}`);
  await loadMonthData();
}

onMounted(loadMonthData);
</script>