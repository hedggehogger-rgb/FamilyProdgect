<template>
  <Teleport to="body">
    <div v-if="day" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-lg p-6 flex flex-col max-h-[85vh]">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-theme-light-border dark:border-theme-dark-border">
          <h3 class="font-black text-base text-slate-800 dark:text-purple-100">Операции за {{ day }} {{ monthName }}</h3>
          <button @click="$emit('close')" class="text-xs font-bold px-2 py-1 rounded hover:bg-purple-100 dark:hover:bg-theme-dark-hover">Закрыть</button>
        </div>
        <div class="flex-1 overflow-y-auto divide-y divide-theme-light-border dark:divide-theme-dark-border">
          <div v-if="transactions.length === 0" class="py-8 text-center text-xs text-theme-light-muted">В этот день операций нет</div>
          <div v-for="t in transactions" :key="t.id" class="py-3 flex justify-between items-center text-sm" :class="{'opacity-75 bg-purple-50/50 dark:bg-purple-950/20 px-2 rounded-xl': t.isPlanned || t.is_executed === false}">
            <div>
              <p class="font-bold text-slate-800 dark:text-purple-200">
                <span v-if="t.is_executed === false" class="text-[10px] bg-purple-600 text-white px-1.5 py-0.5 rounded font-black mr-1 shadow-sm">ОТЛОЖЕН</span>
                <span v-else-if="t.isPlanned" class="text-[10px] bg-purple-200 dark:bg-purple-900 text-purple-800 dark:text-purple-200 px-1.5 py-0.5 rounded font-black mr-1">ПЛАН</span>
                {{ translateType(t.type) }}
              </p>
              <p class="text-xs text-theme-light-muted">{{ t.note || 'Без описания' }} <span v-if="!t.isPlanned">• {{ t.author === 'HUSBAND' ? 'Любими Муж' : 'КошкоЖена' }}</span></p>
            </div>
            <div class="text-right">
              <p class="font-mono font-bold" :class="isIncomeType(t.type) ? 'text-emerald-500' : 'text-rose-500'">
                {{ isIncomeType(t.type) ? '+' : '-' }}{{ t.amount }} {{ settings.getSymbol(t.currency) }}
              </p>
              <button v-if="!t.isPlanned" @click="$emit('ask-delete', t.id)" class="text-[11px] text-red-500 hover:underline">Удалить</button>
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
  day: Number,
  monthName: String,
  transactions: Array,
});
defineEmits(['close', 'ask-delete']);

function isIncomeType(type) { return type.startsWith('INCOME'); }
function translateType(type) {
  const map = {
    EXPENSE_PLANNED: 'Плановый расход',
    EXPENSE_IMPULSE: 'Внеплановый расход',
    INCOME_PLANNED: 'Плановый доход',
    INCOME_UNPLANNED: 'Внеплановый доход',
    INCOME: 'Доход',
    INVESTMENT: 'Инвестиции',
    TRANSFER: 'Перевод'
  };
  return map[type] || type;
}
</script>