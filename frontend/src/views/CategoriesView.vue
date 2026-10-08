<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-lg font-bold text-slate-800">Категории и лимиты</h2>
      <button @click="showModal = true" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-4 py-2 rounded-lg font-medium transition shadow-sm">
        + Новая категория
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div v-for="cat in categories" :key="cat.id" class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex justify-between items-start mb-2">
            <span class="text-xs font-semibold px-2 py-0.5 rounded font-mono" :class="groupBadge(cat.group)">
              {{ cat.group }}
            </span>
            <span class="text-xs text-slate-400 font-mono">{{ cat.frequency }}</span>
          </div>
          <h3 class="font-bold text-slate-800 text-base">{{ cat.name }}</h3>
          <p v-if="cat.day_of_month" class="text-xs text-slate-500 mt-1">День списания: {{ cat.day_of_month }}-е число</p>
        </div>
        <button @click="deleteCategory(cat.id)" class="text-rose-500 hover:text-rose-700 text-xs self-end mt-4">
          Удалить
        </button>
      </div>
    </div>

    <!-- Модалка добавления категории -->
    <div v-if="showModal" class="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6">
        <h3 class="text-base font-bold text-slate-800 mb-4">Создать категорию</h3>
        <form @submit.prevent="createCategory" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-slate-600">Название</label>
            <input v-model="form.name" required placeholder="Продукты" class="mt-1 w-full border rounded-lg p-2 text-sm" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-600">Группа</label>
            <select v-model="form.group" class="mt-1 w-full border rounded-lg p-2 text-sm">
              <option value="EXPENSE">Расход (EXPENSE)</option>
              <option value="INCOME">Доход (INCOME)</option>
              <option value="INVESTMENT">Инвестиции (INVESTMENT)</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-600">Регулярность</label>
            <select v-model="form.frequency" class="mt-1 w-full border rounded-lg p-2 text-sm">
              <option value="NONE">Разовая / Без расписания</option>
              <option value="MONTHLY">Ежемесячно</option>
              <option value="WEEKLY">Еженедельно</option>
            </select>
          </div>
          <div v-if="form.frequency === 'MONTHLY'">
            <label class="block text-xs font-medium text-slate-600">Число месяца (1-31)</label>
            <input v-model.number="form.day_of_month" type="number" min="1" max="31" class="mt-1 w-full border rounded-lg p-2 text-sm" />
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="showModal = false" class="px-4 py-2 text-xs border rounded-lg">Отмена</button>
            <button type="submit" class="px-4 py-2 text-xs bg-indigo-600 text-white rounded-lg">Сохранить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '@/api';

const categories = ref([]);
const showModal = ref(false);

const form = reactive({
  name: '',
  group: 'EXPENSE',
  periodicity: 'INFINITE',
  months_duration: 0,
  frequency: 'NONE',
  day_of_month: null
});

function groupBadge(group) {
  if (group === 'INCOME') return 'bg-emerald-100 text-emerald-800';
  if (group === 'INVESTMENT') return 'bg-amber-100 text-amber-800';
  return 'bg-rose-100 text-rose-800';
}

async function fetchCategories() {
  const { data } = await api.get('/categories');
  categories.value = data;
}

async function createCategory() {
  await api.post('/categories', form);
  showModal.value = false;
  form.name = '';
  await fetchCategories();
}

async function deleteCategory(id) {
  if (!confirm('Удалить категорию?')) return;
  await api.delete(`/categories/${id}`);
  await fetchCategories();
}

onMounted(fetchCategories);
</script>