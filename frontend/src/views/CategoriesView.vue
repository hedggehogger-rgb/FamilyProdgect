<template>
  <div class="space-y-8">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-xl font-black text-slate-800 dark:text-purple-100">Категории и лимиты</h2>
        <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted mt-1">Управление бюджетом и лимитами трат</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="bg-theme-accent-primary hover:bg-theme-accent-hover text-white text-xs px-4 py-2.5 rounded-xl font-bold transition shadow-md shadow-purple-500/20 flex items-center gap-2"
      >
        <Plus class="w-4 h-4" /> Новая категория
      </button>
    </div>

    <!-- РАСХОДЫ -->
    <div>
      <h3 class="text-lg font-black text-rose-600 dark:text-rose-400 mb-4 border-b border-theme-light-border dark:border-theme-dark-border pb-2">Статьи расходов</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div v-for="cat in expenseCategories" :key="cat.id" class="bg-theme-light-card dark:bg-theme-dark-card p-6 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm flex flex-col justify-between">
          <div>
            <div class="flex justify-between items-start mb-3">
              <span class="text-xs font-bold px-2.5 py-1 rounded-full border" :style="{ borderColor: cat.color, color: cat.color, backgroundColor: cat.color + '18' }">{{ groupLabels[cat.group] }}</span>
              <span class="text-xs font-semibold text-theme-light-muted dark:text-theme-dark-muted">{{ freqLabels[cat.frequency] }}</span>
            </div>
            <div class="flex items-center gap-2.5">
              <span class="w-3.5 h-3.5 rounded-full shrink-0 shadow-sm" :style="{ backgroundColor: cat.color }"></span>
              <h3 class="font-black text-base text-slate-800 dark:text-purple-100">{{ cat.name }}</h3>
            </div>
            <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted mt-2">{{ formatSchedule(cat) }}</p>

            <div v-if="cat.default_amount" class="mt-2 text-[11px] font-bold font-mono text-rose-500 bg-rose-50 dark:bg-rose-950/40 px-2 py-1 rounded">
              План: {{ formatMoney(cat.default_amount) }} {{ settings.getSymbol('RUB') }} ({{ getAccountName(cat.default_account_id) }})
            </div>

            <!-- Индикатор лимита -->
            <div v-if="limitsMap[cat.id]" @click="openLimitHistory(cat)" class="mt-4 p-3 bg-purple-50/50 dark:bg-theme-dark-surface/60 rounded-xl border border-theme-light-border dark:border-theme-dark-border cursor-pointer hover:border-purple-300 transition group">
              <div class="flex justify-between text-xs font-bold mb-1">
                <span class="group-hover:text-purple-700 dark:group-hover:text-purple-300">Лимит: {{ formatMoney(limitsMap[cat.id].limit_amount) }} {{ settings.getSymbol(limitsMap[cat.id].currency) }}</span>
                <span :class="limitsMap[cat.id].is_exceeded ? 'text-red-500' : 'text-purple-600'">{{ limitsMap[cat.id].percentage_used }}%</span>
              </div>
              <div class="w-full bg-slate-200 dark:bg-purple-950 h-2 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all" :class="limitsMap[cat.id].is_exceeded ? 'bg-red-500' : 'bg-theme-accent-primary'" :style="{ width: Math.min(100, limitsMap[cat.id].percentage_used) + '%' }"></div>
              </div>
              <p class="text-[9px] text-center mt-1.5 text-purple-400 opacity-0 group-hover:opacity-100 transition">Посмотреть расходы</p>
            </div>
          </div>

          <div class="flex items-center justify-between pt-4 mt-4 border-t border-theme-light-border dark:border-theme-dark-border text-xs font-bold gap-2">
            <button @click="openLimitModal(cat)" class="text-purple-600 dark:text-purple-400 hover:underline whitespace-nowrap">
              {{ limitsMap[cat.id] ? 'Лимит' : '+ Лимит' }}
            </button>
            <div class="flex items-center gap-3.5 whitespace-nowrap">
              <button @click="openEditModal(cat)" class="text-purple-600 dark:text-purple-400 hover:underline">Изменить</button>
              <button @click="askDelete(cat)" class="text-red-500 hover:underline">Удалить</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ДОХОДЫ И ИНВЕСТИЦИИ -->
    <div>
      <h3 class="text-lg font-black text-emerald-600 dark:text-emerald-400 mb-4 border-b border-theme-light-border dark:border-theme-dark-border pb-2 mt-8">Доходы и Инвестиции</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div v-for="cat in incomeCategories" :key="cat.id" class="bg-theme-light-card dark:bg-theme-dark-card p-6 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm flex flex-col justify-between">
          <div>
            <div class="flex justify-between items-start mb-3">
              <span class="text-xs font-bold px-2.5 py-1 rounded-full border" :style="{ borderColor: cat.color, color: cat.color, backgroundColor: cat.color + '18' }">{{ groupLabels[cat.group] }}</span>
              <span class="text-xs font-semibold text-theme-light-muted dark:text-theme-dark-muted">{{ freqLabels[cat.frequency] }}</span>
            </div>
            <div class="flex items-center gap-2.5">
              <span class="w-3.5 h-3.5 rounded-full shrink-0 shadow-sm" :style="{ backgroundColor: cat.color }"></span>
              <h3 class="font-black text-base text-slate-800 dark:text-purple-100">{{ cat.name }}</h3>
            </div>
            <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted mt-2">{{ formatSchedule(cat) }}</p>
            <div v-if="cat.default_amount" class="mt-2 text-[11px] font-bold font-mono text-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-1 rounded">
              План: {{ formatMoney(cat.default_amount) }} {{ settings.getSymbol('RUB') }} ({{ getAccountName(cat.default_account_id) }})
            </div>
          </div>
          <div class="flex items-center justify-between pt-4 mt-4 border-t border-theme-light-border dark:border-theme-dark-border text-xs font-bold gap-3">
            <button @click="openEditModal(cat)" class="text-purple-600 dark:text-purple-400 hover:underline whitespace-nowrap">Изменить</button>
            <button @click="askDelete(cat)" class="text-red-500 hover:underline whitespace-nowrap">Удалить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка Лимита -->
    <Teleport to="body">
      <div v-if="limitCat" @click.self="limitCat = null" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
        <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
          <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-4">Лимит для "{{ limitCat.name }}"</h3>
          <form @submit.prevent="saveLimit" class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-theme-light-muted mb-1">Сумма в месяц ({{ settings.getSymbol('RUB') }})</label>
              <FormattedNumberInput v-model="limitForm.amount" placeholder="10 000" inputClass="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm font-mono font-bold outline-none text-slate-800 dark:text-purple-100" />
            </div>
            <div class="flex items-center justify-between pt-2">
              <button v-if="limitsMap[limitCat.id]" type="button" @click="deleteLimit" class="px-3 py-2 text-xs font-bold text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-xl transition">Удалить лимит</button>
              <div class="flex gap-2 ml-auto">
                <button type="button" @click="limitCat = null" class="px-4 py-2 text-xs font-bold rounded-xl border border-theme-light-border hover:bg-slate-100 transition">Отмена</button>
                <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary hover:bg-theme-accent-hover text-white rounded-xl shadow-md transition">Сохранить</button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Модалка создания/редактирования категории -->
    <CategoryModal :show="showCreateModal || !!editCat" :isEdit="!!editCat" :formData="editCat ? editForm : form" :groupOptions="groupOptions" :frequencyOptions="frequencyOptions" :weekDayOptions="weekDayOptions" :quarterMonthOptions="quarterMonthOptions" :yearMonthOptions="yearMonthOptions" :accountOptions="accountOptions" @close="closeModal" @submit="editCat ? updateCategory() : createCategory()" />

    <!-- Модалка истории лимита -->
    <Teleport to="body">
      <div v-if="historyCat" @click.self="historyCat = null" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
        <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border rounded-2xl shadow-2xl w-full max-w-lg p-6 max-h-[80vh] flex flex-col">
          <div class="flex justify-between items-center mb-4 pb-2 border-b border-theme-light-border">
            <h3 class="font-black text-base text-slate-800 dark:text-purple-100">История расходов: {{ historyCat.name }}</h3>
            <button @click="historyCat = null" class="text-xs font-bold px-2 py-1 hover:bg-purple-100 rounded">Закрыть</button>
          </div>
          <div class="flex-1 overflow-y-auto">
            <div v-if="historyLoading" class="py-10 text-center"><div class="animate-spin inline-block w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full"></div></div>
            <div v-else-if="historyTxs.length === 0" class="py-8 text-center text-xs text-theme-light-muted">В этом месяце расходов не было</div>
            <div v-else class="divide-y divide-theme-light-border dark:divide-theme-dark-border">
              <div v-for="t in historyTxs" :key="t.id" class="py-2.5 flex justify-between items-center">
                <div>
                  <p class="text-sm font-bold text-slate-800 dark:text-purple-200">{{ t.note || 'Без описания' }}</p>
                  <p class="text-[10px] text-theme-light-muted">{{ new Date(t.date).toLocaleDateString('ru-RU') }} • {{ getAccountName(t.account_id) }}</p>
                </div>
                <span class="text-sm font-black font-mono text-rose-500">-{{ formatMoney(t.amount) }} {{ settings.getSymbol(t.currency) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Модалка удаления категории -->
    <Teleport to="body">
      <div v-if="deleteTarget" @click.self="deleteTarget = null" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
        <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border rounded-2xl shadow-2xl w-full max-w-sm p-6 text-center">
          <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-2">Удалить категорию?</h3>
          <p class="text-sm text-theme-light-muted mb-6">Связанные операции останутся без категории.</p>
          <div class="flex justify-center gap-3">
            <button @click="deleteTarget = null" class="px-5 py-2.5 text-sm font-bold rounded-xl border border-theme-light-border hover:bg-slate-100 transition">Отмена</button>
            <button @click="confirmDelete" class="px-5 py-2.5 text-sm font-bold bg-red-500 hover:bg-red-600 text-white rounded-xl shadow-md transition">Удалить</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { Plus } from 'lucide-vue-next';
import api from '@/api';
import CategoryModal from './CategoryModal.vue';
import FormattedNumberInput from '@/components/FormattedNumberInput.vue';
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
const groupLabels = { INCOME: 'Доход', EXPENSE: 'Расход', INVESTMENT: 'Инвестиции' };
const freqLabels = { NONE: 'Разовая', DAILY: 'Ежедневно', WEEKLY: 'Еженедельно', MONTHLY: 'Ежемесячно', QUARTERLY: 'Ежеквартально', ANNUALLY: 'Ежегодно' };
const groupOptions = [{ label: 'Расход', value: 'EXPENSE' }, { label: 'Доход', value: 'INCOME' }, { label: 'Инвестиции', value: 'INVESTMENT' }];
const frequencyOptions = [{ label: 'Разовая / Без расписания', value: 'NONE' }, { label: 'Ежедневно', value: 'DAILY' }, { label: 'Еженедельно', value: 'WEEKLY' }, { label: 'Ежемесячно', value: 'MONTHLY' }, { label: 'Ежеквартально', value: 'QUARTERLY' }, { label: 'Ежегодно', value: 'ANNUALLY' }];
const weekDayOptions = [{ label: 'Пн', value: 1 }, { label: 'Вт', value: 2 }, { label: 'Ср', value: 3 }, { label: 'Чт', value: 4 }, { label: 'Пт', value: 5 }, { label: 'Сб', value: 6 }, { label: 'Вс', value: 7 }];
const quarterMonthOptions = [{ label: '1-й месяц', value: 1 }, { label: '2-й месяц', value: 2 }, { label: '3-й месяц', value: 3 }];
const yearMonthOptions = [{ label: 'Янв', value: 1 }, { label: 'Фев', value: 2 }, { label: 'Мар', value: 3 }, { label: 'Апр', value: 4 }, { label: 'Май', value: 5 }, { label: 'Июн', value: 6 }, { label: 'Июл', value: 7 }, { label: 'Авг', value: 8 }, { label: 'Сен', value: 9 }, { label: 'Окт', value: 10 }, { label: 'Ноя', value: 11 }, { label: 'Дек', value: 12 }];

const form = reactive({ name: '', color: '#8b5cf6', group: 'EXPENSE', frequency: 'NONE', day_of_month: 1, day_of_week: 1, recurrence_month: 1, default_amount: null, default_account_id: null });
const editForm = reactive({ name: '', color: '#8b5cf6', frequency: 'NONE', day_of_month: 1, day_of_week: 1, recurrence_month: 1, default_amount: null, default_account_id: null });
const limitForm = reactive({ amount: 10000, months: 12 });

const accountOptions = computed(() => accounts.value.map(a => ({ label: `${a.name} (${settings.getSymbol(a.currency)})`, value: a.id })));
function getAccountName(id) { if (!id) return '?'; const acc = accounts.value.find(a => a.id === id); return acc ? acc.name : '—'; }
function formatMoney(val) { return (!val || isNaN(val)) ? '0' : Number(val).toLocaleString('ru-RU'); }

function formatSchedule(cat) {
  const act = cat.group === 'INCOME' ? 'начисления' : 'списания';
  if (cat.frequency === 'DAILY') return 'Каждый день';
  if (cat.frequency === 'WEEKLY') return `Еженедельно: ${weekDayOptions.find(o => o.value === cat.day_of_week)?.label || cat.day_of_week}`;
  if (cat.frequency === 'MONTHLY') return `День ${act}: ${cat.day_of_month || 1}-е число`;
  if (cat.frequency === 'QUARTERLY') return `Ежеквартально: ${cat.recurrence_month || 1}-й мес, ${cat.day_of_month || 1} число`;
  if (cat.frequency === 'ANNUALLY') return `Ежегодно: ${cat.day_of_month || 1} ${yearMonthOptions.find(o => o.value === cat.recurrence_month)?.label}`;
  return 'Без расписания';
}

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
  await api.post('/categories', payload); closeModal(); form.name = ''; form.default_amount = null; await loadData();
}

function openEditModal(c) {
  editCat.value = c; editForm.name = c.name; editForm.color = c.color || '#8b5cf6'; editForm.frequency = c.frequency; editForm.day_of_month = c.day_of_month || 1; editForm.day_of_week = c.day_of_week || 1; editForm.recurrence_month = c.recurrence_month || 1; editForm.default_amount = c.default_amount || null; editForm.default_account_id = c.default_account_id || (accounts.value.length > 0 ? accounts.value[0].id : null);
}

async function updateCategory() {
  const payload = { ...editForm };
  if (payload.frequency === 'NONE') { payload.default_amount = null; payload.default_account_id = null; }
  await api.put(`/categories/${editCat.value.id}`, payload); closeModal(); await loadData();
}

function openLimitModal(c) {
  limitCat.value = c;
  limitForm.amount = limitsMap.value[c.id]?.limit_amount ? Number(limitsMap.value[c.id].limit_amount) : 10000;
}

async function saveLimit() {
  if (!limitForm.amount || limitForm.amount <= 0) return;
  await api.post('/limits', { category_id: limitCat.value.id, limit_amount: limitForm.amount, currency: 'RUB', months_duration: limitForm.months });
  limitCat.value = null; await loadData();
}

async function deleteLimit() {
  if (!limitCat.value) return;
  try {
    await api.delete(`/limits/${limitCat.value.id}`);
    delete limitsMap.value[limitCat.value.id];
    limitCat.value = null; await loadData();
  } catch (e) { alert('Не удалось удалить лимит'); }
}

function askDelete(cat) { deleteTarget.value = cat; }
async function confirmDelete() { if (!deleteTarget.value) return; await api.delete(`/categories/${deleteTarget.value.id}`); deleteTarget.value = null; await loadData(); }
onMounted(loadData);
</script>