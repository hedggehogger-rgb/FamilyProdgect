<template>
  <div v-if="show" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
    <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6 max-h-[90vh] overflow-y-auto">
      <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-4">
        {{ isEdit ? 'Редактировать категорию' : 'Создать категорию' }}
      </h3>
      <form @submit.prevent="$emit('submit')" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Название</label>
          <input v-model="formData.name" required placeholder="Продукты, Кафе..." class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none text-slate-800 dark:text-purple-100" />
        </div>

        <div>
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Цвет категории</label>
          <div class="flex items-center gap-3">
            <input type="color" v-model="formData.color" class="w-10 h-10 rounded-xl cursor-pointer bg-transparent border-0" />
            <span class="text-xs font-mono font-bold">{{ formData.color }}</span>
          </div>
        </div>

        <div v-if="!isEdit">
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Группа</label>
          <CustomSelect v-model="formData.group" :options="groupOptions" />
        </div>

        <div class="pt-2 border-t border-theme-light-border dark:border-theme-dark-border">
          <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Периодичность операции</label>
          <CustomSelect v-model="formData.frequency" :options="frequencyOptions" />
        </div>

        <!-- Настройки для регулярных платежей -->
        <template v-if="formData.frequency !== 'NONE' && formData.frequency !== 'DAILY'">

          <!-- Дни/Даты -->
          <div v-if="formData.frequency === 'WEEKLY'">
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">День недели</label>
            <CustomSelect v-model="formData.day_of_week" :options="weekDayOptions" />
          </div>
          <div v-else-if="formData.frequency === 'MONTHLY'">
            <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Число месяца (1-30)</label>
            <input v-model.number="formData.day_of_month" type="number" min="1" max="30" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none text-slate-800 dark:text-purple-100" />
          </div>
          <div v-else-if="formData.frequency === 'QUARTERLY'" class="space-y-3">
            <div>
              <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Номер месяца в квартале (1-3)</label>
              <CustomSelect v-model="formData.recurrence_month" :options="quarterMonthOptions" />
            </div>
            <div>
              <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Число месяца (1-31)</label>
              <input v-model.number="formData.day_of_month" type="number" min="1" max="31" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none text-slate-800 dark:text-purple-100" />
            </div>
          </div>
          <div v-else-if="formData.frequency === 'ANNUALLY'" class="space-y-3">
            <div>
              <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Месяц года</label>
              <CustomSelect v-model="formData.recurrence_month" :options="yearMonthOptions" />
            </div>
            <div>
              <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Число месяца (1-31)</label>
              <input v-model.number="formData.day_of_month" type="number" min="1" max="31" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm outline-none text-slate-800 dark:text-purple-100" />
            </div>
          </div>

          <!-- Автоматическая сумма и счет -->
          <div class="pt-3 pb-1 border-t border-theme-light-border dark:border-theme-dark-border mt-3 space-y-3">
            <p class="text-[11px] uppercase tracking-wider font-bold text-purple-600 dark:text-purple-400">Данные для плана/автоплатежа</p>
            <div>
              <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Сумма операции</label>
              <input v-model.number="formData.default_amount" type="number" step="any" min="0.01" required placeholder="Например: 5000" class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border dark:border-theme-dark-border rounded-xl p-2.5 text-sm font-mono font-bold outline-none text-slate-800 dark:text-purple-100" />
            </div>
            <div>
              <label class="block text-xs font-bold text-theme-light-muted dark:text-theme-dark-muted mb-1">Счёт</label>
              <CustomSelect v-model="formData.default_account_id" :options="accountOptions" placeholder="Выберите счёт" />
            </div>
          </div>
        </template>

        <div class="flex justify-end gap-2 pt-2 mt-4">
          <button type="button" @click="$emit('close')" class="px-4 py-2 text-xs font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition">Отмена</button>
          <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary hover:bg-theme-accent-hover text-white rounded-xl shadow-md transition">Сохранить</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import CustomSelect from '@/components/CustomSelect.vue';

defineProps({
  show: Boolean,
  isEdit: Boolean,
  formData: Object,
  groupOptions: Array,
  frequencyOptions: Array,
  weekDayOptions: Array,
  quarterMonthOptions: Array,
  yearMonthOptions: Array,
  accountOptions: Array, // Добавили пропс для счетов
});

defineEmits(['close', 'submit']);
</script>