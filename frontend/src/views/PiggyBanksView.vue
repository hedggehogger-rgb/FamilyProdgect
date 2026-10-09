<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-xl font-black text-slate-800 dark:text-purple-100">Семейные копилки</h2>
        <p class="text-xs text-theme-light-muted dark:text-theme-dark-muted mt-1">Накопления на совместные цели</p>
      </div>
      <button @click="showModal = true" class="bg-theme-accent-primary hover:bg-theme-accent-hover text-white text-xs px-4 py-2.5 rounded-xl font-bold transition shadow-md shadow-purple-500/20 flex items-center gap-2">
        <Plus class="w-4 h-4" /> Создать копилку
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="pb in piggyBanks" :key="pb.id" class="bg-theme-light-card dark:bg-theme-dark-card p-6 rounded-2xl border border-theme-light-border dark:border-theme-dark-border shadow-sm space-y-4">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-black text-slate-800 dark:text-purple-100 text-lg">{{ pb.name }}</h3>
            <span class="text-xs text-theme-light-muted dark:text-theme-dark-muted font-mono">Счёт списания: {{ getAccountName(pb.account_id) }}</span>
            <div v-if="pb.is_auto_replenish && !pb.is_completed" class="text-xs text-purple-600 dark:text-purple-400 mt-1 font-bold">
              Автопополнение: {{ pb.auto_replenish_amount }} {{ settings.getSymbol(pb.currency) }} (каждое {{ pb.auto_replenish_day }}-е число)
            </div>
            <div v-if="pb.is_auto_replenish && pb.skip_until_month === currentYearMonth" class="text-[11px] text-amber-600 font-bold mt-0.5">
              ⚠️ Пополнение пропущено в этом месяце
            </div>
            <div v-else-if="pb.is_auto_replenish && pb.snoozed_until" class="text-[11px] text-indigo-500 font-bold mt-0.5">
              ⏳ Отсрочено до: {{ new Date(pb.snoozed_until).toLocaleDateString('ru-RU') }}
            </div>
          </div>
          <span :class="pb.is_completed ? 'bg-emerald-100 text-emerald-800' : 'bg-purple-100 text-purple-800'" class="text-xs px-3 py-1 rounded-full font-bold">
            {{ pb.is_completed ? 'Цель достигнута 🎉' : 'Копим' }}
          </span>
        </div>

        <div>
          <div class="flex justify-between text-sm mb-1.5 font-mono">
            <span class="font-bold text-slate-800 dark:text-purple-100">{{ pb.current_amount }} {{ settings.getSymbol(pb.currency) }}</span>
            <span class="text-theme-light-muted dark:text-theme-dark-muted">из {{ pb.target_amount }} {{ settings.getSymbol(pb.currency) }}</span>
          </div>
          <div class="w-full bg-slate-200 dark:bg-purple-950 h-2.5 rounded-full overflow-hidden">
            <div class="bg-emerald-500 h-full transition-all duration-500" :style="{ width: getPercent(pb) + '%' }"></div>
          </div>
        </div>

        <div class="pt-2 border-t border-theme-light-border dark:border-theme-dark-border flex flex-wrap items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            <button @click="openDepositModal(pb)" class="text-xs bg-purple-100 dark:bg-purple-900/60 text-purple-700 dark:text-purple-300 hover:bg-purple-200 font-bold px-3 py-1.5 rounded-xl transition">
              Пополнить
            </button>

            <button
              @click="handleAutoClick(pb)"
              class="text-xs border flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-bold transition shadow-sm"
              :class="[
                pb.is_auto_replenish
                  ? 'border-emerald-300 dark:border-emerald-800/80 bg-emerald-50/50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300 hover:bg-red-50 hover:text-red-600 hover:border-red-200'
                  : 'border-theme-light-border dark:border-theme-dark-border bg-white dark:bg-theme-dark-card text-slate-700 dark:text-purple-200 hover:border-purple-400'
              ]"
            >
              <span class="w-2 h-2 rounded-full" :class="pb.is_auto_replenish ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-slate-600'"></span>
              {{ pb.is_auto_replenish ? 'Отключить авто' : 'Включить авто' }}
            </button>

            <button
              v-if="isApproaching(pb)"
              @click="openSnoozeModal(pb)"
              class="text-xs bg-red-500 hover:bg-red-600 text-white font-bold px-3 py-1.5 rounded-xl shadow-sm transition animate-pulse"
            >
              Отсрочить пополнение
            </button>
          </div>

          <button @click="askDelete(pb)" class="text-xs text-rose-500 hover:text-rose-700 font-bold">
            Разбить / Удалить
          </button>
        </div>
      </div>
    </div>

    <!-- Модалка создания копилки -->
    <Teleport to="body">
      <div v-if="showModal" @click.self="showModal = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
        <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6 max-h-[90vh] overflow-y-auto">
          <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-4">Новая копилка</h3>
          <form @submit.prevent="createPiggy" class="space-y-4">
            <div><label class="block text-xs font-bold text-theme-light-muted mb-1">Название цели</label><input v-model="createForm.name" required placeholder="На отпуск" class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border rounded-xl p-2.5 text-sm outline-none text-slate-800 dark:text-purple-100" /></div>
            <div><label class="block text-xs font-bold text-theme-light-muted mb-1">Целевая сумма</label><input v-model.number="createForm.target_amount" type="number" step="any" min="1" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border rounded-xl p-2.5 text-sm outline-none text-slate-800 font-mono font-bold" /></div>
            <div><label class="block text-xs font-bold text-theme-light-muted mb-1">Счёт для списаний (по умолчанию)</label><CustomSelect v-model="createForm.account_id" :options="accountOptions" /></div>
            <div><label class="block text-xs font-bold text-theme-light-muted mb-1">Валюта копилки</label><CustomSelect v-model="createForm.currency" :options="symbolCurrencyOptions" /></div>

            <div class="pt-3 border-t border-theme-light-border">
              <div class="flex items-center gap-2 mb-3">
                <input type="checkbox" v-model="createForm.is_auto_replenish" id="auto" class="rounded accent-purple-600 w-4 h-4 cursor-pointer" />
                <label for="auto" class="text-xs font-bold text-slate-800 dark:text-purple-200 cursor-pointer">Включить автопополнение</label>
              </div>
              <div v-if="createForm.is_auto_replenish" class="space-y-3">
                <div><label class="block text-xs font-bold text-theme-light-muted mb-1">Сумма в месяц</label><input v-model.number="createForm.auto_replenish_amount" type="number" step="any" min="1" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border rounded-xl p-2.5 text-sm font-mono" /></div>
                <div><label class="block text-xs font-bold text-theme-light-muted mb-1">Число месяца списания (1-31)</label><input v-model.number="createForm.auto_replenish_day" type="number" min="1" max="31" required class="w-full bg-white dark:bg-theme-dark-card border border-theme-light-border rounded-xl p-2.5 text-sm" /></div>
              </div>
            </div>
            <div class="flex justify-end gap-2 pt-2"><button type="button" @click="showModal = false" class="px-4 py-2 text-xs font-bold rounded-xl border hover:bg-slate-100 transition">Отмена</button><button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary text-white rounded-xl shadow-md">Создать</button></div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Модалка автопополнения -->
    <Teleport to="body">
      <div v-if="autoConfigTarget" @click.self="autoConfigTarget = null" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
        <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border dark:border-theme-dark-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
          <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-1">Включить автопополнение</h3>
          <p class="text-xs text-theme-light-muted mb-4">Для копилки "{{ autoConfigTarget.name }}"</p>
          <form @submit.prevent="submitEnableAuto" class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-theme-light-muted mb-1">Сумма списания ({{ settings.getSymbol(autoConfigTarget.currency) }})</label>
              <input v-model.number="autoConfigForm.amount" type="number" step="any" min="1" required class="w-full bg-white dark:bg-theme-dark-card border rounded-xl p-2.5 text-sm font-mono font-bold" />
            </div>
            <div>
              <label class="block text-xs font-bold text-theme-light-muted mb-1">Число месяца списания (1-31)</label>
              <input v-model.number="autoConfigForm.day" type="number" min="1" max="31" required class="w-full bg-white dark:bg-theme-dark-card border rounded-xl p-2.5 text-sm font-mono font-bold" />
            </div>
            <div>
              <label class="block text-xs font-bold text-theme-light-muted mb-1">Счёт для списания</label>
              <CustomSelect v-model="autoConfigForm.account_id" :options="accountOptions" />
            </div>
            <div class="flex justify-end gap-2 pt-2">
              <button type="button" @click="autoConfigTarget = null" class="px-4 py-2 text-xs font-bold rounded-xl border hover:bg-slate-100 transition">Отмена</button>
              <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary text-white rounded-xl shadow-md">Сохранить и включить</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Модалка пополнения -->
    <Teleport to="body">
      <div v-if="depositTarget" @click.self="depositTarget = null" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
        <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
          <h3 class="text-base font-black text-slate-800 dark:text-purple-100 mb-4">Пополнить "{{ depositTarget.name }}"</h3>
          <form @submit.prevent="submitDeposit" class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-theme-light-muted mb-1">Сумма и валюта взноса</label>
              <div class="flex gap-2">
                <input v-model.number="depositForm.amount" type="number" step="any" min="0.01" required placeholder="0.00" class="flex-1 bg-white dark:bg-theme-dark-card border rounded-xl p-2.5 text-sm font-mono font-bold" />
                <div class="w-24 shrink-0">
                  <CustomSelect v-model="depositForm.currency" :options="symbolCurrencyOptions" size="md" />
                </div>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-theme-light-muted mb-1">Списать со счёта</label>
              <CustomSelect v-model="depositForm.account_id" :options="accountOptions" />
            </div>
            <div class="flex justify-end gap-2 pt-2">
              <button type="button" @click="depositTarget = null" class="px-4 py-2 text-xs font-bold rounded-xl border hover:bg-slate-100 transition">Отмена</button>
              <button type="submit" class="px-4 py-2 text-xs font-bold bg-theme-accent-primary text-white rounded-xl shadow-md">Внести</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Модалка отсрочки -->
    <Teleport to="body">
      <div v-if="snoozeTarget" @click.self="snoozeTarget = null" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
        <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border rounded-2xl shadow-2xl w-full max-w-sm p-6 space-y-4">
          <h3 class="text-base font-black text-slate-800 dark:text-purple-100">Отсрочить пополнение</h3>
          <p class="text-xs text-theme-light-muted">Плановое пополнение копилки "{{ snoozeTarget.name }}" назначено на {{ snoozeTarget.auto_replenish_day }}-е число.</p>

          <div>
            <label class="block text-xs font-bold text-theme-light-muted mb-1.5">Выбрать новую дату пополнения</label>
            <CustomDatePicker v-model="snoozeDateInput" placeholder="Выберите дату" />
          </div>

          <div class="flex flex-col gap-2 pt-2">
            <button @click="confirmSnoozeDate" class="w-full py-2.5 text-xs font-bold bg-theme-accent-primary hover:bg-theme-accent-hover text-white rounded-xl shadow-md transition">
              Перенести на выбранную дату
            </button>
            <button @click="confirmSkipMonth" class="w-full py-2.5 text-xs font-bold bg-amber-500 hover:bg-amber-600 text-white rounded-xl shadow-md transition">
              Пропустить пополнение в этом месяце
            </button>
            <button @click="snoozeTarget = null" class="w-full py-2 text-xs font-bold rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-slate-100 dark:hover:bg-theme-dark-hover transition">
              Отмена
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Модалка удаления копилки -->
    <Teleport to="body">
      <div v-if="deleteTarget" @click.self="deleteTarget = null" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
        <div class="bg-theme-light-surface dark:bg-theme-dark-surface border border-theme-light-border rounded-2xl shadow-2xl w-full max-w-sm p-6">
          <h3 class="text-lg font-black text-slate-800 dark:text-purple-100 mb-2">Разбить копилку?</h3>
          <p class="text-sm text-theme-light-muted mb-4">Накопленные {{ deleteTarget.current_amount }} {{ settings.getSymbol(deleteTarget.currency) }} будут зачислены на выбранный счёт.</p>
          <form @submit.prevent="confirmDelete">
            <div v-if="deleteTarget.current_amount > 0" class="mb-4 text-left">
              <label class="block text-xs font-bold text-theme-light-muted mb-1">Куда зачислить деньги?</label>
              <CustomSelect v-model="deleteTargetAccount" :options="accountOptions" required />
            </div>
            <div class="flex justify-center gap-3">
              <button type="button" @click="deleteTarget = null" class="px-5 py-2.5 text-sm font-bold rounded-xl border hover:bg-slate-100 transition">Отмена</button>
              <button type="submit" class="px-5 py-2.5 text-sm font-bold bg-red-500 hover:bg-red-600 text-white rounded-xl shadow-md">Разбить</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { Plus } from 'lucide-vue-next';
import api from '@/api';
import { useSettingsStore } from '@/stores/settings';
import CustomSelect from '@/components/CustomSelect.vue';
import CustomDatePicker from '@/components/CustomDatePicker.vue';

const settings = useSettingsStore();
const piggyBanks = ref([]);
const accounts = ref([]);
const showModal = ref(false);

const depositTarget = ref(null);
const depositForm = reactive({ amount: null, account_id: null, currency: 'RUB' });

const autoConfigTarget = ref(null);
const autoConfigForm = reactive({ amount: 1000, day: 1, account_id: '' });

const deleteTarget = ref(null);
const deleteTargetAccount = ref(null);

const snoozeTarget = ref(null);
const snoozeDateInput = ref('');

const createForm = reactive({ name: '', target_amount: 10000, account_id: '', currency: 'RUB', is_auto_replenish: false, auto_replenish_amount: 1000, auto_replenish_day: 1 });

const symbolCurrencyOptions = [
  { label: '₽', value: 'RUB' },
  { label: '$', value: 'USD' },
  { label: '֏', value: 'AMD' }
];

const accountOptions = computed(() => accounts.value.map(a => ({ label: `${a.name} (${settings.getSymbol(a.currency)})`, value: a.id })));
function getAccountName(id) { const acc = accounts.value.find(a => a.id === id); return acc ? acc.name : '?'; }
function getPercent(pb) { return Math.min(100, Math.round((Number(pb.current_amount) / Number(pb.target_amount)) * 100)); }

const now = new Date();
const currentYearMonth = computed(() => `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`);

function isApproaching(pb) {
  if (!pb.is_auto_replenish || pb.is_completed) return false;
  if (pb.skip_until_month === currentYearMonth.value) return false;
  const currentDay = now.getDate();
  const day = pb.auto_replenish_day;
  return (day >= currentDay && day - currentDay <= 4);
}

async function loadData() {
  const [pbRes, accRes] = await Promise.all([api.get('/piggy-banks'), api.get('/accounts')]);
  piggyBanks.value = pbRes.data; accounts.value = accRes.data;
  if (accounts.value.length && !createForm.account_id) createForm.account_id = accounts.value[0].id;
}

async function createPiggy() {
  await api.post('/piggy-banks', createForm);
  showModal.value = false; createForm.name = ''; createForm.is_auto_replenish = false; await loadData();
}

function openDepositModal(pb) {
  depositTarget.value = pb;
  depositForm.amount = null;
  depositForm.account_id = pb.account_id;
  depositForm.currency = pb.currency;
}

async function submitDeposit() {
  if (!depositForm.amount || depositForm.amount <= 0 || !depositForm.account_id) return;
  await api.post(`/piggy-banks/${depositTarget.value.id}/deposit`, {
    amount: depositForm.amount,
    account_id: depositForm.account_id,
    currency: depositForm.currency
  });
  depositTarget.value = null;
  await loadData();
}

function handleAutoClick(pb) {
  if (pb.is_auto_replenish) {
    disableAuto(pb);
  } else {
    openAutoConfigModal(pb);
  }
}

async function disableAuto(pb) {
  try {
    await api.post(`/piggy-banks/${pb.id}/auto-replenish`, {
      is_auto_replenish: false
    });
    await loadData();
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка отключения автопополнения');
  }
}

function openAutoConfigModal(pb) {
  autoConfigTarget.value = pb;
  autoConfigForm.amount = Number(pb.auto_replenish_amount) > 0 ? Number(pb.auto_replenish_amount) : 1000;
  autoConfigForm.day = Number(pb.auto_replenish_day) >= 1 ? Number(pb.auto_replenish_day) : 1;
  autoConfigForm.account_id = pb.account_id || (accounts.value.length ? accounts.value[0].id : '');
}

async function submitEnableAuto() {
  if (!autoConfigTarget.value) return;
  try {
    await api.post(`/piggy-banks/${autoConfigTarget.value.id}/auto-replenish`, {
      is_auto_replenish: true,
      auto_replenish_amount: autoConfigForm.amount,
      auto_replenish_day: autoConfigForm.day,
      account_id: autoConfigForm.account_id
    });
    autoConfigTarget.value = null;
    await loadData();
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка включения автопополнения');
  }
}

function openSnoozeModal(pb) {
  snoozeTarget.value = pb;
  const targetDate = new Date();
  targetDate.setDate(targetDate.getDate() + 3);
  const y = targetDate.getFullYear();
  const m = String(targetDate.getMonth() + 1).padStart(2, '0');
  const d = String(targetDate.getDate()).padStart(2, '0');
  snoozeDateInput.value = `${y}-${m}-${d}`;
}

async function confirmSnoozeDate() {
  if (!snoozeDateInput.value) return;
  try {
    await api.post(`/piggy-banks/${snoozeTarget.value.id}/snooze`, {
      snooze_date: `${snoozeDateInput.value}T00:00:00`,
      skip_current_month: false
    });
    snoozeTarget.value = null;
    await loadData();
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка отсрочки пополнения');
  }
}

async function confirmSkipMonth() {
  try {
    await api.post(`/piggy-banks/${snoozeTarget.value.id}/snooze`, {
      skip_current_month: true
    });
    snoozeTarget.value = null;
    await loadData();
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка пропуска месяца');
  }
}

function askDelete(pb) {
  deleteTarget.value = pb;
  deleteTargetAccount.value = pb.account_id;
}

async function confirmDelete() {
  if (!deleteTarget.value) return;
  let url = `/piggy-banks/${deleteTarget.value.id}`;
  if (deleteTarget.value.current_amount > 0 && deleteTargetAccount.value) {
    url += `?target_account_id=${deleteTargetAccount.value}`;
  }
  await api.delete(url);
  deleteTarget.value = null;
  await loadData();
}

onMounted(loadData);
</script>