<template>
  <Teleport to="body">
    <div
      v-if="targetId"
      @click.self="$emit('cancel')"
      class="fixed inset-0 bg-slate-950/60 backdrop-blur-md flex items-center justify-center p-4 z-[70]"
    >
      <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-md p-6">
        <!-- Счёт был удалён -->
        <div v-if="isAccountMissing" class="text-center">
          <div class="w-12 h-12 rounded-2xl bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center mx-auto mb-3 shadow-sm">
            <AlertTriangle class="w-6 h-6" />
          </div>
          <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-2">
            Счёт операции был удалён
          </h3>
          <p class="text-xs text-theme-light-muted mb-4 leading-relaxed">
            Счёт операции больше не существует. Куда зачислить отменяемые средства
            <strong class="font-mono text-purple-600 dark:text-purple-300">
              ({{ formatMoney(tx?.amount) }} {{ settings.getSymbol(tx?.currency) }})
            </strong>?
          </p>
          <div class="text-left mb-6">
            <label class="block text-xs font-bold text-theme-light-muted mb-1.5">
              Выберите счёт для возврата:
            </label>
            <CustomSelect
              :modelValue="refundAccountId"
              @update:modelValue="$emit('update:refundAccountId', $event)"
              :options="accountOptions"
              placeholder="Выберите счёт"
            />
          </div>
          <div class="flex flex-col sm:flex-row justify-end gap-2 text-xs font-bold">
            <button type="button" @click="$emit('cancel')" class="px-4 py-2.5 rounded-xl border border-theme-light-border hover:bg-slate-100 transition">Отмена</button>
            <button type="button" @click="$emit('confirm', false)" class="px-4 py-2.5 rounded-xl border border-rose-300 text-rose-500 hover:bg-rose-50 transition">Без зачисления</button>
            <button type="button" @click="$emit('confirm', true)" :disabled="!refundAccountId" class="px-4 py-2.5 bg-theme-accent-primary text-white rounded-xl shadow-md transition disabled:opacity-50">Зачислить и удалить</button>
          </div>
        </div>

        <!-- Обычное удаление -->
        <div v-else class="text-center">
          <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-2">Удалить операцию?</h3>
          <p class="text-xs text-theme-light-muted mb-6">
            Средства будут возвращены на счёт <strong class="text-purple-600">"{{ accountName }}"</strong>.
          </p>
          <div class="flex justify-center gap-3">
            <button type="button" @click="$emit('cancel')" class="px-5 py-2.5 text-xs font-bold rounded-xl border border-theme-light-border hover:bg-slate-100 transition">Отмена</button>
            <button type="button" @click="$emit('confirm', true)" class="px-5 py-2.5 text-xs font-bold bg-rose-500 hover:bg-rose-600 text-white rounded-xl shadow-md transition">Удалить</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { AlertTriangle } from 'lucide-vue-next';
import CustomSelect from '@/components/CustomSelect.vue';
import { useSettingsStore } from '@/stores/settings';

const settings = useSettingsStore();

defineProps({
  targetId: String,
  tx: Object,
  isAccountMissing: Boolean,
  refundAccountId: String,
  accountOptions: Array,
  accountName: String,
});
defineEmits(['cancel', 'confirm', 'update:refundAccountId']);

function formatMoney(val) { return (!val || isNaN(val)) ? '0' : Number(val).toLocaleString('ru-RU'); }
</script>