<template>
  <Teleport to="body">
    <div v-if="category" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border rounded-2xl shadow-2xl w-full max-w-sm p-6 text-center">
        <h3 class="text-lg font-black text-slate-800 dark:text-white mb-2">Удалить категорию?</h3>
        <p class="text-sm text-theme-light-muted dark:text-purple-200 mb-6">Связанные операции останутся без категории.</p>
        <div class="flex justify-center gap-3">
          <button @click="$emit('close')" class="px-5 py-2.5 text-sm font-bold rounded-xl border border-theme-light-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition text-slate-700 dark:text-purple-200">Отмена</button>
          <button @click="$emit('confirm')" class="px-5 py-2.5 text-sm font-bold bg-red-500 hover:bg-red-600 text-white rounded-xl shadow-md transition">Удалить</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  category: Object,
});

defineEmits(['close', 'confirm']);
</script>