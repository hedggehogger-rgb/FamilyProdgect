<template>
  <Teleport to="body">
    <div v-if="show" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-xl p-6 flex flex-col max-h-[85vh]">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-black text-lg text-slate-800 dark:text-purple-100">План расходов: {{ monthName }} {{ year }}</h3>
          <button @click="$emit('close')" class="text-xs font-bold px-2 py-1">Закрыть</button>
        </div>
        <div v-if="loading" class="flex-1 flex justify-center items-center py-10">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
        <div v-else class="flex-1 overflow-y-auto space-y-3 pr-2">
          <div v-for="cat in categories" :key="cat.id" class="p-3.5 bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl flex justify-between items-center">
            <div>
              <p class="font-bold text-sm text-slate-800 dark:text-purple-200">{{ cat.name }}</p>
              <p class="text-[11px] text-theme-light-muted">Средний расход: {{ forecasts[cat.id]?.average_monthly_expense || 0 }} {{ settings.getSymbol(settings.baseCurrency) }}</p>
              <p class="text-[11px] text-purple-600 font-semibold">Уже потрачено: {{ getSpentForCat(cat.id) }} {{ settings.getSymbol(settings.baseCurrency) }}</p>
            </div>
            <div class="text-right">
              <span class="text-xs block text-theme-light-muted">Ожидание</span>
              <span class="text-sm font-black font-mono text-rose-500 bg-rose-50 dark:bg-rose-950/40 px-2 py-1 rounded-lg">
                {{ cat.default_amount || forecasts[cat.id]?.predicted_next_month || '0.00' }} {{ settings.getSymbol(settings.baseCurrency) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useSettingsStore } from '@/stores/settings';

const settings = useSettingsStore();

defineProps({
  show: Boolean,
  loading: Boolean,
  categories: Array,
  forecasts: Object,
  monthName: String,
  year: Number,
  getSpentForCat: Function,
});
defineEmits(['close']);
</script>