<template>
  <div class="relative w-full select-none" ref="rootRef">
    <button
      type="button"
      @click="toggle"
      :disabled="disabled"
      class="w-full flex items-center justify-between gap-2 rounded-xl border font-semibold transition text-left outline-none"
      :class="[
        size === 'sm' ? 'px-2.5 py-1.5 text-xs' : 'px-3.5 py-2.5 text-sm',
        isOpen
          ? 'border-purple-500 ring-2 ring-purple-500/20'
          : 'border-theme-light-border dark:border-theme-dark-border',
        'bg-white dark:bg-theme-dark-card text-theme-light-text dark:text-theme-dark-text hover:border-purple-400 dark:hover:border-purple-500 disabled:opacity-50 disabled:cursor-not-allowed'
      ]"
    >
      <span class="truncate">
        {{ selectedLabel || placeholder }}
      </span>
      <ChevronDown
        class="shrink-0 text-purple-500 transition-transform duration-200"
        :class="[size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4', { 'rotate-180': isOpen }]"
      />
    </button>

    <!-- Стилизованное выпадающее меню со сглаженными рамками, без белых рамок и синего системного фона -->
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
        class="absolute z-50 mt-1.5 w-full min-w-full max-h-60 overflow-y-auto rounded-xl border border-purple-200 dark:border-purple-900/60 bg-white dark:bg-theme-dark-surface p-1.5 shadow-2xl shadow-purple-950/20 backdrop-blur-md"
      >
        <button
          v-for="opt in options"
          :key="String(opt.value)"
          type="button"
          @click="selectOption(opt.value)"
          class="w-full flex items-center justify-between px-3 py-2 text-xs font-semibold rounded-lg text-left transition-colors duration-150 cursor-pointer"
          :class="[
            modelValue === opt.value
              ? 'bg-purple-100 dark:bg-purple-900/70 text-purple-700 dark:text-purple-200 font-bold'
              : 'text-slate-700 dark:text-purple-100 hover:bg-slate-100 dark:hover:bg-theme-dark-hover'
          ]"
        >
          <span class="truncate">{{ opt.label }}</span>
          <Check v-if="modelValue === opt.value" class="w-3.5 h-3.5 text-purple-600 dark:text-purple-300 shrink-0 ml-1.5" />
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { ChevronDown, Check } from 'lucide-vue-next';

const props = defineProps({
  modelValue: { type: [String, Number, Boolean, null], default: null },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Выберите...' },
  disabled: { type: Boolean, default: false },
  size: { type: String, default: 'md' }
});

const emit = defineEmits(['update:modelValue', 'change']);

const isOpen = ref(false);
const rootRef = ref(null);

const selectedLabel = computed(() => {
  const item = props.options.find((o) => o.value === props.modelValue);
  return item ? item.label : '';
});

function toggle() {
  if (!props.disabled) {
    isOpen.value = !isOpen.value;
  }
}

function selectOption(val) {
  emit('update:modelValue', val);
  emit('change', val);
  isOpen.value = false;
}

function handleClickOutside(e) {
  if (rootRef.value && !rootRef.value.contains(e.target)) {
    isOpen.value = false;
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside));
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside));
</script>