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

    <!-- Быстрая запись операции / Перевод -->
    <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl p-6 shadow-sm">
      <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-6 flex items-center gap-2">
        <component :is="isTransfer ? ArrowLeftRight : PlusCircle" class="w-5 h-5 text-theme-accent-primary" />
        {{ isTransfer ? 'Перевод между счетами' : 'Быстрая запись операции' }}
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

        <!-- Поля формы: режим перевода -->
        <div v-if="isTransfer" class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Тип операции</label>
            <CustomSelect v-model="txForm.type" :options="typeOptions" @change="handleTypeChange" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Счёт списания (Откуда)</label>
            <CustomSelect v-model="txForm.account_id" :options="accountOptions" placeholder="Выберите счёт" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Счёт зачисления (Куда)</label>
            <CustomSelect v-model="txForm.to_account_id" :options="toAccountOptions" placeholder="Выберите счёт" />
          </div>
        </div>

        <!-- Поля формы: стандартный режим (доход/расход) -->
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Тип операции</label>
            <CustomSelect v-model="txForm.type" :options="typeOptions" @change="handleTypeChange" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Счёт</label>
            <CustomSelect v-model="txForm.account_id" :options="accountOptions" placeholder="Выберите счёт" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Категория</label>
            <CustomSelect v-model="txForm.category_id" :options="categoryOptions" placeholder="Без категории" />
          </div>
        </div>

        <!-- Плановая дата (только для плановых расходов/доходов) -->
        <div v-if="!isTransfer && isPlannedType" class="p-4 bg-purple-50/60 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-900/50 rounded-2xl space-y-2">
          <label class="block text-xs font-bold text-purple-700 dark:text-purple-300">
            📅 Дата исполнения разового платежа
          </label>
          <div class="max-w-xs">
            <CustomDatePicker v-model="txForm.plannedDate" placeholder="Выберите дату платежа" />
          </div>
        </div>

        <!-- Описание / заметка (только если не перевод) -->
        <div v-if="!isTransfer">
          <label class="block text-xs font-bold mb-1" :class="!txForm.category_id ? 'text-rose-500 font-bold' : 'text-theme-light-muted'">
            {{ !txForm.category_id ? '* Описание обязательно (так как категория не выбрана)' : 'Описание / заметка' }}
          </label>
          <input
            v-model="txForm.note"
            :required="!txForm.category_id"
            placeholder="Например: Оплата страховки"
            class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-purple-500 text-slate-800 dark:text-purple-100"
          />
        </div>

        <div class="flex justify-end">
          <button
            type="submit"
            :disabled="submitDisabled"
            class="bg-theme-accent-primary hover:bg-theme-accent-hover text-white font-bold px-8 py-3 rounded-xl transition shadow-md shadow-purple-500/20 active:scale-95 disabled:opacity-50"
          >
            {{ isTransfer ? 'Выполнить перевод' : (isPlannedType ? 'Запланировать платёж' : 'Записать операцию') }}
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
            <div class="w-10 h-10 rounded-xl flex items-center justify-center font-mono font-bold text-xs" :class="item.type === 'INCOME_PLANNED' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'">
              {{ item.type === 'INCOME_PLANNED' ? 'ВХ' : 'ИСХ' }}
            </div>
            <div>
              <p class="text-sm font-bold text-slate-800 dark:text-purple-100">
                {{ item.note || getCategoryName(item.category_id) }}
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
            <button @click="deleteDeferred(item.id)" class="p-2 text-red-500 hover:text-red-700 transition">
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
import { PlusCircle, Clock, Trash2, ArrowLeftRight } from 'lucide-vue-next';
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
  { label: 'Инвестиция', value: 'INVESTMENT' },
  { label: 'Перевод между счетами', value: 'TRANSFER' }
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
  to_account_id: '',
  category_id: null,
  amount: null,
  currency: settings.baseCurrency,
  note: '',
  plannedDate: ''
});

const isTransfer = computed(() => txForm.type === 'TRANSFER');
const isPlannedType = computed(() => ['EXPENSE_PLANNED', 'INCOME_PLANNED'].includes(txForm.type));

const accountOptions = computed(() => accounts.value.map(a => ({ label: `${a.name} (${settings.getSymbol(a.currency)})`, value: a.id })));
const toAccountOptions = computed(() => accounts.value.filter(a => a.id !== txForm.account_id).map(a => ({ label: `${a.name} (${settings.getSymbol(a.currency)})`, value: a.id })));

const categoryOptions = computed(() => {
  const isIncome = txForm.type.includes('INCOME');
  const isInvest = txForm.type === 'INVESTMENT';
  const list = categories.value.filter(c => {
    if (isIncome) return c.group === 'INCOME';
    if (isInvest) return c.group === 'INVESTMENT';
    return c.group === 'EXPENSE';
  });
  return [{ label: 'Без категории', value: null }, ...list.map(c => ({ label: c.name, value: c.id }))];
});

const submitDisabled = computed(() => {
  if (loading.value || !txForm.amount) return true;
  if (isTransfer.value) return !txForm.account_id || !txForm.to_account_id || txForm.account_id === txForm.to_account_id;
  return !txForm.account_id;
});

function formatMoney(val) { return (!val || isNaN(val)) ? '0' : Number(val).toLocaleString('ru-RU'); }
function formatDate(isoStr) { return new Date(isoStr).toLocaleDateString('ru-RU'); }
function getAccountName(id) { const a = accounts.value.find(acc => acc.id === id); return a ? a.name : '—'; }
function getCategoryName(id) { const c = categories.value.find(cat => cat.id === id); return c ? c.name : 'Без категории'; }

function handleTypeChange() {
  txForm.category_id = null;
  if (isTransfer.value && accounts.value.length > 1 && (!txForm.to_account_id || txForm.to_account_id === txForm.account_id)) {
    const alt = accounts.value.find(a => a.id !== txForm.account_id);
    if (alt) txForm.to_account_id = alt.id;
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

  if (accounts.value.length > 0 && !txForm.account_id) txForm.account_id = accounts.value[0].id;
  if (accounts.value.length > 1 && !txForm.to_account_id) txForm.to_account_id = accounts.value[1].id;

  const now = new Date();
  try {
    const { data: rep } = await api.get(`/analytics/monthly-report?year=${now.getFullYear()}&month=${now.getMonth() + 1}&currency=${settings.baseCurrency}`);
    monthlyStats.income = rep.total_income;
    monthlyStats.expense = rep.total_expense;
    monthlyStats.savings = rep.net_savings;
  } catch (e) {}
}

async function submitTransaction() {
  if (submitDisabled.value) return;
  loading.value = true;
  try {
    if (isTransfer.value) {
      await api.post('/transactions/transfer', {
        from_account_id: txForm.account_id,
        to_account_id: txForm.to_account_id,
        amount: txForm.amount,
        currency: txForm.currency,
        note: 'Перевод между счетами'
      });
    } else {
      const payload = {
        type: txForm.type,
        account_id: txForm.account_id,
        category_id: txForm.category_id || null,
        amount: txForm.amount,
        currency: txForm.currency,
        note: txForm.note || (txForm.category_id ? 'Операция' : '')
      };
      if (isPlannedType.value && txForm.plannedDate) payload.date = `${txForm.plannedDate}T12:00:00`;
      await api.post('/transactions', payload);
    }
    txForm.amount = null;
    txForm.note = '';
    await loadData();
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка сохранения операции');
  } finally {
    loading.value = false;
  }
}

async function deleteDeferred(id) {
  await api.delete(`/transactions/${id}`);
  await loadData();
}

onMounted(loadData);
</script>