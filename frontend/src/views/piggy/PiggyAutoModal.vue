<template>
  <Teleport to="body">
    <div v-if="target" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-1">Включить автопополнение</h3>
        <p class="text-xs text-theme-light-muted mb-4">Для копилки "{{ target.name }}"</p>
        <form @submit.prevent="$emit('submit')" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Сумма списания</label>
            <input v-model.number="form.amount" type="number" step="any" min="1" required class="w-full bg-white dark:bg-theme-dark-card border rounded-xl p-2.5 text-sm font-mono font-bold" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Число месяца списания (1-31)</label>
            <input v-model.number="form.day" type="number" min="1" max="31" required class="w-full bg-white dark:bg-theme-dark-card border rounded-xl p-2.5 text-sm font-mono font-bold" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Счёт для списания</label>
            <CustomSelect v-model="form.account_id" :options="accountOptions" />
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="$emit('close')" class="px-4 py-2 text-xs font-bold rounded-xl border hover:bg-slate-100 transition">Отмена</button>
            <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary text-white rounded-xl shadow-md">Сохранить и включить</button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import CustomSelect from '@/components/CustomSelect.vue';

defineProps({
  target: Object,
  form: Object,
  accountOptions: Array,
});
defineEmits(['close', 'submit']);
</script>