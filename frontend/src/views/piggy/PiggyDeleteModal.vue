<template>
  <Teleport to="body">
    <div v-if="target" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-2">Разбить копилку?</h3>
        <p class="text-sm text-theme-light-muted mb-4">Накопленные {{ target.current_amount }} будут зачислены на выбранный счёт.</p>
        <form @submit.prevent="$emit('confirm')">
          <div v-if="target.current_amount > 0" class="mb-4 text-left">
            <label class="block text-xs font-bold text-theme-light-muted mb-1">Куда зачислить деньги?</label>
            <CustomSelect :modelValue="targetAccountId" @update:modelValue="$emit('update:targetAccountId', $event)" :options="accountOptions" required />
          </div>
          <div class="flex justify-center gap-3">
            <button type="button" @click="$emit('close')" class="px-5 py-2.5 text-sm font-bold rounded-xl border hover:bg-slate-100 transition">Отмена</button>
            <button type="submit" class="px-5 py-2.5 text-sm font-bold bg-red-500 hover:bg-red-600 text-white rounded-xl shadow-md">Разбить</button>
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
  targetAccountId: String,
  accountOptions: Array,
});
defineEmits(['close', 'confirm', 'update:targetAccountId']);
</script>