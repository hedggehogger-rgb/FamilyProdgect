<template>
  <Teleport to="body">
    <div v-if="category" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-[60]">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-lg p-6 flex flex-col max-h-[80vh]">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-theme-light-border dark:border-theme-dark-border">
          <h3 class="font-black text-base text-slate-800 dark:text-purple-100">Операции категории "{{ category.name }}" за {{ monthName }}</h3>
          <button @click="$emit('close')" class="text-xs font-bold px-2 py-1">Закрыть</button>
        </div>
        <div class="flex-1 overflow-y-auto divide-y divide-theme-light-border dark:divide-theme-dark-border">
          <div v-if="transactions.length === 0" class="py-8 text-center text-xs text-theme-light-muted">Операций нет</div>
          <div v-for="t in transactions" :key="t.id" class="py-2.5 flex justify-between items-center text-xs">
            <div>
              <p class="font-bold text-slate-800 dark:text-purple-200">{{ t.note || 'Без описания' }}</p>
              <p class="text-[10px] text-theme-light-muted">{{ formatDate(t.date) }} • {{ t.author === 'HUSBAND' ? 'Любими Муж' : 'КошкоЖена' }}</p>
            </div>
            <span class="font-mono font-bold text-rose-500 text-sm">-{{ t.amount }} {{ settings.getSymbol(t.currency) }}</span>
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
  monthName: String,
  transactions: Array,
});
defineEmits(['close']);
</script>