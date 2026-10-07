<template>
  <div class="space-y-6">
    <!-- Блок со счетами и кнопкой добавления счёта -->
    <div class="flex justify-between items-center">
      <h2 class="text-lg font-bold text-slate-800">Банковские и наличные счета</h2>
      <button @click="showAddAccount = true" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-4 py-2 rounded-lg font-medium transition shadow-sm">
        + Добавить счёт
      </button>
    </div>

    <!-- Сетка карточек счетов -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <div
        v-for="acc in accounts"
        :key="acc.id"
        class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm relative overflow-hidden"
      >
        <div class="flex justify-between items-start">
          <div>
            <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Счёт</span>
            <h3 class="text-lg font-bold text-slate-800">{{ acc.name }}</h3>
          </div>
          <span :class="acc.is_investment ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'" class="text-xs px-2 py-0.5 rounded font-mono">
            {{ acc.currency }}
          </span>
        </div>
        <div class="mt-4">
          <p class="text-2xl font-black text-slate-900 tracking-tight">
            {{ formatMoney(acc.balance) }} <span class="text-base font-normal text-slate-500">{{ getSymbol(acc.currency) }}</span>
          </p>
          <span v-if="acc.is_investment" class="text-xs text-amber-600 font-medium">Инвестиционный</span>
        </div>
      </div>
    </div>

    <!-- Блок быстрого внесения операции -->
    <div class="bg-white rounded-xl p-6 border border-slate-200 shadow-sm mt-8">
      <h3 class="text-base font-bold text-slate-800 mb-4">Быстрая запись расхода / дохода</h3>
      <form @submit.prevent="submitTransaction" class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-xs font-medium text-slate-600">Тип</label>
          <select v-model="txForm.type" class="mt-1 w-full border rounded-lg p-2 text-sm">
            <option value="EXPENSE_PLANNED">Расход (плановый)</option>
            <option value="EXPENSE_IMPULSE">Расход (импульсивный)</option>
            <option value="INCOME">Доход</option>
            <option value="INVESTMENT">Инвестиция</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-600">Счёт списания</label>
          <select v-model="txForm.account_id" required class="mt-1 w-full border rounded-lg p-2 text-sm">
            <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
              {{ acc.name }} ({{ acc.currency }})
            </option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-600">Категория</label>
          <select v-model="txForm.category_id" class="mt-1 w-full border rounded-lg p-2 text-sm">
            <option :value="null">Без категории</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }} ({{ cat.group }})
            </option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-600">Сумма</label>
          <input v-model.number="txForm.amount" type="number" step="0.01" min="0.01" required placeholder="0.00" class="mt-1 w-full border rounded-lg p-2 text-sm font-mono" />
        </div>

        <div class="flex items-end">
          <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 rounded-lg text-sm transition">
            Записать
          </button>
        </div>
      </form>
    </div>

    <!-- Модалка добавления счёта -->
    <div v-if="showAddAccount" class="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6">
        <h3 class="text-base font-bold text-slate-800 mb-4">Новый счёт</h3>
        <form @submit.prevent="createAccount" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-slate-600">ID счёта (латиница)</label>
            <input v-model="accForm.id" required placeholder="tinkoff-black" class="mt-1 w-full border rounded-lg p-2 text-sm font-mono" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-600">Название</label>
            <input v-model="accForm.name" required placeholder="Т-Банк Основной" class="mt-1 w-full border rounded-lg p-2 text-sm" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-600">Валюта</label>
            <select v-model="accForm.currency" class="mt-1 w-full border rounded-lg p-2 text-sm">
              <option value="RUB">RUB (₽)</option>
              <option value="USD">USD ($)</option>
              <option value="AMD">AMD (֏)</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-600">Стартовый баланс</label>
            <input v-model.number="accForm.balance" type="number" step="0.01" class="mt-1 w-full border rounded-lg p-2 text-sm" />
          </div>
          <div class="flex items-center gap-2">
            <input type="checkbox" v-model="accForm.is_investment" id="inv" />
            <label for="inv" class="text-xs text-slate-700">Инвестиционный счёт</label>
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="showAddAccount = false" class="px-4 py-2 text-xs border rounded-lg">Отмена</button>
            <button type="submit" class="px-4 py-2 text-xs bg-indigo-600 text-white rounded-lg">Создать</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '@/api';

const accounts = ref([]);
const categories = ref([]);
const showAddAccount = ref(false);

const accForm = reactive({
  id: '',
  name: '',
  currency: 'RUB',
  balance: 0,
  is_investment: false
});

const txForm = reactive({
  type: 'EXPENSE_PLANNED',
  account_id: '',
  category_id: null,
  amount: null,
  currency: 'RUB',
});

function formatMoney(val) {
  return Number(val).toLocaleString('ru-RU', { minimumFractionDigits: 2 });
}

function getSymbol(cur) {
  const map = { RUB: '₽', USD: '$', AMD: '֏' };
  return map[cur] || cur;
}

async function loadData() {
  const [accRes, catRes] = await Promise.all([
    api.get('/accounts'),
    api.get('/categories')
  ]);
  accounts.value = accRes.data;
  categories.value = catRes.data;
  if (accounts.value.length && !txForm.account_id) {
    txForm.account_id = accounts.value[0].id;
    txForm.currency = accounts.value[0].currency;
  }
}

async function createAccount() {
  await api.post('/accounts', accForm);
  showAddAccount.value = false;
  accForm.id = '';
  accForm.name = '';
  accForm.balance = 0;
  await loadData();
}

async function submitTransaction() {
  const acc = accounts.value.find(a => a.id === txForm.account_id);
  await api.post('/transactions', {
    ...txForm,
    currency: acc?.currency || 'RUB'
  });
  txForm.amount = null;
  await loadData();
}

onMounted(loadData);
</script>