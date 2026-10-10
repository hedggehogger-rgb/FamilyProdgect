<template>
  <Teleport to="body">
    <div v-if="category" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <h3 class="text-base font-black text-slate-800 dark:text-white mb-4">Лимит: {{ category.name }}</h3>
        <form @submit.prevent="$emit('save', form.amount)" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted dark:text-purple-200 mb-1">Сумма в месяц ({{ settings.getSymbol('RUB') }})</label>
            <FormattedNumberInput v-model="form.amount" placeholder="10 000" inputClass="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm font-mono font-bold outline-none text-slate-800 dark:text-white" />
          </div>
          <div class="flex items-center justify-between pt-2">
            <button v-if="hasLimit" type="button" @click="$emit('delete')" class="px-3 py-2 text-xs font-bold text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-xl transition">Удалить лимит</button>
            <div class="flex gap-2 ml-auto">
              <button type="button" @click="$emit('close')" class="px-4 py-2 text-xs font-bold rounded-xl border border-theme-light-border hover:bg-slate-100 transition text-slate-700 dark:text-purple-200">Отмена</button>
              <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary hover:bg-theme-accent-hover text-white rounded-xl shadow-md transition">Сохранить</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { reactive, watch } from 'vue';
import FormattedNumberInput from '@/components/FormattedNumberInput.vue';
import { useSettingsStore } from '@/stores/settings';

const props = defineProps({
  category: Object,
  initialAmount: Number,
  hasLimit: Boolean,
});

const emit = defineEmits(['close', 'save', 'delete']);
const settings = useSettingsStore();

const form = reactive({
  amount: props.initialAmount || 10000,
});

watch(() => props.initialAmount, (val) => {
  form.amount = val || 10000;
});
</script>