<template>
  <input
    type="text"
    inputmode="decimal"
    :value="displayValue"
    @input="handleInput"
    :placeholder="placeholder"
    :disabled="disabled"
    :class="inputClass"
  />
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: { type: [Number, String, null], default: null },
  placeholder: { type: String, default: '0' },
  disabled: { type: Boolean, default: false },
  inputClass: { type: String, default: '' }
});

const emit = defineEmits(['update:modelValue']);

function formatWithSpaces(val) {
  if (val === null || val === undefined || val === '') return '';
  const str = String(val).replace(/\s+/g, '').replace(',', '.');
  const parts = str.split('.');
  // Разделяем каждые 3 цифры неразрывным или обычным пробелом
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  return parts.join('.');
}

const displayValue = ref(formatWithSpaces(props.modelValue));

watch(
  () => props.modelValue,
  (newVal) => {
    const rawDisplay = displayValue.value.replace(/\s+/g, '').replace(',', '.');
    if (String(newVal ?? '') !== rawDisplay) {
      displayValue.value = formatWithSpaces(newVal);
    }
  }
);

function handleInput(event) {
  let val = event.target.value;
  // Очищаем от лишних символов кроме цифр и разделителя
  let clean = val.replace(/\s+/g, '').replace(',', '.');
  clean = clean.replace(/[^0-9.]/g, '');

  const parts = clean.split('.');
  if (parts.length > 2) {
    clean = parts[0] + '.' + parts.slice(1).join('');
  }

  const num = clean === '' ? null : parseFloat(clean);
  emit('update:modelValue', num);

  // Обновляем визуальное отображение с пробелами
  const formatted = formatWithSpaces(clean);
  displayValue.value = formatted;
  event.target.value = formatted;
}
</script>