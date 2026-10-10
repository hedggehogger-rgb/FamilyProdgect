<template>
  <Teleport to="body">
    <div v-if="show" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/60 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-slate-200/70 dark:border-white/[0.08] rounded-3xl shadow-2xl w-full max-w-3xl p-6 sm:p-7 flex flex-col max-h-[90vh]">

        <!-- Заголовок -->
        <div class="flex justify-between items-center mb-5 pb-3 border-b border-theme-light-border dark:border-theme-dark-border">
          <h3 class="font-black text-xl text-slate-800 dark:text-purple-100 flex items-center gap-2">
            <span>📊</span> Аналитика: {{ monthName }} {{ year }}
          </h3>
          <button @click="$emit('close')" class="text-xs font-bold px-3 py-1.5 rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition text-slate-700 dark:text-purple-200">
            Закрыть
          </button>
        </div>

        <div class="flex-1 overflow-y-auto space-y-6 pr-1">
          <!-- Карточки Доходы / Расходы / Остаток -->
          <div class="grid grid-cols-3 gap-3">
            <div class="p-3.5 sm:p-4 rounded-2xl bg-purple-50/60 dark:bg-theme-dark-card border border-purple-200/60 dark:border-white/[0.06] text-center">
              <span class="text-xs text-theme-light-muted font-bold">Доходы</span>
              <p class="text-base sm:text-lg font-black text-emerald-500 mt-1 font-mono">+{{ formatMoney(totalIncome) }} {{ currentSymbol }}</p>
            </div>
            <div class="p-3.5 sm:p-4 rounded-2xl bg-purple-50/60 dark:bg-theme-dark-card border border-purple-200/60 dark:border-white/[0.06] text-center">
              <span class="text-xs text-theme-light-muted font-bold">Расходы</span>
              <p class="text-base sm:text-lg font-black text-rose-500 mt-1 font-mono">-{{ formatMoney(totalExpense) }} {{ currentSymbol }}</p>
            </div>
            <div class="p-3.5 sm:p-4 rounded-2xl bg-purple-50/60 dark:bg-theme-dark-card border border-purple-200/60 dark:border-white/[0.06] text-center">
              <span class="text-xs text-theme-light-muted font-bold">Остаток</span>
              <p class="text-base sm:text-lg font-black mt-1 font-mono" :class="savings >= 0 ? 'text-purple-600 dark:text-purple-300' : 'text-rose-500'">
                {{ formatMoney(savings) }} {{ currentSymbol }}
              </p>
            </div>
          </div>

          <!-- Блок с диаграммой и категориями -->
          <div>
            <h4 class="text-xs font-bold uppercase tracking-wider text-theme-light-muted dark:text-theme-dark-muted mb-4">
              Распределение трат по категориям
            </h4>

            <div v-if="categoryStats.length === 0" class="text-xs text-theme-light-muted italic text-center py-8">
              В этом месяце расходов не зафиксировано
            </div>

            <div v-else class="flex flex-col md:flex-row items-center gap-6 bg-slate-50/70 dark:bg-theme-dark-card/40 p-5 rounded-3xl border border-theme-light-border dark:border-white/[0.06]">

              <!-- Круговая диаграмма со счетчиком в центре -->
              <div class="relative w-52 h-52 sm:w-56 sm:h-56 shrink-0 flex items-center justify-center">
                <svg viewBox="0 0 100 100" class="w-full h-full -rotate-90 transform">
                  <!-- Фоновый круг-подложка -->
                  <circle
                    cx="50"
                    cy="50"
                    :r="RADIUS"
                    class="stroke-slate-200/70 dark:stroke-purple-950/80 fill-none"
                    stroke-width="12"
                  />
                  <!-- Сектора категорий -->
                  <circle
                    v-for="seg in chartSegments"
                    :key="seg.cat.id"
                    cx="50"
                    cy="50"
                    :r="RADIUS"
                    fill="none"
                    :stroke="seg.cat.color"
                    :stroke-width="hoveredCatId === seg.cat.id ? 15 : 12"
                    :stroke-dasharray="seg.dashArray"
                    :stroke-dashoffset="seg.dashOffset"
                    class="transition-all duration-200 cursor-pointer"
                    @mouseenter="hoveredCatId = seg.cat.id"
                    @mouseleave="hoveredCatId = null"
                    @click="$emit('select-category', seg.cat)"
                  />
                </svg>

                <!-- Информационный центр диаграммы -->
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-3 pointer-events-none">
                  <template v-if="activeHoverItem">
                    <span class="text-[11px] font-bold text-theme-light-muted truncate max-w-[130px]" :title="activeHoverItem.cat.name">
                      {{ activeHoverItem.cat.name }}
                    </span>
                    <span class="text-base sm:text-lg font-black font-mono text-slate-900 dark:text-white leading-tight">
                      {{ formatMoney(activeHoverItem.spent) }} {{ currentSymbol }}
                    </span>
                    <span class="text-[11px] font-black text-purple-600 dark:text-purple-300">
                      {{ activeHoverItem.pct }}%
                    </span>
                  </template>
                  <template v-else>
                    <span class="text-[10px] uppercase font-bold text-theme-light-muted">Всего расходов</span>
                    <span class="text-base sm:text-lg font-black font-mono text-slate-900 dark:text-white leading-tight">
                      {{ formatMoney(totalExpense) }} {{ currentSymbol }}
                    </span>
                    <span class="text-[10px] text-theme-light-muted">категорий: {{ categoryStats.length }}</span>
                  </template>
                </div>
              </div>

              <!-- Список категорий (Легенда) -->
              <div class="flex-1 w-full space-y-2 max-h-64 overflow-y-auto pr-1">
                <div
                  v-for="item in categoryStats"
                  :key="item.cat.id"
                  @mouseenter="hoveredCatId = item.cat.id"
                  @mouseleave="hoveredCatId = null"
                  @click="$emit('select-category', item.cat)"
                  class="p-2.5 rounded-2xl border transition-all duration-150 cursor-pointer flex items-center justify-between gap-3"
                  :class="[
                    hoveredCatId === item.cat.id
                      ? 'border-purple-500 bg-purple-50/80 dark:bg-purple-900/40 shadow-sm'
                      : 'border-theme-light-border dark:border-white/[0.06] bg-white dark:bg-theme-dark-card hover:border-purple-300'
                  ]"
                >
                  <div class="flex items-center gap-2.5 min-w-0">
                    <span class="w-3.5 h-3.5 rounded-full shrink-0 shadow-sm" :style="{ backgroundColor: item.cat.color }"></span>
                    <div class="truncate">
                      <p class="text-xs font-bold text-slate-800 dark:text-purple-100 truncate" :title="item.cat.name">
                        {{ item.cat.name }}
                      </p>
                      <p v-if="item.limit" class="text-[10px] font-semibold" :class="item.limit.is_exceeded ? 'text-red-500' : 'text-emerald-500'">
                        {{ item.limit.is_exceeded ? 'Лимит превышен!' : 'В лимите' }}
                      </p>
                    </div>
                  </div>

                  <div class="text-right shrink-0 font-mono">
                    <span class="text-xs font-black text-slate-900 dark:text-white">
                      {{ formatMoney(item.spent) }} {{ currentSymbol }}
                    </span>
                    <span class="ml-1.5 text-xs font-bold text-purple-600 dark:text-purple-300">
                      ({{ item.pct }}%)
                    </span>
                  </div>
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
import { ref, computed } from 'vue';
import { useSettingsStore } from '@/stores/settings';

const settings = useSettingsStore();
const currentSymbol = computed(() => settings.getSymbol(settings.baseCurrency));
const hoveredCatId = ref(null);

const props = defineProps({
  show: Boolean,
  monthName: String,
  year: Number,
  totalIncome: Number,
  totalExpense: Number,
  savings: Number,
  categoryStats: Array,
});

defineEmits(['close', 'select-category']);

function formatMoney(val) {
  if (val === null || val === undefined || isNaN(val)) return '0';
  return Number(val).toLocaleString('ru-RU');
}

const activeHoverItem = computed(() => {
  if (!hoveredCatId.value) return null;
  return props.categoryStats.find(i => i.cat.id === hoveredCatId.value) || null;
});

// Математика круговой диаграммы
const RADIUS = 38;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

const chartSegments = computed(() => {
  const total = props.categoryStats.reduce((sum, item) => sum + Number(item.spent || 0), 0);
  if (total <= 0) return [];

  let accumulatedPercent = 0;
  return props.categoryStats.map(item => {
    const ratio = Number(item.spent || 0) / total;
    const strokeLength = ratio * CIRCUMFERENCE;
    const strokeOffset = -accumulatedPercent * CIRCUMFERENCE;
    accumulatedPercent += ratio;

    return {
      ...item,
      dashArray: `${strokeLength} ${CIRCUMFERENCE}`,
      dashOffset: strokeOffset,
    };
  });
});
</script>