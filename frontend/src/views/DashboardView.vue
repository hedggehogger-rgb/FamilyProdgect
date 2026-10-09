<template>
  <div class="space-y-8">
    <!-- Блок со статистикой месяца -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-theme-light-card dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border p-6 rounded-2xl shadow-sm">
        <span class="text-xs font-bold uppercase tracking-wider text-theme-light-muted dark:text-theme-dark-muted">Доходы в этом месяце</span>
        <p class="text-3xl font-black text-emerald-600 dark:text-emerald-400 mt-2 font-mono">+{{ formatMoney(monthlyStats.income) }} {{ currentSymbol }}</p>
      </div>
      <div class="bg-theme-light-card dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border p-6 rounded-2xl shadow-sm">
        <span class="text-xs font-bold uppercase tracking-wider text-theme-light-muted dark:text-theme-dark-muted">Расходы в этом месяце</span>
        <p class="text-3xl font-black text-rose-600 dark:text-rose-400 mt-2 font-mono">-{{ formatMoney(monthlyStats.expense) }} {{ currentSymbol }}</p>
      </div>
      <div class="bg-theme-light-card dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border p-6 rounded-2xl shadow-sm">
        <span class="text-xs font-bold uppercase tracking-wider text-theme-light-muted dark:text-theme-dark-muted">Итог месяца</span>
        <p class="text-3xl font-black mt-2 font-mono" :class="monthlyStats.savings >= 0 ? 'text-purple-600 dark:text-purple-300' : 'text-rose-500'">
          {{ formatMoney(monthlyStats.savings) }} {{ currentSymbol }}
        </p>
      </div>
    </div>

    <!-- Быстрая запись операции С ФОРМАТИРОВАНИЕМ ЧИСЕЛ ЧЕРЕЗ ПРОБЕЛ -->
    <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-6 shadow-sm">
      <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-6 flex items-center gap-2">
        <PlusCircle class="w-5 h-5 text-theme-accent-primary" />
        Быстрая запись операции
      </h3>

      <form @submit.prevent="submitTransaction" class="space-y-6">
        <div>
          <label class="block text-sm font-bold text-theme-light-muted dark:text-theme-dark-muted mb-2">Сумма операции</label>
          <div class="flex gap-2">
            <FormattedNumberInput
              v-model="txForm.amount"
              placeholder="0"
              inputClass="w-full bg-white dark:bg-theme-dark-card border-2 border-purple-200 dark:border-purple-900/60 rounded-2xl px-4 py-4 text-3xl font-black font-mono focus:border-purple-500 outline-none text-slate-900 dark:text-white transition-colors"
            />
            <div class="w-28 shrink-0">
              <CustomSelect v-model="txForm.currency" :options="symbolCurrencyOptions" size="lg" class="h-full" />
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Тип операции</label>
            <CustomSelect v-model="txForm.type" :options="typeOptions" @change="handleTypeChange" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Счёт</label>
            <CustomSelect v-model="txForm.account_id" :options="accountOptions" :placeholder="accounts.length ? 'Выберите счёт' : 'Нет счетов'" :disabled="!accounts.length" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Категория</label>
            <CustomSelect v-model="txForm.category_id" :options="categoryOptions" placeholder="Без категории" />
          </div>
        </div>

        <div v-if="isPlannedType" class="p-4 bg-purple-50/60 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-900/50 rounded-2xl space-y-2">
          <label class="block text-xs font-bold text-purple-700 dark:text-purple-300">
            📅 Дата исполнения разового платежа (деньги спишутся в этот день)
          </label>
          <div class="max-w-xs">
            <CustomDatePicker v-model="txForm.plannedDate" placeholder="Выберите дату платежа" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold mb-1" :class="!txForm.category_id ? 'text-rose-500 font-bold' : 'text-theme-light-muted'">
            {{ !txForm.category_id ? '* Описание обязательно (так как категория не выбрана)' : 'Описание / заметка' }}
          </label>
          <input
            v-model="txForm.note"
            :required="!txForm.category_id"
            placeholder="Например: Оплата страховки или Ремонт авто"
            class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-purple-500 text-slate-800 dark:text-purple-100"
          />
        </div>

        <div class="flex justify-end">
          <button
            type="submit"
            :disabled="loading || !txForm.account_id || !txForm.amount"
            class="bg-theme-accent-primary hover:bg-theme-accent-hover text-white font-bold px-8 py-3 rounded-xl transition shadow-md shadow-purple-500/20 active:scale-95 disabled:opacity-50"
          >
            {{ isPlannedType ? 'Запланировать платёж' : 'Записать операцию' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Список отложенных разовых платежей -->
    <div v-if="deferredList.length > 0" class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-6 shadow-sm space-y-4">
      <div class="flex justify-between items-center">
        <div>
          <h3 class="text-base font-black text-slate-800 dark:text-purple-100 flex items-center gap-2">
            <Clock class="w-4 h-4 text-purple-600 dark:text-purple-400" />
            Запланированные разовые платежи
          </h3>
          <p class="text-xs text-theme-light-muted">Средства будут автоматически списаны/зачислены в указанный день</p>
        </div>
        <span class="text-xs font-bold px-2.5 py-1 rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900/60 dark:text-purple-200">
          Ожидают: {{ deferredList.length }}
        </span>
      </div>

      <div class="divide-y divide-theme-light-border dark:divide-theme-dark-border">
        <div v-for="item in deferredList" :key="item.id" class="py-3.5 flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center font-mono font-bold text-xs" :class="item.type === 'INCOME_PLANNED' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300' : 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300'">
              {{ item.type === 'INCOME_PLANNED' ? 'ВХ' : 'ИСХ' }}
            </div>
            <div>
              <p class="text-sm font-bold text-slate-800 dark:text-purple-100">
                {{ item.note || getCategoryName(item.category_id) }}
                <span class="text-xs font-normal text-theme-light-muted">({{ getCategoryName(item.category_id) }})</span>
              </p>
              <p class="text-xs text-theme-light-muted">
                Дата: <strong class="text-purple-600 font-mono">{{ formatDate(item.date) }}</strong> • Счёт: {{ getAccountName(item.account_id) }}
              </p>
            </div>
          </div>

          <div class="flex items-center gap-4">
            <span class="font-mono font-bold text-base" :class="item.type === 'INCOME_PLANNED' ? 'text-emerald-500' : 'text-rose-500'">
              {{ item.type === 'INCOME_PLANNED' ? '+' : '-' }}{{ formatMoney(item.amount) }} {{ settings.getSymbol(item.currency) }}
            </span>
            <button
              @click="deleteDeferred(item.id)"
              title="Отменить и удалить платёж"
              class="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-xl transition"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { PlusCircle, Clock, Trash2 } from 'lucide-vue-next';
import api from '@/api';
import { useSettingsStore } from '@/stores/settings';
import CustomSelect from '@/components/CustomSelect.vue';
import CustomDatePicker from '@/components/CustomDatePicker.vue';
import FormattedNumberInput from '@/components/FormattedNumberInput.vue';

const settings = useSettingsStore();
const accounts = ref([]);
const categories = ref([]);
const deferredList = ref([]);
const loading = ref(false);

const monthlyStats = reactive({ income: 0, expense: 0, savings: 0 });

const typeOptions = [
  { label: 'Внеплановый расход', value: 'EXPENSE_IMPULSE' },
  { label: 'Запланировать расход (на дату)', value: 'EXPENSE_PLANNED' },
  { label: 'Внеплановый доход', value: 'INCOME_UNPLANNED' },
  { label: 'Запланировать доход (на дату)', value: 'INCOME_PLANNED' },
  { label: 'Инвестиция', value: 'INVESTMENT' }
];

const symbolCurrencyOptions = [
  { label: '₽', value: 'RUB' },
  { label: '$', value: 'USD' },
  { label: '֏', value: 'AMD' }
];

const currentSymbol = computed(() => settings.getSymbol(settings.baseCurrency));

const txForm = reactive({
  type: 'EXPENSE_IMPULSE',
  account_id: '',
  category_id: null,
  amount: null,
  currency: settings.baseCurrency,
  note: '',
  plannedDate: ''
});

const isPlannedType = computed(() => ['EXPENSE_PLANNED', 'INCOME_PLANNED'].includes(txForm.type));

const accountOptions = computed(() => accounts.value.map(a => ({ label: `${a.name} (${settings.getSymbol(a.currency)})`, value: a.id })));

const categoryOptions = computed(() => {
  const isIncome = txForm.type.includes('INCOME');
  const isInvest = txForm.type === 'INVESTMENT';
  const list = categories.value.filter(c => {
    if (isIncome) return c.group === 'INCOME';
    if (isInvest) return c.group === 'INVESTMENT';
    return c.group === 'EXPENSE';
  });

  return [
    { label: 'Без категории', value: null },
    ...list.map(c => ({ label: c.name, value: c.id }))
  ];
});

function formatMoney(val) {
  if (val === null || val === undefined || isNaN(val)) return '0';
  return Number(val).toLocaleString('ru-RU');
}

function formatDate(isoStr) {
  return new Date(isoStr).toLocaleDateString('ru-RU');
}

function getAccountName(id) {
  const acc = accounts.value.find(a => a.id === id);
  return acc ? acc.name : '—';
}

function getCategoryName(id) {
  const cat = categories.value.find(c => c.id === id);
  return cat ? cat.name : 'Без категории';
}

function handleTypeChange() {
  txForm.category_id = null;
  if (isPlannedType.value && !txForm.plannedDate) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    txForm.plannedDate = tomorrow.toISOString().split('T')[0];
  }
}

async function loadData() {
  const [accRes, catRes, defRes] = await Promise.all([
    api.get('/accounts'),
    api.get('/categories'),
    api.get('/transactions/deferred')
  ]);
  accounts.value = accRes.data;
  categories.value = catRes.data;
  deferredList.value = defRes.data;

  if (accounts.value.length > 0) {
    if (!txForm.account_id || !accounts.value.some(a => a.id === txForm.account_id)) {
      txForm.account_id = accounts.value[0].id;
    }
  } else {
    txForm.account_id = '';
  }

  const now = new Date();
  try {
    const { data: rep } = await api.get(`/analytics/monthly-report?year=${now.getFullYear()}&month=${now.getMonth() + 1}&currency=${settings.baseCurrency}`);
    monthlyStats.income = rep.total_income;
    monthlyStats.expense = rep.total_expense;
    monthlyStats.savings = rep.net_savings;
  } catch (e) { console.error(e); }
}

async function submitTransaction() {
  if (!txForm.account_id || !txForm.amount) return;
  loading.value = true;
  try {
    const payload = {
      type: txForm.type,
      account_id: txForm.account_id,
      category_id: txForm.category_id || null,
      amount: txForm.amount,
      currency: txForm.currency,
      note: txForm.note || (txForm.category_id ? 'Плановый платёж' : '')
    };

    if (isPlannedType.value && txForm.plannedDate) {
      payload.date = `${txForm.plannedDate}T12:00:00`;
    }

    await api.post('/transactions', payload);
    txForm.amount = null;
    txForm.note = '';
    await loadData();
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка сохранения транзакции');
  } finally {
    loading.value = false;
  }
}

async function deleteDeferred(id) {
  try {
    await api.delete(`/transactions/${id}`);
    await loadData();
  } catch (err) {
    alert('Не удалось отменить отложенный платёж');
  }
}

onMounted(loadData);
</script>