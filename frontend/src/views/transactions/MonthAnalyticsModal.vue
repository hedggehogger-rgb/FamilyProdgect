<template>
  <Teleport to="body">
    <div v-if="show" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-2xl p-6 flex flex-col max-h-[88vh]">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-theme-light-border dark:border-theme-dark-border">
          <h3 class="font-black text-lg text-slate-800 dark:text-purple-100">📊 Аналитика: {{ monthName }} {{ year }}</h3>
          <button @click="$emit('close')" class="text-xs font-bold px-2 py-1">Закрыть</button>
        </div>

        <div class="flex-1 overflow-y-auto space-y-6 pr-2">
          <div class="grid grid-cols-3 gap-3">
            <div class="p-4 rounded-xl bg-purple-50 dark:bg-theme-dark-card border border-purple-200 dark:border-purple-900/60 text-center">
              <span class="text-xs text-theme-light-muted font-bold">Доходы</span>
              <p class="text-base font-black text-emerald-500 mt-1 font-mono">+{{ totalIncome }} {{ settings.getSymbol(settings.baseCurrency) }}</p>
            </div>
            <div class="p-4 rounded-xl bg-purple-50 dark:bg-theme-dark-card border border-purple-200 dark:border-purple-900/60 text-center">
              <span class="text-xs text-theme-light-muted font-bold">Расходы</span>
              <p class="text-base font-black text-rose-500 mt-1 font-mono">-{{ totalExpense }} {{ settings.getSymbol(settings.baseCurrency) }}</p>
            </div>
            <div class="p-4 rounded-xl bg-purple-50 dark:bg-theme-dark-card border border-purple-200 dark:border-purple-900/60 text-center">
              <span class="text-xs text-theme-light-muted font-bold">Остаток</span>
              <p class="text-base font-black mt-1 font-mono" :class="savings >= 0 ? 'text-purple-600 dark:text-purple-300' : 'text-rose-500'">
                {{ savings }} {{ settings.getSymbol(settings.baseCurrency) }}
              </p>
            </div>
          </div>

          <div>
            <h4 class="text-xs font-bold uppercase tracking-wider text-theme-light-muted mb-3">Распределение трат по категориям</h4>
            <div v-if="categoryStats.length === 0" class="text-xs text-theme-light-muted italic text-center py-4">В этом месяце расходов не зафиксировано</div>
            <div v-else class="space-y-3">
              <div
                v-for="item in categoryStats"
                :key="item.cat.id"
                @click="$emit('select-category', item.cat)"
                class="p-3 bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl cursor-pointer hover:border-purple-400 transition"
              >
                <div class="flex justify-between items-center text-xs mb-1">
                  <span class="font-bold flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full" :style="{ backgroundColor: item.cat.color }"></span>
                    {{ item.cat.name }}
                  </span>
                  <div class="flex items-center gap-3 font-mono">
                    <span class="font-bold">{{ item.spent }} {{ settings.getSymbol(settings.baseCurrency) }}</span>
                    <span class="text-purple-600 font-black">({{ item.pct }}%)</span>
                  </div>
                </div>
                <div class="w-full bg-slate-100 dark:bg-purple-950 h-2 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all" :style="{ width: item.pct + '%', backgroundColor: item.cat.color }"></div>
                </div>
                <div class="flex justify-between items-center text-[10px] mt-1.5 font-bold">
                  <span v-if="item.limit" :class="item.limit.is_exceeded ? 'text-red-500' : 'text-emerald-600'">
                    {{ item.limit.is_exceeded ? 'Лимит превышен!' : 'Лимит соблюдён' }} (Лимит: {{ item.limit.limit_amount }} {{ settings.getSymbol(item.limit.currency) }})
                  </span>
                  <span v-else class="text-theme-light-muted">Без лимита</span>
                  <span class="text-purple-500 font-normal">Посмотреть операции →</span>
                </div>
              </div>
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
  monthName: String,
  year: Number,
  totalIncome: Number,
  totalExpense: Number,
  savings: Number,
  categoryStats: Array,
});
defineEmits(['close', 'select-category']);
</script>