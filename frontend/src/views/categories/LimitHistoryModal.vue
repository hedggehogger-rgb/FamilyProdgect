<template>
  <Teleport to="body">
    <div v-if="category" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border rounded-2xl shadow-2xl w-full max-w-lg p-6 max-h-[80vh] flex flex-col">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-theme-light-border">
          <h3 class="font-black text-base text-slate-800 dark:text-white">Расходы: {{ category.name }}</h3>
          <button @click="$emit('close')" class="text-xs font-bold px-2 py-1 hover:bg-purple-100 dark:hover:bg-theme-dark-hover rounded text-slate-700 dark:text-purple-200">Закрыть</button>
        </div>
        <div class="flex-1 overflow-y-auto">
          <div v-if="loading" class="py-10 text-center"><div class="animate-spin inline-block w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full"></div></div>
          <div v-else-if="transactions.length === 0" class="py-8 text-center text-xs text-theme-light-muted dark:text-purple-200">В этом месяце расходов не было</div>
          <div v-else class="divide-y divide-theme-light-border dark:divide-theme-dark-border">
            <div v-for="t in transactions" :key="t.id" class="py-2.5 flex justify-between items-center">
              <div>
                <p class="text-sm font-bold text-slate-800 dark:text-white">{{ t.note || 'Без описания' }}</p>
                <p class="text-[10px] text-theme-light-muted dark:text-purple-300">{{ formatDate(t.date) }}</p>
              </div>
              <span class="text-sm font-black font-mono text-rose-500">-{{ formatMoney(t.amount) }} {{ settings.getSymbol(t.currency) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useSettingsStore } from '@/stores/settings';
import { formatDate } from '@/utils/formatters';

const settings = useSettingsStore();

defineProps({
  category: Object,
  transactions: Array,
  loading: Boolean,
});

defineEmits(['close']);

function formatMoney(val) {
  return (!val || isNaN(val)) ? '0' : Number(val).toLocaleString('ru-RU');
}
</script>