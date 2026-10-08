<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-xl font-black text-slate-800 dark:text-purple-100">Банковские и наличные счета</h2>
        <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted mt-1">Все финансовые источники семьи</p>
      </div>
      <button
        @click="showModal = true"
        class="bg-theme-accent-primary hover:bg-theme-accent-hover text-white text-xs px-4 py-2.5 rounded-xl font-bold transition shadow-md shadow-purple-500/20 flex items-center gap-2"
      >
        <Plus class="w-4 h-4" />
        Добавить счёт
      </button>
    </div>

    <!-- Сетка счетов -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div
        v-for="acc in accounts"
        :key="acc.id"
        class="bg-theme-light-card dark:bg-theme-dark-card rounded-2xl p-6 border border-theme-light-border dark:border-theme-dark-border shadow-sm flex flex-col justify-between"
      >
        <div>
          <div class="flex justify-between items-start">
            <span class="text-xs font-bold uppercase tracking-wider text-purple-600 dark:text-purple-400">
              {{ acc.is_investment ? 'Инвестиционный' : 'Обычный счёт' }}
            </span>
            <span class="text-xs px-2.5 py-0.5 rounded-full font-bold font-mono bg-purple-100 dark:bg-purple-900/60 text-purple-800 dark:text-purple-200">
              {{ acc.currency }}
            </span>
          </div>
          <h3 class="text-xl font-black text-slate-800 dark:text-purple-100 mt-2">{{ acc.name }}</h3>
        </div>

        <div class="mt-6 pt-4 border-t border-theme-light-border dark:border-theme-dark-border flex items-center justify-between">
          <p class="text-2xl font-black font-mono text-slate-900 dark:text-white">
            {{ formatMoney(acc.balance) }} <span class="text-lg font-normal text-purple-500">{{ getSymbol(acc.currency) }}</span>
          </p>

          <button
            @click="deleteAccount(acc)"
            title="Удалить счёт"
            class="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/40 p-2 rounded-xl transition"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Модалка добавления счёта -->
    <div v-if="showModal" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-4">Новый счёт</h3>
        <form @submit.prevent="createAccount" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Название</label>
            <input
              v-model="form.name"
              required
              placeholder="Т-Банк, Сбер или Наличные"
              class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none focus:ring-2 focus:ring-purple-500 text-slate-800 dark:text-purple-100"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Валюта счёта</label>
            <CustomSelect
              v-model="form.currency"
              :options="currencyOptions"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Стартовый баланс</label>
            <input
              v-model.number="form.balance"
              type="number"
              step="any"
              min="0"
              required
              class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm font-mono outline-none text-slate-800 dark:text-purple-100"
            />
          </div>
          <div class="flex items-center gap-2 pt-1">
            <input type="checkbox" v-model="form.is_investment" id="inv" class="rounded accent-purple-600 w-4 h-4 cursor-pointer" />
            <label for="inv" class="text-xs font-semibold text-slate-700 dark:text-purple-200 cursor-pointer">Это инвестиционный счёт</label>
          </div>
          <div class="flex justify-end gap-2 pt-3">
            <button type="button" @click="showModal = false" class="px-4 py-2 text-xs font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition">
              Отмена
            </button>
            <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary hover:bg-theme-accent-hover text-white rounded-xl shadow-md transition">
              Создать
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { Plus, Trash2 } from 'lucide-vue-next';
import api from '@/api';
import CustomSelect from '@/components/CustomSelect.vue';

const accounts = ref([]);
const showModal = ref(false);

const currencyOptions = [
  { label: 'RUB (₽)', value: 'RUB' },
  { label: 'USD ($)', value: 'USD' },
  { label: 'AMD (֏)', value: 'AMD' }
];

const form = reactive({
  name: '',
  currency: 'RUB',
  balance: 0,
  is_investment: false
});

function formatMoney(val) {
  return Number(val).toLocaleString('ru-RU', { minimumFractionDigits: 2 });
}

function getSymbol(cur) {
  const map = { RUB: '₽', USD: '$', AMD: '֏' };
  return map[cur] || cur;
}

async function fetchAccounts() {
  const { data } = await api.get('/accounts');
  accounts.value = data;
}

async function createAccount() {
  await api.post('/accounts', form);
  showModal.value = false;
  form.name = '';
  form.balance = 0;
  form.is_investment = false;
  await fetchAccounts();
}

async function deleteAccount(acc) {
  if (!confirm(`Вы действительно хотите удалить счёт "${acc.name}"?`)) return;
  try {
    await api.delete(`/accounts/${acc.id}`);
    await fetchAccounts();
  } catch (err) {
    alert(err.response?.data?.detail || 'Не удалось удалить счёт');
  }
}

onMounted(fetchAccounts);
</script>