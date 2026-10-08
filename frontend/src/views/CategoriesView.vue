         <template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-xl font-black text-slate-800 dark:text-purple-100">Категории и лимиты</h2>
        <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted mt-1">Управление бюджетом и лимитами расходов</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="bg-theme-accent-primary hover:bg-theme-accent-hover text-white text-xs px-4 py-2.5 rounded-xl font-bold transition shadow-md shadow-purple-500/20 flex items-center gap-2"
      >
        <Plus class="w-4 h-4" />
        Новая категория
      </button>
    </div>

    <!-- Сетка категорий -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div
        v-for="cat in categories"
        :key="cat.id"
        class="bg-theme-light-card dark:bg-theme-dark-card p-6 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm flex flex-col justify-between"
      >
        <div>
          <div class="flex justify-between items-start mb-3">
            <span
              class="text-xs font-bold px-2.5 py-1 rounded-full border"
              :style="{ borderColor: cat.color, color: cat.color, backgroundColor: cat.color + '18' }"
            >
              {{ groupLabels[cat.group] }}
            </span>
            <span class="text-xs font-semibold text-theme-light-muted dark:text-theme-dark-muted">
              {{ freqLabels[cat.frequency] }}
            </span>
          </div>

          <div class="flex items-center gap-2.5">
            <span class="w-3.5 h-3.5 rounded-full shrink-0 shadow-sm" :style="{ backgroundColor: cat.color }"></span>
            <h3 class="font-black text-base text-slate-800 dark:text-purple-100">{{ cat.name }}</h3>
          </div>

          <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted mt-2">
            {{ formatSchedule(cat) }}
          </p>

          <div v-if="limitsMap[cat.id]" class="mt-4 p-3 bg-purple-50/50 dark:bg-theme-dark-surface/60 rounded-xl border border-theme-light-border dark:border-theme-dark-border">
            <div class="flex justify-between text-xs font-bold mb-1">
              <span>Лимит: {{ limitsMap[cat.id].limit_amount }} {{ limitsMap[cat.id].currency }}</span>
              <span :class="limitsMap[cat.id].is_exceeded ? 'text-red-500' : 'text-purple-600'">
                {{ limitsMap[cat.id].percentage_used }}%
              </span>
            </div>
            <div class="w-full bg-slate-200 dark:bg-purple-950 h-2 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all"
                :class="limitsMap[cat.id].is_exceeded ? 'bg-red-500' : 'bg-theme-accent-primary'"
                :style="{ width: Math.min(100, limitsMap[cat.id].percentage_used) + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between pt-4 mt-4 border-t border-theme-light-border dark:border-theme-dark-border text-xs font-bold">
          <div class="flex gap-3">
            <button @click="openLimitModal(cat)" class="text-purple-600 dark:text-purple-400 hover:underline">Лимит</button>
            <button @click="openEditModal(cat)" class="text-slate-600 dark:text-purple-300 hover:underline">Изменить</button>
          </div>
          <button @click="deleteCategory(cat.id)" class="text-red-500 hover:underline">Удалить</button>
        </div>
      </div>
    </div>

    <!-- Модалка создания/редактирования -->
    <CategoryModal
      :show="showCreateModal || !!editCat"
      :isEdit="!!editCat"
      :formData="editCat ? editForm : form"
      :groupOptions="groupOptions"
      :frequencyOptions="frequencyOptions"
      :weekDayOptions="weekDayOptions"
      :quarterMonthOptions="quarterMonthOptions"
      :yearMonthOptions="yearMonthOptions"
      @close="closeModal"
      @submit="editCat ? updateCategory() : createCategory()"
    />

    <!-- Модалка установки лимита -->
    <div v-if="limitCat" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-4">Установить лимит для "{{ limitCat.name }}"</h3>
        <form @submit.prevent="saveLimit" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Сумма лимита в месяц</label>
            <input v-model.number="limitForm.amount" type="number" step="any" min="1" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm font-mono outline-none text-slate-800 dark:text-purple-100" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Срок действия (в месяцах)</label>
            <input v-model.number="limitForm.months" type="number" min="1" max="36" class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none text-slate-800 dark:text-purple-100" />
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="limitCat = null" class="px-4 py-2 text-xs font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition">Отмена</button>
            <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary hover:bg-theme-accent-hover text-white rounded-xl shadow-md transition">Установить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { Plus } from 'lucide-vue-next';
import api from '@/api';
import CategoryModal from '@/components/CategoryModal.vue';

const categories = ref([]);
const limitsMap = ref({});
const showCreateModal = ref(false);
const editCat = ref(null);
const limitCat = ref(null);

const groupLabels = { INCOME: 'Доход', EXPENSE: 'Расход', INVESTMENT: 'Инвестиции' };
const freqLabels = { NONE: 'Разовая', DAILY: 'Ежедневно', WEEKLY: 'Еженедельно', MONTHLY: 'Ежемесячно', QUARTERLY: 'Ежеквартально', ANNUALLY: 'Ежегодно' };
const groupOptions = [{ label: 'Расход', value: 'EXPENSE' }, { label: 'Доход', value: 'INCOME' }, { label: 'Инвестиции', value: 'INVESTMENT' }];
const frequencyOptions = [
  { label: 'Разовая / Без расписания', value: 'NONE' }, { label: 'Ежедневно', value: 'DAILY' },
  { label: 'Еженедельно', value: 'WEEKLY' }, { label: 'Ежемесячно', value: 'MONTHLY' },
  { label: 'Ежеквартально', value: 'QUARTERLY' }, { label: 'Ежегодно', value: 'ANNUALLY' }
];

const weekDayOptions = [
  { label: 'Понедельник', value: 1 }, { label: 'Вторник', value: 2 }, { label: 'Среда', value: 3 },
  { label: 'Четверг', value: 4 }, { label: 'Пятница', value: 5 }, { label: 'Суббота', value: 6 }, { label: 'Воскресенье', value: 7 }
];
const quarterMonthOptions = [{ label: '1-й месяц квартала', value: 1 }, { label: '2-й месяц квартала', value: 2 }, { label: '3-й месяц квартала', value: 3 }];
const yearMonthOptions = [
  { label: 'Январь', value: 1 }, { label: 'Февраль', value: 2 }, { label: 'Март', value: 3 }, { label: 'Апрель', value: 4 },
  { label: 'Май', value: 5 }, { label: 'Июнь', value: 6 }, { label: 'Июль', value: 7 }, { label: 'Август', value: 8 },
  { label: 'Сентябрь', value: 9 }, { label: 'Октябрь', value: 10 }, { label: 'Ноябрь', value: 11 }, { label: 'Декабрь', value: 12 }
];

const form = reactive({ name: '', color: '#8b5cf6', group: 'EXPENSE', frequency: 'NONE', day_of_month: 1, day_of_week: 1, recurrence_month: 1 });
const editForm = reactive({ name: '', color: '#8b5cf6', frequency: 'NONE', day_of_month: 1, day_of_week: 1, recurrence_month: 1 });
const limitForm = reactive({ amount: 10000, months: 12 });

function formatSchedule(cat) {
  if (cat.frequency === 'DAILY') return 'Каждый день';
  if (cat.frequency === 'WEEKLY') {
    const d = weekDayOptions.find(o => o.value === cat.day_of_week);
    return `Еженедельно: ${d ? d.label : 'день ' + cat.day_of_week}`;
  }
  if (cat.frequency === 'MONTHLY') return `День списания: ${cat.day_of_month || 1}-е число`;
  if (cat.frequency === 'QUARTERLY') return `Ежеквартально: ${cat.recurrence_month || 1}-й мес., ${cat.day_of_month || 1}-е число`;
  if (cat.frequency === 'ANNUALLY') {
    const m = yearMonthOptions.find(o => o.value === cat.recurrence_month);
    return `Ежегодно: ${cat.day_of_month || 1} ${m ? m.label : 'мес. ' + cat.recurrence_month}`;
  }
  return 'Без расписания';
}

function closeModal() {
  showCreateModal.value = false;
  editCat.value = null;
}

async function fetchCategories() {
  const { data } = await api.get('/categories');
  categories.value = data;
  const now = new Date();
  for (const c of data) {
    try {
      const { data: lim } = await api.get(`/limits/status/${c.id}?year=${now.getFullYear()}&month=${now.getMonth() + 1}`);
      limitsMap.value[c.id] = lim;
    } catch (e) {}
  }
}

async function createCategory() {
  await api.post('/categories', form);
  closeModal();
  form.name = '';
  await fetchCategories();
}

function openEditModal(c) {
  editCat.value = c;
  editForm.name = c.name;
  editForm.color = c.color || '#8b5cf6';
  editForm.frequency = c.frequency;
  editForm.day_of_month = c.day_of_month || 1;
  editForm.day_of_week = c.day_of_week || 1;
  editForm.recurrence_month = c.recurrence_month || 1;
}

async function updateCategory() {
  await api.put(`/categories/${editCat.value.id}`, editForm);
  closeModal();
  await fetchCategories();
}

function openLimitModal(c) { limitCat.value = c; }

async function saveLimit() {
  await api.post('/limits', { category_id: limitCat.value.id, limit_amount: limitForm.amount, currency: 'RUB', months_duration: limitForm.months });
  limitCat.value = null;
  await fetchCategories();
}

async function deleteCategory(id) {
  if (!confirm('Удалить категорию?')) return;
  await api.delete(`/categories/${id}`);
  await fetchCategories();
}

onMounted(fetchCategories);
</script>
