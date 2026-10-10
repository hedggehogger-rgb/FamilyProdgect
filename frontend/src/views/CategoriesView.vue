<template>
  <div class="space-y-8">
    <!-- Плавающая кнопка создания категории -->
    <button
      @click="showCreateModal = true"
      title="Новая категория"
      class="fixed top-20 right-8 z-30 bg-theme-accent-primary hover:bg-theme-accent-hover text-white p-3 rounded-2xl font-bold transition-all shadow-lg shadow-purple-500/30 hover:scale-105 active:scale-95 flex items-center justify-center"
    >
      <Plus class="w-5 h-5 stroke-[2.5]" />
    </button>

    <!-- РАСХОДЫ -->
    <div>
      <h3 class="text-lg font-black text-rose-600 dark:text-rose-400 mb-4 border-b border-theme-light-border dark:border-theme-dark-border pb-2">Расходы</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <CategoryCard
          v-for="cat in expenseCategories"
          :key="cat.id"
          :category="cat"
          :limit="limitsMap[cat.id]"
          :isExpense="true"
          @open-history="openLimitHistory"
          @open-limit="openLimitModal"
          @edit="openEditModal"
          @delete="askDelete"
        />
      </div>
    </div>

    <!-- ДОХОДЫ -->
    <div>
      <h3 class="text-lg font-black text-emerald-600 dark:text-emerald-400 mb-4 border-b border-theme-light-border dark:border-theme-dark-border pb-2 mt-8">Доходы</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <CategoryCard
          v-for="cat in incomeCategories"
          :key="cat.id"
          :category="cat"
          :isExpense="false"
          @edit="openEditModal"
          @delete="askDelete"
        />
      </div>
    </div>

    <!-- Модалки -->
    <LimitModal
      :category="limitCat"
      :initialAmount="limitsMap[limitCat?.id]?.limit_amount ? Number(limitsMap[limitCat?.id].limit_amount) : 10000"
      :hasLimit="!!limitsMap[limitCat?.id]"
      @close="limitCat = null"
      @save="saveLimit"
      @delete="deleteLimit"
    />

    <CategoryModal
      :show="showCreateModal || !!editCat"
      :isEdit="!!editCat"
      :formData="editCat ? editForm : form"
      :groupOptions="groupOptions"
      :frequencyOptions="frequencyOptions"
      :weekDayOptions="weekDayOptions"
      :quarterMonthOptions="quarterMonthOptions"
      :yearMonthOptions="yearMonthOptions"
      :accountOptions="accountOptions"
      :currencyOptions="currencyOptions"
      @close="closeModal"
      @submit="editCat ? updateCategory() : createCategory()"
    />

    <LimitHistoryModal
      :category="historyCat"
      :transactions="historyTxs"
      :loading="historyLoading"
      @close="historyCat = null"
    />

    <CategoryDeleteModal
      :category="deleteTarget"
      @close="deleteTarget = null"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { Plus } from 'lucide-vue-next';
import api from '@/api';
import CategoryModal from './CategoryModal.vue';
import CategoryCard from './categories/CategoryCard.vue';
import LimitModal from './categories/LimitModal.vue';
import LimitHistoryModal from './categories/LimitHistoryModal.vue';
import CategoryDeleteModal from './categories/CategoryDeleteModal.vue';
import { useSettingsStore } from '@/stores/settings';

const settings = useSettingsStore();
const categories = ref([]);
const accounts = ref([]);
const limitsMap = ref({});
const showCreateModal = ref(false);
const editCat = ref(null);
const limitCat = ref(null);
const deleteTarget = ref(null);
const historyCat = ref(null);
const historyTxs = ref([]);
const historyLoading = ref(false);

const expenseCategories = computed(() => categories.value.filter(c => c.group === 'EXPENSE'));
const incomeCategories = computed(() => categories.value.filter(c => c.group !== 'EXPENSE'));

const groupOptions = [{ label: 'Расход', value: 'EXPENSE' }, { label: 'Доход', value: 'INCOME' }, { label: 'Инвестиции', value: 'INVESTMENT' }];
const frequencyOptions = [{ label: 'Разовая / Без расписания', value: 'NONE' }, { label: 'Ежедневно', value: 'DAILY' }, { label: 'Еженедельно', value: 'WEEKLY' }, { label: 'Ежемесячно', value: 'MONTHLY' }, { label: 'Ежеквартально', value: 'QUARTERLY' }, { label: 'Ежегодно', value: 'ANNUALLY' }];
const weekDayOptions = [{ label: 'Пн', value: 1 }, { label: 'Вт', value: 2 }, { label: 'Ср', value: 3 }, { label: 'Чт', value: 4 }, { label: 'Пт', value: 5 }, { label: 'Сб', value: 6 }, { label: 'Вс', value: 7 }];
const quarterMonthOptions = [{ label: '1-й месяц', value: 1 }, { label: '2-й месяц', value: 2 }, { label: '3-й месяц', value: 3 }];
const yearMonthOptions = [{ label: 'Янв', value: 1 }, { label: 'Фев', value: 2 }, { label: 'Мар', value: 3 }, { label: 'Апр', value: 4 }, { label: 'Май', value: 5 }, { label: 'Июн', value: 6 }, { label: 'Июл', value: 7 }, { label: 'Авг', value: 8 }, { label: 'Сен', value: 9 }, { label: 'Окт', value: 10 }, { label: 'Ноя', value: 11 }, { label: 'Дек', value: 12 }];

const currencyOptions = [{ label: '₽', value: 'RUB' }, { label: '$', value: 'USD' }, { label: '֏', value: 'AMD' }];

const form = reactive({ name: '', color: '#8b5cf6', group: 'EXPENSE', frequency: 'NONE', day_of_month: 1, day_of_week: 1, recurrence_month: 1, default_amount: null, default_currency: 'RUB', default_account_id: null, expires_at: null });
const editForm = reactive({ name: '', color: '#8b5cf6', frequency: 'NONE', day_of_month: 1, day_of_week: 1, recurrence_month: 1, default_amount: null, default_currency: 'RUB', default_account_id: null, expires_at: null });

const accountOptions = computed(() => accounts.value.map(a => ({ label: `${a.name} (${settings.getSymbol(a.currency)})`, value: a.id })));

function closeModal() { showCreateModal.value = false; editCat.value = null; }

async function loadData() {
  const [catRes, accRes] = await Promise.all([api.get('/categories'), api.get('/accounts')]);
  categories.value = catRes.data; accounts.value = accRes.data;
  if (accounts.value.length > 0 && !form.default_account_id) form.default_account_id = accounts.value[0].id;
  const now = new Date();
  for (const c of categories.value) {
    if (c.group === 'EXPENSE') {
      try {
        const { data: lim } = await api.get(`/limits/status/${c.id}?year=${now.getFullYear()}&month=${now.getMonth() + 1}`);
        limitsMap.value[c.id] = lim;
      } catch (e) { limitsMap.value[c.id] = null; }
    }
  }
}

async function openLimitHistory(cat) {
  historyCat.value = cat; historyLoading.value = true;
  try {
    const { data } = await api.get(`/transactions?category_id=${cat.id}&limit=100`);
    const now = new Date();
    historyTxs.value = data.items.filter(t => {
      const d = new Date(t.date);
      return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
    });
  } catch (e) {} finally { historyLoading.value = false; }
}

async function createCategory() {
  const payload = { ...form };
  if (payload.frequency === 'NONE') { payload.default_amount = null; payload.default_account_id = null; }
  if (payload.expires_at) payload.expires_at = `${payload.expires_at}T23:59:59`;
  await api.post('/categories', payload);
  closeModal();
  form.name = ''; form.default_amount = null; form.expires_at = null;
  await loadData();
}

function openEditModal(c) {
  editCat.value = c;
  editForm.name = c.name; editForm.color = c.color || '#8b5cf6'; editForm.frequency = c.frequency;
  editForm.day_of_month = c.day_of_month || 1; editForm.day_of_week = c.day_of_week || 1; editForm.recurrence_month = c.recurrence_month || 1;
  editForm.default_amount = c.default_amount || null; editForm.default_currency = c.default_currency || 'RUB';
  editForm.default_account_id = c.default_account_id || (accounts.value.length > 0 ? accounts.value[0].id : null);
  editForm.expires_at = c.expires_at ? c.expires_at.split('T')[0] : null;
}

async function updateCategory() {
  const payload = { ...editForm };
  if (payload.frequency === 'NONE') { payload.default_amount = null; payload.default_account_id = null; }
  payload.expires_at = payload.expires_at ? `${payload.expires_at}T23:59:59` : null;
  await api.put(`/categories/${editCat.value.id}`, payload);
  closeModal();
  await loadData();
}

function openLimitModal(c) { limitCat.value = c; }

async function saveLimit(amount) {
  if (!amount || amount <= 0) return;
  await api.post('/limits', { category_id: limitCat.value.id, limit_amount: amount, currency: 'RUB', months_duration: 12 });
  limitCat.value = null;
  await loadData();
}

async function deleteLimit() {
  if (!limitCat.value) return;
  try {
    await api.delete(`/limits/${limitCat.value.id}`);
    delete limitsMap.value[limitCat.value.id];
    limitCat.value = null;
    await loadData();
  } catch (e) { alert('Не удалось удалить лимит'); }
}

function askDelete(cat) { deleteTarget.value = cat; }

async function confirmDelete() {
  if (!deleteTarget.value) return;
  await api.delete(`/categories/${deleteTarget.value.id}`);
  deleteTarget.value = null;
  await loadData();
}

onMounted(loadData);
</script>