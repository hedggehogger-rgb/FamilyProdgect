<template>
  <Teleport to="body">
    <div v-if="show" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-4">Новая копилка</h3>
        <form @submit.prevent="$emit('submit')" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Название цели</label>
            <input v-model="form.name" required placeholder="На отпуск" class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border rounded-xl p-2.5 text-sm outline-none text-slate-800 dark:text-purple-100" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Целевая сумма</label>
            <input v-model.number="form.target_amount" type="number" step="any" min="1" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border rounded-xl p-2.5 text-sm outline-none text-slate-800 font-mono font-bold" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Счёт для списаний (по умолчанию)</label>
            <CustomSelect v-model="form.account_id" :options="accountOptions" />
          </div>
          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Валюта копилки</label>
            <CustomSelect v-model="form.currency" :options="currencyOptions" />
          </div>

          <div class="pt-3 border-t border-theme-light-border">
            <div class="flex items-center gap-2 mb-3">
              <input type="checkbox" v-model="form.is_auto_replenish" id="auto" class="rounded accent-purple-600 w-4 h-4 cursor-pointer" />
              <label for="auto" class="text-xs font-bold text-slate-800 dark:text-purple-200 cursor-pointer">Включить автопополнение</label>
            </div>
            <div v-if="form.is_auto_replenish" class="space-y-3">
              <div>
                <label class="block text-xs font-bold text-theme-light-muted mb-1">Сумма в месяц</label>
                <input v-model.number="form.auto_replenish_amount" type="number" step="any" min="1" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border rounded-xl p-2.5 text-sm font-mono" />
              </div>
              <div>
                <label class="block text-xs font-bold text-theme-light-muted mb-1">Число месяца списания (1-31)</label>
                <input v-model.number="form.auto_replenish_day" type="number" min="1" max="31" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border rounded-xl p-2.5 text-sm" />
              </div>
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="$emit('close')" class="px-4 py-2 text-xs font-bold rounded-xl border hover:bg-slate-100 transition">Отмена</button>
            <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary text-white rounded-xl shadow-md">Создать</button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import CustomSelect from '@/components/CustomSelect.vue';

defineProps({
  show: Boolean,
  form: Object,
  accountOptions: Array,
  currencyOptions: Array,
});
defineEmits(['close', 'submit']);
</script>