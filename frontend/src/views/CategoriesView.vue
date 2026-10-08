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

          <p v-if="cat.day_of_month" class="text-xs text-theme-light-muted dark:text-theme-dark-muted mt-2">
            День списания: {{ cat.day_of_month }}-е число
          </p>

          <!-- Блок лимита -->
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
          <div class="flex gap-2">
            <button @click="openLimitModal(cat)" class="text-purple-600 dark:text-purple-400 hover:underline">
              Лимит
            </button>
            <button @click="openEditModal(cat)" class="text-slate-600 dark:text-purple-300 hover:underline">
              Изменить
            </button>
          </div>
          <button @click="deleteCategory(cat.id)" class="text-red-500 hover:underline">
            Удалить
          </button>
        </div>
      </div>
    </div>

    <!-- Модалка создания категории -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-4">Создать категорию</h3>
        <form @submit.prevent="createCategory" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">Название</label>
            <input v-model="form.name" required placeholder="Продукты, Кафе..." class="mt-1 w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none" />
          </div>

          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">Цвет категории</label>
            <div class="flex items-center gap-3 mt-1">
              <input type="color" v-model="form.color" class="w-10 h-10 rounded-xl cursor-pointer bg-transparent border-0" />
              <span class="text-xs font-mono font-bold">{{ form.color }}</span>
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">Группа</label>
            <select v-model="form.group" class="mt-1 w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm font-semibold outline-none">
              <option value="EXPENSE">Расход</option>
              <option value="INCOME">Доход</option>
              <option value="INVESTMENT">Инвестиции</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">Периодичность</label>
            <select v-model="form.frequency" class="mt-1 w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm font-semibold outline-none">
              <option value="NONE">Разовая / Без расписания</option>
              <option value="DAILY">Ежедневно</option>
              <option value="WEEKLY">Еженедельно</option>
              <option value="MONTHLY">Ежемесячно</option>
              <option value="QUARTERLY">Ежеквартально</option>
              <option value="ANNUALLY">Ежегодно</option>
            </select>
          </div>

          <div v-if="form.frequency === 'MONTHLY'">
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">Число месяца списания (1-31)</label>
            <input v-model.number="form.day_of_month" type="number" min="1" max="31" class="mt-1 w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none" />
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="showCreateModal = false" class="px-4 py-2 text-xs font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border">Отмена</button>
            <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary text-white rounded-xl shadow-md">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модалка редактирования категории -->
    <div v-if="editCat" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-4">Редактировать категорию</h3>
        <form @submit.prevent="updateCategory" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">Название</label>
            <input v-model="editForm.name" required class="mt-1 w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">Цвет</label>
            <div class="flex items-center gap-3 mt-1">
              <input type="color" v-model="editForm.color" class="w-10 h-10 rounded-xl cursor-pointer bg-transparent border-0" />
              <span class="text-xs font-mono font-bold">{{ editForm.color }}</span>
            </div>
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">День списания</label>
            <input v-model.number="editForm.day_of_month" type="number" min="1" max="31" class="mt-1 w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none" />
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="editCat = null" class="px-4 py-2 text-xs font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border">Отмена</button>
            <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary text-white rounded-xl shadow-md">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модалка установки лимита -->
    <div v-if="limitCat" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-4">Установить лимит для "{{ limitCat.name }}"</h3>
        <form @submit.prevent="saveLimit" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">Сумма лимита в месяц</label>
            <input v-model.number="limitForm.amount" type="number" min="1" required class="mt-1 w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm font-mono outline-none" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted">Срок действия (в месяцах)</label>
            <input v-model.number="limitForm.months" type="number" min="1" max="36" class="mt-1 w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none" />
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="limitCat = null" class="px-4 py-2 text-xs font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border">Отмена</button>
            <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary text-white rounded-xl shadow-md">Установить</button>
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

const categories = ref([]);
const limitsMap = ref({});
const showCreateModal = ref(false);
const editCat = ref(null);
const limitCat = ref(null);

const groupLabels = {
  INCOME: 'Доход',
  EXPENSE: 'Расход',
  INVESTMENT: 'Инвестиции'
};

const freqLabels = {
  NONE: 'Разовая',
  DAILY: 'Ежедневно',
  WEEKLY: 'Еженедельно',
  MONTHLY: 'Ежемесячно',
  QUARTERLY: 'Ежеквартально',
  ANNUALLY: 'Ежегодно'
};

const form = reactive({
  name: '',
  color: '#8b5cf6',
  group: 'EXPENSE',
  frequency: 'NONE',
  day_of_month: null
});

const editForm = reactive({
  name: '',
  color: '#8b5cf6',
  day_of_month: null
});

const limitForm = reactive({
  amount: 10000,
  months: 12
});

async function fetchCategories() {
  const { data } = await api.get('/categories');
  categories.value = data;

  const now = new Date();
  for (const c of data) {
    try {
      const { data: lim } = await api.get(`/limits/status/${c.id}?year=${now.getFullYear()}&month=${now.getMonth() + 1}`);
      limitsMap.value[c.id] = lim;
    } catch (e) {
      // лимит не установлен
    }
  }
}

async function createCategory() {
  await api.post('/categories', form);
  showCreateModal.value = false;
  form.name = '';
  await fetchCategories();
}

function openEditModal(c) {
  editCat.value = c;
  editForm.name = c.name;
  editForm.color = c.color || '#8b5cf6';
  editForm.day_of_month = c.day_of_month;
}

async function updateCategory() {
  await api.put(`/categories/${editCat.value.id}`, editForm);
  editCat.value = null;
  await fetchCategories();
}

function openLimitModal(c) {
  limitCat.value = c;
}

async function saveLimit() {
  await api.post('/limits', {
    category_id: limitCat.value.id,
    limit_amount: limitForm.amount,
    currency: 'RUB',
    months_duration: limitForm.months
  });
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