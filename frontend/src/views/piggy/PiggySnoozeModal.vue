<template>
  <Teleport to="body">
    <div v-if="target" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border rounded-2xl shadow-2xl w-full max-w-sm p-6 space-y-4">
        <h3 class="text-base font-black text-slate-800 dark:text-purple-100">Отсрочить пополнение</h3>
        <p class="text-xs text-theme-light-muted">Плановое пополнение копилки "{{ target.name }}" назначено на {{ target.auto_replenish_day }}-е число.</p>

        <div>
          <label class="block text-xs font-bold text-theme-light-muted mb-1.5">Выбрать новую дату пополнения</label>
          <CustomDatePicker :modelValue="snoozeDate" @update:modelValue="$emit('update:snoozeDate', $event)" placeholder="Выберите дату" />
        </div>

        <div class="flex flex-col gap-2 pt-2">
          <button @click="$emit('confirm-date')" class="w-full py-2.5 text-xs font-bold bg-theme-accent-primary hover:bg-theme-accent-hover text-white rounded-xl shadow-md transition">
            Перенести на выбранную дату
          </button>
          <button @click="$emit('confirm-skip')" class="w-full py-2.5 text-xs font-bold bg-amber-500 hover:bg-amber-600 text-white rounded-xl shadow-md transition">
            Пропустить пополнение в этом месяце
          </button>
          <button @click="$emit('close')" class="w-full py-2 text-xs font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition">
            Отмена
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import CustomDatePicker from '@/components/CustomDatePicker.vue';

defineProps({
  target: Object,
  snoozeDate: String,
});
defineEmits(['close', 'confirm-date', 'confirm-skip', 'update:snoozeDate']);
</script>