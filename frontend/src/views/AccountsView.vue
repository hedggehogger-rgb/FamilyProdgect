<template>
  <div class="space-y-6">
    <!-- Плавающая кнопка добавления счёта -->
    <button
      @click="showModal = true"
      title="Добавить счёт"
      class="fixed top-20 right-8 z-30 bg-theme-accent-primary hover:bg-theme-accent-hover text-white p-3 rounded-2xl font-bold transition-all shadow-lg shadow-purple-500/30 hover:scale-105 active:scale-95 flex items-center justify-center"
    >
      <Plus class="w-5 h-5 stroke-[2.5]" />
    </button>

    <!-- Сетка счетов (начинается сразу вверху) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="acc in accounts"
        :key="acc.id"
        class="bg-theme-light-card dark:bg-theme-dark-card rounded-3xl p-6 border border-theme-light-border dark:border-theme-dark-border shadow-sm flex flex-col gap-4"
      >
        <div class="flex justify-between items-start gap-4">
          <div class="overflow-hidden">
            <span v-if="acc.is_investment" class="text-[10px] font-bold uppercase tracking-wider text-purple-600 dark:text-purple-400">
              Инвестиционный счёт
            </span>
            <h3 class="text-xl font-black text-slate-800 dark:text-purple-100 leading-tight mt-1 truncate" :title="acc.name">
              {{ acc.name }}
            </h3>
          </div>
          <span class="shrink-0 text-xs px-3 py-1 rounded-xl font-bold font-mono bg-purple-100 dark:bg-purple-900/60 text-purple-800 dark:text-purple-200 border border-purple-200 dark:border-purple-800">
            В {{ acc.currency }}
          </span>
        </div>

        <div class="pt-4 mt-auto border-t border-theme-light-border dark:border-theme-dark-border flex items-end justify-between gap-4">
          <div class="flex items-baseline gap-1.5 whitespace-nowrap overflow-hidden">
            <span class="text-2xl font-black font-mono text-slate-900 dark:text-white tracking-tight truncate">
              {{ formatMoney(settings.convert(acc.balance, acc.currency)) }}
            </span>
            <span class="text-lg font-bold text-purple-500 dark:text-purple-400">
              {{ getSymbol(settings.baseCurrency) }}
            </span>
          </div>

          <button
            @click="askDelete(acc)"
            title="Удалить счёт"
            class="shrink-0 p-2.5 text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-xl transition"
          >
            <Trash2 class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Плашка перевода между счетами -->
    <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-3xl p-6 shadow-sm space-y-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-purple-100 dark:bg-purple-900/60 text-purple-600 dark:text-purple-300 flex items-center justify-center shrink-0">
          <ArrowLeftRight class="w-5 h-5" />
        </div>
        <h3 class="text-base font-black text-slate-800 dark:text-purple-100">Перевести деньги между счетами</h3>
      </div>

      <form @submit.prevent="executeTransfer" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
        <div>
          <label class="block text-xs font-bold text-theme-light-muted mb-1">Сумма и валюта</label>
          <div class="flex gap-2">
            <FormattedNumberInput
              v-model="transferForm.amount"
              placeholder="0"
              inputClass="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl px-3 py-2.5 text-sm font-bold font-mono outline-none"
            />
            <div class="w-24 shrink-0">
              <CustomSelect v-model="transferForm.currency" :options="currencySymbolOptions" />
            </div>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-theme-light-muted mb-1">Откуда списать</label>
          <CustomSelect v-model="transferForm.from_account_id" :options="accountSelectOptions" placeholder="Выберите счёт" />
        </div>

        <div>
          <label class="block text-xs font-bold text-theme-light-muted mb-1">Куда зачислить</label>
          <CustomSelect v-model="transferForm.to_account_id" :options="toAccountSelectOptions" placeholder="Выберите счёт" />
        </div>

        <div>
          <button
            type="submit"
            :disabled="transferDisabled"
            class="w-full bg-theme-accent-primary hover:bg-theme-accent-hover text-white text-xs px-4 py-3 rounded-xl font-bold transition shadow-md shadow-purple-500/20 disabled:opacity-50"
          >
            Перевести
          </button>
        </div>
      </form>
    </div>

    <!-- Модалка добавления счёта -->
    <Teleport to="body">
      <div v-if="showModal" @click.self="showModal = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
        <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
          <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-4">Новый счёт</h3>
          <form @submit.prevent="createAccount" class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-theme-light-muted mb-1">Название</label>
              <input v-model="form.name" required placeholder="Т-Банк или Сбер" class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none text-slate-800 dark:text-purple-100" />
            </div>
            <div>
              <label class="block text-xs font-bold text-theme-light-muted mb-1">Валюта счёта</label>
              <CustomSelect v-model="form.currency" :options="currencyOptions" />
            </div>
            <div>
              <label class="block text-xs font-bold text-theme-light-muted mb-1">Стартовый баланс</label>
              <input v-model.number="form.balance" type="number" step="any" min="0" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm font-mono outline-none text-slate-800 dark:text-purple-100" />
            </div>
            <div class="flex items-center gap-2 pt-1">
              <input type="checkbox" v-model="form.is_investment" id="inv" class="rounded accent-purple-600 w-4 h-4 cursor-pointer" />
              <label for="inv" class="text-xs font-semibold text-slate-700 dark:text-purple-200 cursor-pointer">Инвестиционный счёт</label>
            </div>
            <div class="flex justify-end gap-2 pt-3">
              <button type="button" @click="showModal = false" class="px-4 py-2 text-xs font-bold rounded-xl border border-theme-light-border hover:bg-slate-100">Отмена</button>
              <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary text-white rounded-xl shadow-md">Создать</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Модалка удаления счёта -->
    <Teleport to="body">
      <div v-if="deleteTarget" @click.self="deleteTarget = null" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
        <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border rounded-2xl shadow-2xl w-full max-w-sm p-6 text-center">
          <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-2">Удалить "{{ deleteTarget.name }}"?</h3>
          <p class="text-sm text-theme-light-muted mb-6">Вместе со счетом могут быть удалены связанные данные.</p>
          <div class="flex justify-center gap-3">
            <button @click="deleteTarget = null" class="px-5 py-2.5 text-sm font-bold rounded-xl border border-theme-light-border hover:bg-slate-100">Отмена</button>
            <button @click="confirmDelete" class="px-5 py-2.5 text-sm font-bold bg-red-500 text-white rounded-xl shadow-md">Удалить</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { Plus, Trash2, ArrowLeftRight } from 'lucide-vue-next';
import api from '@/api';
import CustomSelect from '@/components/CustomSelect.vue';
import FormattedNumberInput from '@/components/FormattedNumberInput.vue';
import { useSettingsStore } from '@/stores/settings';

const settings = useSettingsStore();
const accounts = ref([]);
const showModal = ref(false);
const deleteTarget = ref(null);
const transferLoading = ref(false);

const currencyOptions = [
  { label: 'RUB (₽)', value: 'RUB' },
  { label: 'USD ($)', value: 'USD' },
  { label: 'AMD (֏)', value: 'AMD' }
];

const currencySymbolOptions = [
  { label: '₽', value: 'RUB' },
  { label: '$', value: 'USD' },
  { label: '֏', value: 'AMD' }
];

const form = reactive({ name: '', currency: 'RUB', balance: 0, is_investment: false });
const transferForm = reactive({ from_account_id: '', to_account_id: '', amount: null, currency: 'RUB' });

const accountSelectOptions = computed(() => accounts.value.map(a => ({ label: `${a.name} (${settings.getSymbol(a.currency)})`, value: a.id })));
const toAccountSelectOptions = computed(() => accounts.value.filter(a => a.id !== transferForm.from_account_id).map(a => ({ label: `${a.name} (${settings.getSymbol(a.currency)})`, value: a.id })));

const transferDisabled = computed(() => {
  return transferLoading.value || !transferForm.amount || !transferForm.from_account_id || !transferForm.to_account_id || transferForm.from_account_id === transferForm.to_account_id;
});

function formatMoney(val) { return Number(val).toLocaleString('ru-RU', { minimumFractionDigits: 2 }); }
function getSymbol(cur) { const map = { RUB: '₽', USD: '$', AMD: '֏' }; return map[cur] || cur; }

async function fetchAccounts() {
  const { data } = await api.get('/accounts');
  accounts.value = data;
  if (accounts.value.length > 0 && !transferForm.from_account_id) transferForm.from_account_id = accounts.value[0].id;
  if (accounts.value.length > 1 && !transferForm.to_account_id) transferForm.to_account_id = accounts.value[1].id;
}

async function createAccount() {
  await api.post('/accounts', form);
  showModal.value = false;
  form.name = ''; form.balance = 0; form.is_investment = false;
  await fetchAccounts();
}

async function executeTransfer() {
  if (transferDisabled.value) return;
  transferLoading.value = true;
  try {
    await api.post('/transactions/transfer', {
      from_account_id: transferForm.from_account_id,
      to_account_id: transferForm.to_account_id,
      amount: transferForm.amount,
      currency: transferForm.currency,
      note: 'Перевод между счетами'
    });
    transferForm.amount = null;
    await fetchAccounts();
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка выполнения перевода');
  } finally {
    transferLoading.value = false;
  }
}

function askDelete(acc) { deleteTarget.value = acc; }
async function confirmDelete() {
  if (!deleteTarget.value) return;
  await api.delete(`/accounts/${deleteTarget.value.id}`);
  deleteTarget.value = null;
  await fetchAccounts();
}

onMounted(fetchAccounts);
</script>