<template>
  <div class="relative w-full select-none" ref="pickerRef">
    <!-- Поле ввода с датой -->
    <button
      type="button"
      @click="toggleOpen"
      class="w-full flex items-center justify-between gap-2 px-3.5 py-2.5 rounded-xl border font-semibold text-sm transition outline-none"
      :class="[
        isOpen
          ? 'border-purple-500 ring-2 ring-purple-500/20'
          : 'border-theme-light-border dark:border-theme-dark-border',
        'bg-white dark:bg-theme-dark-card text-theme-light-text dark:text-theme-dark-text hover:border-purple-400 dark:hover:border-purple-500'
      ]"
    >
      <span :class="formattedDisplayDate ? 'font-mono font-bold' : 'text-theme-light-muted'">
        {{ formattedDisplayDate || placeholder }}
      </span>
      <Calendar class="w-4 h-4 text-purple-600 dark:text-purple-400 shrink-0" />
    </button>

    <!-- Выпадающее меню календаря -->
    <transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 mt-1.5 w-72 rounded-2xl border border-purple-200 dark:border-purple-900/60 bg-white dark:bg-theme-dark-surface p-4 shadow-2xl shadow-purple-950/20 backdrop-blur-md"
      >
        <!-- Навигация: Месяц и Год -->
        <div class="flex items-center justify-between mb-3 pb-2 border-b border-theme-light-border dark:border-theme-dark-border">
          <button
            type="button"
            @click="prevMonth"
            class="p-1 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/50 text-purple-600 dark:text-purple-400 transition"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>
          <span class="text-xs font-black text-slate-800 dark:text-purple-100">
            {{ monthNames[viewMonth] }} {{ viewYear }}
          </span>
          <button
            type="button"
            @click="nextMonth"
            class="p-1 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/50 text-purple-600 dark:text-purple-400 transition"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>

        <!-- Дни недели -->
        <div class="grid grid-cols-7 gap-1 text-center mb-1">
          <span
            v-for="day in weekDays"
            :key="day"
            class="text-[10px] font-bold text-theme-light-muted dark:text-theme-dark-muted uppercase"
          >
            {{ day }}
          </span>
        </div>

        <!-- Сетка чисел -->
        <div class="grid grid-cols-7 gap-1">
          <button
            v-for="(cell, idx) in daysGrid"
            :key="idx"
            type="button"
            :disabled="!cell.isCurrentMonth"
            @click="selectDate(cell)"
            class="h-8 w-8 text-xs font-semibold rounded-lg flex items-center justify-center transition-all duration-150"
            :class="[
              !cell.isCurrentMonth
                ? 'opacity-20 cursor-default'
                : cell.isSelected
                  ? 'bg-theme-accent-primary text-white font-bold shadow-md shadow-purple-500/30'
                  : cell.isToday
                    ? 'border border-purple-500 text-purple-600 dark:text-purple-300 font-bold hover:bg-purple-50 dark:hover:bg-purple-900/30'
                    : 'text-slate-700 dark:text-purple-200 hover:bg-purple-100 dark:hover:bg-theme-dark-hover cursor-pointer'
            ]"
          >
            {{ cell.dayNumber }}
          </button>
        </div>

        <!-- Кнопка "Сегодня" -->
        <div class="mt-3 pt-2 border-t border-theme-light-border dark:border-theme-dark-border flex justify-between">
          <button
            type="button"
            @click="setToday"
            class="text-[11px] font-bold text-purple-600 dark:text-purple-400 hover:underline"
          >
            Сегодня
          </button>
          <button
            type="button"
            @click="isOpen = false"
            class="text-[11px] font-bold text-theme-light-muted hover:underline"
          >
            Закрыть
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { Calendar, ChevronLeft, ChevronRight } from 'lucide-vue-next';

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Выберите дату' }
});

const emit = defineEmits(['update:modelValue', 'change']);

const isOpen = ref(false);
const pickerRef = ref(null);

const monthNames = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];
const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

const today = new Date();
const viewYear = ref(today.getFullYear());
const viewMonth = ref(today.getMonth());

function syncWithModelValue() {
  if (props.modelValue) {
    const parts = props.modelValue.split('-');
    if (parts.length === 3) {
      viewYear.value = parseInt(parts[0], 10);
      viewMonth.value = parseInt(parts[1], 10) - 1;
    }
  }
}

watch(() => props.modelValue, syncWithModelValue, { immediate: true });

const formattedDisplayDate = computed(() => {
  if (!props.modelValue) return '';
  const parts = props.modelValue.split('-');
  if (parts.length !== 3) return props.modelValue;
  return `${parts[2]}.${parts[1]}.${parts[0]}`;
});

const daysGrid = computed(() => {
  const year = viewYear.value;
  const month = viewMonth.value;

  const firstDayOfWeek = (new Date(year, month, 1).getDay() + 6) % 7;
  const daysInCurrentMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();

  const cells = [];

  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    cells.push({
      dayNumber: daysInPrevMonth - i,
      isCurrentMonth: false,
      dateString: ''
    });
  }

  for (let d = 1; d <= daysInCurrentMonth; d++) {
    const mStr = String(month + 1).padStart(2, '0');
    const dStr = String(d).padStart(2, '0');
    const dateString = `${year}-${mStr}-${dStr}`;

    const isToday =
      today.getFullYear() === year &&
      today.getMonth() === month &&
      today.getDate() === d;

    const isSelected = props.modelValue === dateString;

    cells.push({
      dayNumber: d,
      isCurrentMonth: true,
      dateString,
      isToday,
      isSelected
    });
  }

  const remaining = 42 - cells.length;
  for (let d = 1; d <= remaining; d++) {
    cells.push({
      dayNumber: d,
      isCurrentMonth: false,
      dateString: ''
    });
  }

  return cells;
});

function toggleOpen() {
  isOpen.value = !isOpen.value;
}

function prevMonth() {
  if (viewMonth.value === 0) {
    viewMonth.value = 11;
    viewYear.value--;
  } else {
    viewMonth.value--;
  }
}

function nextMonth() {
  if (viewMonth.value === 11) {
    viewMonth.value = 0;
    viewYear.value++;
  } else {
    viewMonth.value++;
  }
}

function selectDate(cell) {
  if (!cell.isCurrentMonth) return;
  emit('update:modelValue', cell.dateString);
  emit('change', cell.dateString);
  isOpen.value = false;
}

function setToday() {
  const y = today.getFullYear();
  const m = String(today.getMonth() + 1).padStart(2, '0');
  const d = String(today.getDate()).padStart(2, '0');
  const todayStr = `${y}-${m}-${d}`;
  viewYear.value = today.getFullYear();
  viewMonth.value = today.getMonth();
  emit('update:modelValue', todayStr);
  emit('change', todayStr);
  isOpen.value = false;
}

function handleClickOutside(e) {
  if (pickerRef.value && !pickerRef.value.contains(e.target)) {
    isOpen.value = false;
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside));
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside));
</script>