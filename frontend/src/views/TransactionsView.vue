<template>
  <div class="space-y-6">
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

      <div class="flex gap-2">
        <button
          @click="openPlanModal"
          class="bg-white dark:bg-theme-dark-card text-slate-700 dark:text-purple-200 border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-50 dark:hover:bg-theme-dark-hover text-xs px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 shadow-sm"
        >
          <Target class="w-4 h-4" /> Запланировать расходы
        </button>
        <button
          @click="showAnalyticsModal = true"
          class="bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-200 border border-purple-200 dark:border-purple-800 hover:bg-purple-200 text-xs px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 shadow-sm"
        >
          <BarChart3 class="w-4 h-4" /> Аналитика
        </button>
      </div>
    </div>

    <!-- Сетка Календаря -->
    <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-4 shadow-sm">
      <div class="grid grid-cols-7 gap-2 mb-2 text-center text-xs font-black uppercase text-theme-light-muted dark:text-theme-dark-muted">
        <div v-for="w in weekDays" :key="w">{{ w }}</div>
      </div>

      <div class="grid grid-cols-7 gap-2">
        <div
          v-for="(cell, idx) in calendarCells"
          :key="idx"
          @click="cell.isCurrentMonth && selectDay(cell.day)"
          :class="[
            cell.isCurrentMonth
              ? 'bg-theme-light-card dark:bg-theme-dark-card border-theme-light-border dark:border-theme-dark-border cursor-pointer hover:border-purple-500 dark:hover:border-purple-400 relative overflow-hidden'
              : 'opacity-25 pointer-events-none border-transparent',
            selectedDay === cell.day ? 'ring-2 ring-purple-600 dark:ring-purple-400' : ''
          ]"
          class="border rounded-xl min-h-24 p-2 flex flex-col justify-between transition-all"
        >
          <div class="flex justify-between items-start z-10">
            <span class="text-xs font-bold" :class="cell.isToday ? 'bg-theme-accent-primary text-white w-5 h-5 rounded-full flex items-center justify-center' : 'text-slate-700 dark:text-purple-300'">
              {{ cell.day }}
            </span>
            <div v-if="cell.hasPlanned" class="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></div>
          </div>

          <div v-if="cell.isCurrentMonth && cell.totals" class="space-y-1 font-mono text-[11px] leading-tight mt-1 z-10 relative">
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

    <!-- Модалка операций выбранного дня -->
    <div v-if="selectedDay" @click.self="selectedDay = null" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-lg p-6 max-h-[85vh] flex flex-col">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-theme-light-border dark:border-theme-dark-border">
          <h3 class="font-black text-base text-slate-800 dark:text-purple-100">
            Операции за {{ selectedDay }} {{ monthNames[currentMonth - 1] }}
          </h3>
          <button @click="selectedDay = null" class="text-xs font-bold px-2 py-1 rounded hover:bg-purple-100 dark:hover:bg-purple-900/60">Закрыть</button>
        </div>

        <div class="flex-1 overflow-y-auto divide-y divide-theme-light-border dark:divide-theme-dark-border">
          <div v-if="dayTransactions.length === 0" class="py-8 text-center text-xs text-theme-light-muted dark:text-theme-dark-muted">
            В этот день операций нет
          </div>
          <div v-for="t in dayTransactions" :key="t.id" class="py-3 flex justify-between items-center text-sm" :class="{'opacity-60 grayscale': t.isPlanned}">
            <div>
              <p class="font-bold text-slate-800 dark:text-purple-200">
                <span v-if="t.isPlanned" class="text-[10px] bg-purple-100 text-purple-800 px-1.5 py-0.5 rounded mr-1">ПЛАН</span>
                {{ translateType(t.type) }}
              </p>
              <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted">
                {{ t.note || 'Без описания' }}
                <span v-if="!t.isPlanned">• {{ t.author === 'HUSBAND' ? 'Любими Муж' : 'КошкоЖена' }}</span>
              </p>
            </div>
            <div class="text-right">
              <p class="font-mono font-bold" :class="isIncomeType(t.type) ? 'text-emerald-500' : 'text-rose-500'">
                {{ isIncomeType(t.type) ? '+' : '-' }}{{ t.amount }} {{ t.currency }}
              </p>
              <button v-if="!t.isPlanned" @click="askDelete(t.id)" class="text-[11px] text-red-500 hover:underline">Удалить</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка Планирования -->
    <div v-if="showPlanModal" @click.self="showPlanModal = false" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-xl p-6 flex flex-col max-h-[80vh]">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-black text-lg text-slate-800 dark:text-purple-100">План расходов на месяц</h3>
          <button @click="showPlanModal = false" class="text-xs font-bold px-2 py-1">Закрыть</button>
        </div>

        <div v-if="isForecastLoading" class="flex-1 flex justify-center items-center py-10">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
        <div v-else class="flex-1 overflow-y-auto space-y-3 pr-2">
          <div v-for="cat in expenseCategories" :key="cat.id" class="p-3 bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl flex justify-between items-center">
            <div>
              <p class="font-bold text-sm text-slate-800 dark:text-purple-100">{{ cat.name }}</p>
              <p class="text-[11px] text-theme-light-muted dark:text-theme-dark-muted mt-0.5">
                Прогноз ИИ: {{ forecasts[cat.id]?.predicted_next_month || 0 }} {{ settings.baseCurrency }}
              </p>
            </div>
            <div class="text-right">
              <span v-if="cat.default_amount" class="text-sm font-black font-mono text-rose-500 bg-rose-50 dark:bg-rose-950/40 px-2 py-1 rounded-lg">
                {{ cat.default_amount }}
              </span>
              <span v-else class="text-xs text-slate-400 italic">Не запланировано</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка удаления (осталась прежней) -->
    <div v-if="deleteTxId" @click.self="deleteTxId = null" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-[60]">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6 text-center">
        <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-2">Удалить операцию?</h3>
        <p class="text-sm text-theme-light-muted dark:text-theme-dark-muted mb-6">Это действие нельзя отменить. Баланс счёта будет пересчитан.</p>
        <div class="flex justify-center gap-3">
          <button @click="deleteTxId = null" class="px-5 py-2.5 text-sm font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition">Отмена</button>
          <button @click="confirmDelete" class="px-5 py-2.5 text-sm font-bold bg-red-500 hover:bg-red-600 text-white rounded-xl shadow-md transition">Удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ChevronLeft, ChevronRight, BarChart3, Target } from 'lucide-vue-next';
import api from '@/api';
import { useSettingsStore } from '@/stores/settings';

const settings = useSettingsStore();
const now = new Date();
const currentYear = ref(now.getFullYear());
const currentMonth = ref(now.getMonth() + 1);
const selectedDay = ref(null);
const showAnalyticsModal = ref(false);
const showPlanModal = ref(false);
const analyticsData = ref(null);
const deleteTxId = ref(null);

const transactions = ref([]);
const categories = ref([]);
const accounts = ref([]);
const forecasts = ref({});
const isForecastLoading = ref(false);

const monthNames = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];
const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

function isIncomeType(type) { return type.startsWith('INCOME'); }

function translateType(type) {
  const map = {
    EXPENSE_PLANNED: 'Плановый расход', EXPENSE_IMPULSE: 'Внеплановый расход',
    INCOME_PLANNED: 'Плановый доход', INCOME_UNPLANNED: 'Внеплановый доход',
    INCOME: 'Доход', INVESTMENT: 'Инвестиции', TRANSFER: 'Перевод'
  };
  return map[type] || type;
}

const expenseCategories = computed(() => categories.value.filter(c => c.group === 'EXPENSE'));

// Генерация плановых операций на лету
const plannedTransactions = computed(() => {
  const planned = [];
  categories.value.forEach(cat => {
    if (!cat.default_amount || cat.frequency === 'NONE') return;
    const days = [];
    const daysInMonth = new Date(currentYear.value, currentMonth.value, 0).getDate();

    if (cat.frequency === 'DAILY') {
      for(let i=1; i<=daysInMonth; i++) days.push(i);
    } else if (cat.frequency === 'WEEKLY') {
      for(let i=1; i<=daysInMonth; i++) {
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
    const curr = acc ? acc.currency : 'RUB';

    days.forEach(d => {
      planned.push({
        id: `plan-${cat.id}-${d}`,
        type: cat.group === 'INCOME' ? 'INCOME_PLANNED' : 'EXPENSE_PLANNED',
        category_id: cat.id,
        amount: cat.default_amount,
        currency: curr,
        date: new Date(currentYear.value, currentMonth.value - 1, d, 12).toISOString(),
        isPlanned: true,
        note: `План: ${cat.name}`
      });
    });
  });
  return planned;
});

const calendarCells = computed(() => {
  const daysInMonth = new Date(currentYear.value, currentMonth.value, 0).getDate();
  const firstDayIndex = (new Date(currentYear.value, currentMonth.value - 1, 1).getDay() + 6) % 7;
  const cells = [];

  for (let i = 0; i < firstDayIndex; i++) cells.push({ day: 0, isCurrentMonth: false });

  for (let d = 1; d <= daysInMonth; d++) {
    // Берем реальные + плановые операции за этот день
    const realDayTxs = transactions.value.filter(t => new Date(t.date).getDate() === d);
    const planDayTxs = plannedTransactions.value.filter(t => new Date(t.date).getDate() === d);

    let inc = 0, exp = 0;

    // Считаем суммы конвертируя на лету
    [...realDayTxs, ...planDayTxs].forEach(t => {
      const converted = settings.convert(t.amount, t.currency);
      if (isIncomeType(t.type)) inc += converted;
      else exp += converted;
    });

    const isToday = (now.getFullYear() === currentYear.value && now.getMonth() + 1 === currentMonth.value && now.getDate() === d);

    cells.push({
      day: d,
      isCurrentMonth: true,
      isToday,
      hasPlanned: planDayTxs.length > 0,
      totals: { income: inc, expense: exp }
    });
  }
  return cells;
});

const dayTransactions = computed(() => {
  if (!selectedDay.value) return [];
  const real = transactions.value.filter(t => new Date(t.date).getDate() === selectedDay.value);
  const plan = plannedTransactions.value.filter(t => new Date(t.date).getDate() === selectedDay.value);
  return [...real, ...plan]; // Показываем и реальные и плановые
});

function selectDay(d) { selectedDay.value = d; }
function prevMonth() { if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value--; } else { currentMonth.value--; } loadMonthData(); }
function nextMonth() { if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++; } else { currentMonth.value++; } loadMonthData(); }

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
  const [txRes, catRes, accRes] = await Promise.all([
    api.get('/transactions?limit=200&offset=0'),
    api.get('/categories'),
    api.get('/accounts')
  ]);
  categories.value = catRes.data;
  accounts.value = accRes.data;
  transactions.value = txRes.data.items.filter(t => {
    const dt = new Date(t.date);
    return dt.getFullYear() === currentYear.value && dt.getMonth() + 1 === currentMonth.value;
  });
}

function askDelete(id) { deleteTxId.value = id; }
async function confirmDelete() {
  if (!deleteTxId.value) return;
  await api.delete(`/transactions/${deleteTxId.value}`);
  deleteTxId.value = null;
  await loadMonthData();
}

onMounted(loadMonthData);
</script>