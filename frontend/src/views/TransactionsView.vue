<template>
  <div class="space-y-6">
    <!-- Шапка календаря -->
    <div class="flex flex-wrap items-center justify-between gap-4 bg-theme-light-surface dark:bg-theme-dark-surface p-4 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm">
      <div class="flex items-center gap-3">
        <button @click="prevMonth" class="p-2 rounded-xl hover:bg-theme-light-hover dark:hover:bg-theme-dark-hover transition"><ChevronLeft class="w-5 h-5 text-purple-600 dark:text-purple-400" /></button>
        <span class="text-base font-black text-slate-800 dark:text-purple-100 min-w-36 text-center">{{ monthNames[currentMonth - 1] }} {{ currentYear }}</span>
        <button @click="nextMonth" class="p-2 rounded-xl hover:bg-theme-light-hover dark:hover:bg-theme-dark-hover transition"><ChevronRight class="w-5 h-5 text-purple-600 dark:text-purple-400" /></button>
      </div>

      <div class="flex gap-2">
        <button @click="openPlanModal" class="bg-white dark:bg-theme-dark-card text-slate-700 dark:text-purple-200 border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-50 dark:hover:bg-theme-dark-hover text-xs px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 shadow-sm"><Target class="w-4 h-4" /> Запланировать расходы</button>
        <button @click="openAnalyticsModal" class="bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-200 border border-purple-200 dark:border-purple-800 hover:bg-purple-200 text-xs px-4 py-2.5 rounded-xl font-bold transition flex items-center gap-2 shadow-sm"><BarChart3 class="w-4 h-4" /> Аналитика за {{ monthNames[currentMonth - 1] }}</button>
      </div>
    </div>

    <!-- Календарная сетка -->
    <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-4 shadow-sm">
      <div class="grid grid-cols-7 gap-2 mb-2 text-center text-xs font-black uppercase text-theme-light-muted dark:text-theme-dark-muted"><div v-for="w in weekDays" :key="w">{{ w }}</div></div>
      <div class="grid grid-cols-7 gap-2">
        <div v-for="(cell, idx) in calendarCells" :key="idx" @click="cell.isCurrentMonth && selectDay(cell.day)" :class="[cell.isCurrentMonth ? 'bg-theme-light-card dark:bg-theme-dark-card border-theme-light-border dark:border-theme-dark-border cursor-pointer hover:border-purple-500 relative overflow-hidden' : 'opacity-25 pointer-events-none border-transparent', selectedDay === cell.day ? 'ring-2 ring-purple-600' : '']" class="border rounded-xl min-h-24 p-2 flex flex-col justify-between transition-all">
          <div class="flex justify-between items-start z-10">
            <span class="text-xs font-bold" :class="cell.isToday ? 'bg-theme-accent-primary text-white w-5 h-5 rounded-full flex items-center justify-center' : 'text-slate-700 dark:text-purple-300'">{{ cell.day }}</span>
            <div v-if="cell.hasPlanned" class="w-2 h-2 rounded-full bg-purple-500 animate-pulse" title="Есть запланированные операции"></div>
          </div>
          <div v-if="cell.isCurrentMonth && cell.totals" class="space-y-1 font-mono text-[11px] leading-tight mt-1 z-10 relative">
            <p v-if="cell.totals.income > 0" class="text-emerald-600 font-bold truncate">+{{ Math.round(cell.totals.income) }} {{ settings.getSymbol(settings.baseCurrency) }}</p>
            <p v-if="cell.totals.expense > 0" class="text-rose-600 font-bold truncate">-{{ Math.round(cell.totals.expense) }} {{ settings.getSymbol(settings.baseCurrency) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Модалка операций за день -->
  <Teleport to="body">
    <div v-if="selectedDay" @click.self="selectedDay = null" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-lg p-6 flex flex-col max-h-[85vh]">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-theme-light-border dark:border-theme-dark-border"><h3 class="font-black text-base text-slate-800 dark:text-purple-100">Операции за {{ selectedDay }} {{ monthNames[currentMonth - 1] }}</h3><button @click="selectedDay = null" class="text-xs font-bold px-2 py-1 rounded hover:bg-purple-100 dark:hover:bg-theme-dark-hover">Закрыть</button></div>
        <div class="flex-1 overflow-y-auto divide-y divide-theme-light-border dark:divide-theme-dark-border">
          <div v-if="dayTransactions.length === 0" class="py-8 text-center text-xs text-theme-light-muted">В этот день операций нет</div>
          <div v-for="t in dayTransactions" :key="t.id" class="py-3 flex justify-between items-center text-sm" :class="{'opacity-75 bg-purple-50/50 dark:bg-purple-950/20 px-2 rounded-xl': t.isPlanned || t.is_executed === false}">
            <div>
              <p class="font-bold text-slate-800 dark:text-purple-200">
                <span v-if="t.is_executed === false" class="text-[10px] bg-purple-600 text-white px-1.5 py-0.5 rounded font-black mr-1 shadow-sm">ОТЛОЖЕН</span>
                <span v-else-if="t.isPlanned" class="text-[10px] bg-purple-200 dark:bg-purple-900 text-purple-800 dark:text-purple-200 px-1.5 py-0.5 rounded font-black mr-1">ПЛАН</span>
                {{ translateType(t.type) }}
              </p>
              <p class="text-xs text-theme-light-muted">{{ t.note || 'Без описания' }} <span v-if="!t.isPlanned">• {{ t.author === 'HUSBAND' ? 'Любими Муж' : 'КошкоЖена' }}</span></p>
            </div>
            <div class="text-right">
              <p class="font-mono font-bold" :class="isIncomeType(t.type) ? 'text-emerald-500' : 'text-rose-500'">{{ isIncomeType(t.type) ? '+' : '-' }}{{ t.amount }} {{ settings.getSymbol(t.currency) }}</p>
              <button v-if="!t.isPlanned" @click="askDelete(t.id)" class="text-[11px] text-red-500 hover:underline">Удалить</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Модалка Планирования Расходов -->
  <Teleport to="body">
    <div v-if="showPlanModal" @click.self="showPlanModal = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-xl p-6 flex flex-col max-h-[85vh]">
        <div class="flex justify-between items-center mb-4"><h3 class="font-black text-lg text-slate-800 dark:text-purple-100">План расходов: {{ monthNames[currentMonth - 1] }} {{ currentYear }}</h3><button @click="showPlanModal = false" class="text-xs font-bold px-2 py-1">Закрыть</button></div>
        <div v-if="isForecastLoading" class="flex-1 flex justify-center items-center py-10"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>
        <div v-else class="flex-1 overflow-y-auto space-y-3 pr-2">
          <div v-for="cat in expenseCategories" :key="cat.id" class="p-3.5 bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl flex justify-between items-center">
            <div>
              <p class="font-bold text-sm text-slate-800 dark:text-purple-200">{{ cat.name }}</p>
              <p class="text-[11px] text-theme-light-muted">Средний расход: {{ forecasts[cat.id]?.average_monthly_expense || 0 }} {{ settings.getSymbol(settings.baseCurrency) }}</p>
              <p class="text-[11px] text-purple-600 font-semibold">Уже потрачено: {{ getSpentInCurrentMonthForCat(cat.id) }} {{ settings.getSymbol(settings.baseCurrency) }}</p>
            </div>
            <div class="text-right">
              <span class="text-xs block text-theme-light-muted">Ожидание</span>
              <span class="text-sm font-black font-mono text-rose-500 bg-rose-50 dark:bg-rose-950/40 px-2 py-1 rounded-lg">
                {{ cat.default_amount || forecasts[cat.id]?.predicted_next_month || '0.00' }} {{ settings.getSymbol(settings.baseCurrency) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Модалка Аналитики за выбранный месяц -->
  <Teleport to="body">
    <div v-if="showAnalyticsModal" @click.self="showAnalyticsModal = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-2xl p-6 flex flex-col max-h-[88vh]">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-theme-light-border dark:border-theme-dark-border">
          <h3 class="font-black text-lg text-slate-800 dark:text-purple-100">📊 Аналитика: {{ monthNames[currentMonth - 1] }} {{ currentYear }}</h3>
          <button @click="showAnalyticsModal = false" class="text-xs font-bold px-2 py-1">Закрыть</button>
        </div>

        <div class="flex-1 overflow-y-auto space-y-6 pr-2">
          <div class="grid grid-cols-3 gap-3">
            <div class="p-4 rounded-xl bg-purple-50 dark:bg-theme-dark-card border border-purple-200 dark:border-purple-900/60 text-center">
              <span class="text-xs text-theme-light-muted font-bold">Доходы</span>
              <p class="text-base font-black text-emerald-500 mt-1 font-mono">+{{ monthTotalIncome }} {{ settings.getSymbol(settings.baseCurrency) }}</p>
            </div>
            <div class="p-4 rounded-xl bg-purple-50 dark:bg-theme-dark-card border border-purple-200 dark:border-purple-900/60 text-center">
              <span class="text-xs text-theme-light-muted font-bold">Расходы</span>
              <p class="text-base font-black text-rose-500 mt-1 font-mono">-{{ monthTotalExpense }} {{ settings.getSymbol(settings.baseCurrency) }}</p>
            </div>
            <div class="p-4 rounded-xl bg-purple-50 dark:bg-theme-dark-card border border-purple-200 dark:border-purple-900/60 text-center">
              <span class="text-xs text-theme-light-muted font-bold">Остаток</span>
              <p class="text-base font-black mt-1 font-mono" :class="monthSavings >= 0 ? 'text-purple-600 dark:text-purple-300' : 'text-rose-500'">
                {{ monthSavings }} {{ settings.getSymbol(settings.baseCurrency) }}
              </p>
            </div>
          </div>

          <div>
            <h4 class="text-xs font-bold uppercase tracking-wider text-theme-light-muted mb-3">Распределение трат по категориям</h4>
            <div v-if="categoryStats.length === 0" class="text-xs text-theme-light-muted italic text-center py-4">В этом месяце расходов не зафиксировано</div>
            <div v-else class="space-y-3">
              <div
                v-for="item in categoryStats"
                :key="item.cat.id"
                @click="openCategoryDetail(item.cat)"
                class="p-3 bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl cursor-pointer hover:border-purple-400 transition"
              >
                <div class="flex justify-between items-center text-xs mb-1">
                  <span class="font-bold flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full" :style="{ backgroundColor: item.cat.color }"></span>
                    {{ item.cat.name }}
                  </span>
                  <div class="flex items-center gap-3 font-mono">
                    <span class="font-bold">{{ item.spent }} {{ settings.getSymbol(settings.baseCurrency) }}</span>
                    <span class="text-purple-600 font-black">({{ item.pct }}%)</span>
                  </div>
                </div>
                <div class="w-full bg-slate-100 dark:bg-purple-950 h-2 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all" :style="{ width: item.pct + '%', backgroundColor: item.cat.color }"></div>
                </div>
                <div class="flex justify-between items-center text-[10px] mt-1.5 font-bold">
                  <span v-if="item.limit" :class="item.limit.is_exceeded ? 'text-red-500' : 'text-emerald-600'">
                    {{ item.limit.is_exceeded ? 'Лимит превышен!' : 'Лимит соблюдён' }} (Лимит: {{ item.limit.limit_amount }} {{ settings.getSymbol(item.limit.currency) }})
                  </span>
                  <span v-else class="text-theme-light-muted">Без лимита</span>
                  <span class="text-purple-500 font-normal">Посмотреть операции →</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Модалка транзакций по категории -->
  <Teleport to="body">
    <div v-if="detailCategory" @click.self="detailCategory = null" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-[60]">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-lg p-6 flex flex-col max-h-[80vh]">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-theme-light-border dark:border-theme-dark-border">
          <h3 class="font-black text-base text-slate-800 dark:text-purple-100">Операции категории "{{ detailCategory.name }}" за {{ monthNames[currentMonth - 1] }}</h3>
          <button @click="detailCategory = null" class="text-xs font-bold px-2 py-1">Закрыть</button>
        </div>
        <div class="flex-1 overflow-y-auto divide-y divide-theme-light-border dark:divide-theme-dark-border">
          <div v-if="categoryTransactions.length === 0" class="py-8 text-center text-xs text-theme-light-muted">Операций нет</div>
          <div v-for="t in categoryTransactions" :key="t.id" class="py-2.5 flex justify-between items-center text-xs">
            <div>
              <p class="font-bold text-slate-800 dark:text-purple-200">{{ t.note || 'Без описания' }}</p>
              <p class="text-[10px] text-theme-light-muted">{{ new Date(t.date).toLocaleDateString('ru-RU') }} • {{ t.author === 'HUSBAND' ? 'Любими Муж' : 'КошкоЖена' }}</p>
            </div>
            <span class="font-mono font-bold text-rose-500 text-sm">-{{ t.amount }} {{ settings.getSymbol(t.currency) }}</span>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Модалка удаления -->
  <Teleport to="body">
    <div v-if="deleteTxId" @click.self="deleteTxId = null" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-[70]">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6 text-center">
        <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-2">Удалить операцию?</h3>
        <div class="flex justify-center gap-3 mt-4">
          <button @click="deleteTxId = null" class="px-5 py-2.5 text-sm font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition">Отмена</button>
          <button @click="confirmDelete" class="px-5 py-2.5 text-sm font-bold bg-red-500 hover:bg-red-600 text-white rounded-xl transition">Удалить</button>
        </div>
      </div>
    </div>
  </Teleport>
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
const detailCategory = ref(null);
const deleteTxId = ref(null);

const transactions = ref([]);
const categories = ref([]);
const accounts = ref([]);
const piggyBanks = ref([]);
const limitsMap = ref({});
const forecasts = ref({});
const isForecastLoading = ref(false);

const monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

function isIncomeType(type) { return type.startsWith('INCOME'); }
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

function getExactDay(isoString) {
  if (!isoString) return 0;
  const d = isoString.split('T')[0].split(' ')[0].split('-');
  return parseInt(d[2], 10);
}
function getExactMonth(isoString) {
  if (!isoString) return 0;
  const d = isoString.split('T')[0].split(' ')[0].split('-');
  return parseInt(d[1], 10);
}
function getExactYear(isoString) {
  if (!isoString) return 0;
  const d = isoString.split('T')[0].split(' ')[0].split('-');
  return parseInt(d[0], 10);
}

const expenseCategories = computed(() => categories.value.filter(c => c.group === 'EXPENSE'));

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
    const executed = t.is_executed !== false;
    if (isIncomeType(t.type) && executed) sum += settings.convert(t.amount, t.currency);
  });
  return Math.round(sum);
});

const monthTotalExpense = computed(() => {
  let sum = 0;
  transactions.value.forEach(t => {
    const executed = t.is_executed !== false;
    if (!isIncomeType(t.type) && t.type !== 'TRANSFER' && executed) sum += settings.convert(t.amount, t.currency);
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
      const executed = t.is_executed !== false;
      if (t.category_id === cat.id && !isIncomeType(t.type) && executed) {
        spent += settings.convert(t.amount, t.currency);
      }
    });
    if (spent > 0) {
      const pct = Math.min(100, Math.round((spent / totalExp) * 100));
      res.push({
        cat,
        spent: Math.round(spent),
        pct,
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
    const executed = t.is_executed !== false;
    if (t.category_id === catId && !isIncomeType(t.type) && executed) {
      sum += settings.convert(t.amount, t.currency);
    }
  });
  return Math.round(sum);
}

function selectDay(d) { selectedDay.value = d; }
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

function openAnalyticsModal() { showAnalyticsModal.value = true; }
function openCategoryDetail(cat) { detailCategory.value = cat; }

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

function askDelete(id) { deleteTxId.value = id; }
async function confirmDelete() {
  if (!deleteTxId.value) return;
  await api.delete(`/transactions/${deleteTxId.value}`);
  deleteTxId.value = null;
  await loadMonthData();
}

onMounted(loadMonthData);
</script>