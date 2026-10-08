<template>
  <div class="space-y-8">
    <!-- Сводка текущего месяца -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-theme-light-card dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border p-6 rounded-2xl shadow-sm">
        <span class="text-xs font-bold uppercase tracking-wider text-theme-light-muted dark:text-theme-dark-muted">
          Доходы в этом месяце
        </span>
        <p class="text-3xl font-black text-emerald-600 dark:text-emerald-400 mt-2 font-mono">
          +{{ formatMoney(monthlyStats.income) }} {{ currentSymbol }}
        </p>
      </div>

      <div class="bg-theme-light-card dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border p-6 rounded-2xl shadow-sm">
        <span class="text-xs font-bold uppercase tracking-wider text-theme-light-muted dark:text-theme-dark-muted">
          Расходы в этом месяце
        </span>
        <p class="text-3xl font-black text-rose-600 dark:text-rose-400 mt-2 font-mono">
          -{{ formatMoney(monthlyStats.expense) }} {{ currentSymbol }}
        </p>
      </div>

      <div class="bg-theme-light-card dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border p-6 rounded-2xl shadow-sm">
        <span class="text-xs font-bold uppercase tracking-wider text-theme-light-muted dark:text-theme-dark-muted">
          Итог месяца
        </span>
        <p
          class="text-3xl font-black mt-2 font-mono"
          :class="monthlyStats.savings >= 0 ? 'text-purple-600 dark:text-purple-300' : 'text-rose-500'"
        >
          {{ formatMoney(monthlyStats.savings) }} {{ currentSymbol }}
        </p>
      </div>
    </div>

    <!-- Форма быстрой записи расхода / дохода -->
    <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-6 shadow-sm">
      <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-6 flex items-center gap-2">
        <PlusCircle class="w-5 h-5 text-theme-accent-primary" />
        Быстрая запись операции
      </h3>

      <form @submit.prevent="submitTransaction" class="grid grid-cols-1 md:grid-cols-6 gap-4">
        <!-- 1. Тип операции -->
        <div class="md:col-span-2">
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">
            Тип операции
          </label>
          <CustomSelect
            v-model="txForm.type"
            :options="typeOptions"
            @change="handleTypeChange"
          />
        </div>

        <!-- 2. Счёт списания / пополнения -->
        <div>
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">
            Счёт
          </label>
          <CustomSelect
            v-model="txForm.account_id"
            :options="accountOptions"
            :placeholder="accounts.length ? 'Выберите счёт' : 'Нет счетов'"
            :disabled="!accounts.length"
          />
        </div>

        <!-- 3. Категория -->
        <div>
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">
            Категория
          </label>
          <CustomSelect
            v-model="txForm.category_id"
            :options="categoryOptions"
            placeholder="Без категории"
          />
        </div>

        <!-- 4. Сумма и валюта -->
        <div>
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">
            Сумма
          </label>
          <div class="flex gap-1.5">
            <input
              v-model.number="txForm.amount"
              type="number"
              step="any"
              min="0.01"
              required
              placeholder="0.00"
              class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl px-3 py-2 text-sm font-bold font-mono focus:ring-2 focus:ring-purple-500 outline-none text-slate-800 dark:text-purple-100"
            />
            <div class="w-24 shrink-0">
              <CustomSelect
                v-model="txForm.currency"
                :options="currencyOptions"
                size="md"
              />
            </div>
          </div>
        </div>

        <!-- Кнопка записи -->
        <div class="flex items-end">
          <button
            type="submit"
            :disabled="loading || !txForm.account_id"
            class="w-full bg-theme-accent-primary hover:bg-theme-accent-hover text-white font-bold py-2.5 rounded-xl text-sm transition shadow-md shadow-purple-500/20 active:scale-95 disabled:opacity-50"
          >
            Записать
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { PlusCircle } from 'lucide-vue-next';
import api from '@/api';
import { useSettingsStore } from '@/stores/settings';
import CustomSelect from '@/components/CustomSelect.vue';

const settings = useSettingsStore();
const accounts = ref([]);
const categories = ref([]);
const loading = ref(false);

const monthlyStats = reactive({
  income: 0,
  expense: 0,
  savings: 0,
});

const typeOptions = [
  { label: 'Плановый расход', value: 'EXPENSE_PLANNED' },
  { label: 'Внеплановый расход', value: 'EXPENSE_IMPULSE' },
  { label: 'Плановый доход', value: 'INCOME_PLANNED' },
  { label: 'Внеплановый доход', value: 'INCOME_UNPLANNED' },
  { label: 'Инвестиция', value: 'INVESTMENT' }
];

const currencyOptions = [
  { label: 'RUB', value: 'RUB' },
  { label: 'USD', value: 'USD' },
  { label: 'AMD', value: 'AMD' }
];

const currentSymbol = computed(() => {
  const map = { RUB: '₽', USD: '$', AMD: '֏' };
  return map[settings.baseCurrency] || '₽';
});

const txForm = reactive({
  type: 'EXPENSE_PLANNED',
  account_id: '',
  category_id: null,
  amount: null,
  currency: settings.baseCurrency,
});

const accountOptions = computed(() => {
  return accounts.value.map(a => ({
    label: `${a.name} (${a.currency})`,
    value: a.id
  }));
});

const categoryOptions = computed(() => {
  const isIncome = txForm.type.startsWith('INCOME');
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
  return Number(val || 0).toLocaleString('ru-RU', { minimumFractionDigits: 2 });
}

function handleTypeChange() {
  txForm.category_id = null;
}

async function loadData() {
  const [accRes, catRes] = await Promise.all([
    api.get('/accounts'),
    api.get('/categories')
  ]);
  accounts.value = accRes.data;
  categories.value = catRes.data;

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
  } catch (e) {
    console.error(e);
  }
}

async function submitTransaction() {
  if (!txForm.account_id) {
    alert('Сначала добавьте хотя бы один счёт во вкладке "Счета"');
    return;
  }
  loading.value = true;
  try {
    await api.post('/transactions', {
      type: txForm.type,
      account_id: txForm.account_id,
      category_id: txForm.category_id || null,
      amount: txForm.amount,
      currency: txForm.currency,
      note: 'Быстрая запись'
    });
    txForm.amount = null;
    await loadData();
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка сохранения транзакции');
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>