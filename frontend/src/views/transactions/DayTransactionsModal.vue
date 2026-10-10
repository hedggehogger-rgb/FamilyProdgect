<template>
  <Teleport to="body">
    <div v-if="day" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-lg p-6 flex flex-col max-h-[85vh]">
        <!-- Шапка: день и крестик -->
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-theme-light-border dark:border-theme-dark-border">
          <h3 class="font-black text-lg text-slate-900 dark:text-white capitalize">
            {{ day }} {{ monthName }}
          </h3>
          <button
            @click="$emit('close')"
            title="Закрыть"
            class="p-1 rounded-lg text-black dark:text-white hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition"
          >
            <X class="w-5 h-5 stroke-[2.5]" />
          </button>
        </div>

        <!-- Список операций -->
        <div
          class="flex-1 overflow-y-auto divide-y divide-theme-light-border dark:divide-theme-dark-border"
          @scroll="hideTooltip"
        >
          <div v-if="transactions.length === 0" class="py-8 text-center text-xs text-theme-light-muted">
            В этот день операций нет
          </div>

          <div
            v-for="t in transactions"
            :key="t.id"
            class="py-3 px-1 flex items-center justify-between gap-3 text-sm hover:bg-slate-50/60 dark:hover:bg-theme-dark-card/40 rounded-xl transition-colors"
            :class="{'opacity-75 bg-purple-50/40 dark:bg-purple-950/20': t.isPlanned || t.is_executed === false}"
          >
            <!-- 1. Сумма слева (зелёный / красный) -->
            <div class="min-w-[115px] shrink-0 text-left">
              <span
                class="font-mono font-black text-sm whitespace-nowrap"
                :class="isIncomeType(t.type) ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'"
              >
                {{ isIncomeType(t.type) ? '+' : '-' }}{{ formatMoney(t.amount) }} {{ settings.getSymbol(t.currency) }}
              </span>
            </div>

            <!-- 2. Категория или 'Без категории' с тултипом -->
            <div class="flex-1 min-w-0 text-left">
              <span v-if="getCategoryTitle(t)" class="text-xs font-bold text-slate-800 dark:text-white truncate block" :title="t.note || ''">
                {{ getCategoryTitle(t) }}
              </span>

              <div
                v-else
                @mouseenter="showTooltip($event, t.note || 'Комментарий отсутствует')"
                @mouseleave="hideTooltip"
                class="inline-flex items-center cursor-help"
              >
                <span class="text-xs font-semibold text-theme-light-muted dark:text-purple-300 border-b border-dashed border-theme-light-muted/60 dark:border-purple-300/60">
                  Без категории
                </span>
              </div>
            </div>

            <!-- 3. Название счёта -->
            <div class="w-24 text-left truncate shrink-0">
              <span class="text-xs font-semibold text-slate-600 dark:text-purple-200" :title="getAccountTitle(t)">
                {{ getAccountTitle(t) }}
              </span>
            </div>

            <!-- 4. Мусорка максимально справа -->
            <div class="shrink-0 flex items-center justify-end w-8">
              <button
                v-if="!t.isPlanned"
                @click="$emit('ask-delete', t.id)"
                title="Удалить операцию"
                class="p-1.5 text-rose-500 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg transition"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Глобальное всплывающее окошко поверх всего интерфейса -->
      <div
        v-if="activeTooltip"
        class="fixed z-[100] pointer-events-none min-w-44 max-w-xs bg-slate-900/95 dark:bg-purple-950/95 text-white text-xs font-medium p-3 rounded-2xl shadow-2xl border border-slate-700/80 dark:border-purple-700/80 backdrop-blur-md transition-opacity duration-150"
        :class="activeTooltip.isNearTop ? 'translate-y-0' : '-translate-y-full'"
        :style="{ top: `${activeTooltip.top}px`, left: `${activeTooltip.left}px` }"
      >
        <span class="text-[10px] font-bold uppercase tracking-wider text-purple-300 block mb-1">Комментарий:</span>
        <span class="break-words leading-snug block text-slate-100">{{ activeTooltip.text }}</span>
        <!-- Стрелочка -->
        <div
          class="absolute left-5 w-0 h-0 border-x-4 border-x-transparent"
          :class="activeTooltip.isNearTop
            ? 'bottom-full border-b-4 border-b-slate-900/95 dark:border-b-purple-950/95'
            : 'top-full border-t-4 border-t-slate-900/95 dark:border-t-purple-950/95'"
        ></div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue';
import { X, Trash2 } from 'lucide-vue-next';
import { useSettingsStore } from '@/stores/settings';

const settings = useSettingsStore();

const props = defineProps({
  day: Number,
  monthName: String,
  transactions: Array,
  categories: { type: Array, default: () => [] },
  accounts: { type: Array, default: () => [] },
});

defineEmits(['close', 'ask-delete']);

const activeTooltip = ref(null);

function showTooltip(e, text) {
  const rect = e.currentTarget.getBoundingClientRect();
  const isNearTop = rect.top < 130;
  activeTooltip.value = {
    text,
    isNearTop,
    top: isNearTop ? rect.bottom + 8 : rect.top - 8,
    left: Math.max(16, rect.left - 8),
  };
}

function hideTooltip() {
  activeTooltip.value = null;
}

function isIncomeType(type) {
  return String(type).startsWith('INCOME');
}

function formatMoney(val) {
  return (!val || isNaN(val)) ? '0' : Number(val).toLocaleString('ru-RU');
}

function getCategoryTitle(t) {
  if (!t.category_id) return null;
  const cat = props.categories.find(c => c.id === t.category_id);
  return cat ? cat.name : null;
}

function getAccountTitle(t) {
  if (!t.account_id) return '—';
  const acc = props.accounts.find(a => a.id === t.account_id);
  return acc ? acc.name : '—';
}
</script>