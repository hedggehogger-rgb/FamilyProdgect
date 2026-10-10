<template>
  <div class="bg-theme-light-card dark:bg-theme-dark-card p-6 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm flex flex-col justify-between">
    <div>
      <div class="flex items-center gap-2.5 mb-2">
        <span class="w-3.5 h-3.5 rounded-full shrink-0 shadow-sm" :style="{ backgroundColor: category.color }"></span>
        <h3 class="font-black text-base text-slate-800 dark:text-white truncate" :title="category.name">{{ category.name }}</h3>
      </div>
      <p class="text-xs text-theme-light-muted dark:text-purple-200">{{ scheduleText }}</p>

      <!-- Срок годности -->
      <div v-if="category.expires_at" class="mt-2 text-[11px] font-bold text-amber-600 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/40 px-2.5 py-1 rounded-lg border border-amber-200 dark:border-amber-800/60 inline-flex items-center gap-1.5">
        <span>⏳ До:</span>
        <span class="font-mono">{{ formatDate(category.expires_at) }}</span>
      </div>

      <!-- Сумма по умолчанию -->
      <div v-if="category.default_amount" class="mt-2 text-[11px] font-bold font-mono px-2 py-1 rounded" :class="isExpense ? 'text-rose-500 bg-rose-50 dark:bg-rose-950/40' : 'text-emerald-500 bg-emerald-50 dark:bg-emerald-950/40'">
        План: {{ formatMoney(category.default_amount) }} {{ settings.getSymbol(category.default_currency || 'RUB') }}
      </div>

      <!-- Индикатор лимита -->
      <div v-if="isExpense && limit" @click="$emit('open-history', category)" class="mt-4 p-3 bg-purple-50/50 dark:bg-theme-dark-surface/60 rounded-xl border border-theme-light-border dark:border-theme-dark-border cursor-pointer hover:border-purple-300 transition group">
        <div class="flex justify-between text-xs font-bold mb-1">
          <span class="text-slate-800 dark:text-white">{{ formatMoney(limit.limit_amount) }} {{ settings.getSymbol(limit.currency) }}</span>
          <span :class="limit.is_exceeded ? 'text-red-500' : 'text-purple-600 dark:text-purple-300'">{{ limit.percentage_used }}%</span>
        </div>
        <div class="w-full bg-slate-200 dark:bg-purple-950 h-2 rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all" :class="limit.is_exceeded ? 'bg-red-500' : 'bg-theme-accent-primary'" :style="{ width: Math.min(100, limit.percentage_used) + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- Кнопки управления (только символы) -->
    <div class="flex items-center justify-between pt-4 mt-4 border-t border-theme-light-border dark:border-theme-dark-border">
      <div v-if="isExpense">
        <button
          @click="$emit('open-limit', category)"
          :title="limit ? 'Настроить лимит' : 'Установить лимит'"
          class="p-2 rounded-lg transition"
          :class="limit ? 'text-purple-600 dark:text-purple-300 hover:bg-purple-100 dark:hover:bg-purple-900/40' : 'text-slate-400 hover:text-purple-600 hover:bg-slate-100 dark:hover:bg-theme-dark-hover'"
        >
          <Flag class="w-4 h-4" :class="{ 'fill-current': !!limit }" />
        </button>
      </div>
      <div v-else></div>

      <div class="flex items-center gap-1.5">
        <button
          @click="$emit('edit', category)"
          title="Редактировать"
          class="p-2 text-slate-500 dark:text-purple-200 hover:text-purple-600 dark:hover:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-900/30 rounded-lg transition"
        >
          <Pencil class="w-4 h-4" />
        </button>
        <button
          @click="$emit('delete', category)"
          title="Удалить категорию"
          class="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-lg transition"
        >
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Pencil, Trash2, Flag } from 'lucide-vue-next';
import { useSettingsStore } from '@/stores/settings';
import { formatDate } from '@/utils/formatters';

const props = defineProps({
  category: Object,
  limit: Object,
  isExpense: Boolean,
});

defineEmits(['open-history', 'open-limit', 'edit', 'delete']);

const settings = useSettingsStore();

function formatMoney(val) {
  return (!val || isNaN(val)) ? '0' : Number(val).toLocaleString('ru-RU');
}

const scheduleText = computed(() => {
  const cat = props.category;
  const act = cat.group === 'INCOME' ? 'начисления' : 'списания';
  if (cat.frequency === 'DAILY') return 'Каждый день';
  if (cat.frequency === 'WEEKLY') return `Еженедельно`;
  if (cat.frequency === 'MONTHLY') return `День ${act}: ${cat.day_of_month || 1}-е число`;
  if (cat.frequency === 'QUARTERLY') return `Ежеквартально (${cat.day_of_month || 1} число)`;
  if (cat.frequency === 'ANNUALLY') return `Ежегодно`;
  return 'Без расписания';
});
</script>