<template>
  <div class="flex h-screen overflow-hidden bg-theme-light-bg dark:bg-theme-dark-bg text-theme-light-text dark:text-theme-dark-text">
    <!-- Боковое меню -->
    <aside class="w-64 bg-theme-light-surface dark:bg-theme-dark-surface border-r border-theme-light-border dark:border-theme-dark-border flex flex-col justify-between shadow-lg z-20">
      <div>
        <!-- Логотип: без градиента, чистый цвет -->
        <div class="h-16 flex items-center gap-3 px-6 border-b border-theme-light-border dark:border-theme-dark-border">
          <div class="w-9 h-9 rounded-xl bg-purple-600 flex items-center justify-center text-white shadow-md shadow-purple-500/30">
            <WalletCards class="w-5 h-5 text-white" />
          </div>
          <span class="font-black text-xl tracking-tight text-purple-600 dark:text-purple-300">
            Family Finance
          </span>
        </div>

        <!-- Навигация -->
        <nav class="mt-6 px-3 space-y-1.5">
          <RouterLink
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3.5 px-3.5 py-3 rounded-xl text-sm font-semibold transition-all duration-150"
            :class="[
              $route.path === item.path
                ? 'bg-theme-accent-primary text-white shadow-md shadow-purple-500/25'
                : 'text-theme-light-muted dark:text-theme-dark-muted hover:bg-theme-light-hover dark:hover:bg-theme-dark-hover hover:text-purple-600 dark:hover:text-purple-300'
            ]"
          >
            <component :is="item.icon" class="w-5 h-5 stroke-[2.2]" />
            <span>{{ item.label }}</span>
          </RouterLink>
        </nav>
      </div>

      <!-- Пользователь внизу -->
      <div class="p-4 border-t border-theme-light-border dark:border-theme-dark-border bg-purple-50/50 dark:bg-theme-dark-card/40 flex items-center justify-between">
        <div class="flex items-center gap-3 overflow-hidden">
          <div class="w-9 h-9 rounded-full bg-purple-200 dark:bg-purple-900/60 flex items-center justify-center text-purple-700 dark:text-purple-300 font-bold text-sm">
            {{ auth.user?.name ? auth.user.name.charAt(0).toUpperCase() : 'U' }}
          </div>
          <div class="overflow-hidden">
            <p class="text-sm font-bold truncate">{{ auth.user?.name }}</p>
            <p class="text-xs text-purple-600 dark:text-purple-400 font-bold">
              {{ auth.user?.role === 'HUSBAND' ? 'Любими Муж' : 'КошкоЖена' }}
            </p>
          </div>
        </div>
        <button
          @click="handleLogout"
          title="Выйти"
          class="p-2 text-theme-light-muted dark:text-theme-dark-muted hover:text-red-500 dark:hover:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/30 transition"
        >
          <LogOut class="w-5 h-5" />
        </button>
      </div>
    </aside>

    <!-- Основной контент -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Шапка -->
      <header class="h-16 bg-theme-light-surface dark:bg-theme-dark-surface border-b border-theme-light-border dark:border-theme-dark-border px-8 flex items-center justify-between z-10">
        <h1 class="text-xl font-black tracking-tight text-slate-800 dark:text-purple-100">{{ pageTitle }}</h1>

        <div class="flex items-center gap-4">
          <button
            @click="settings.toggleTheme()"
            class="p-2 rounded-xl border border-theme-light-border dark:border-theme-dark-border hover:bg-theme-light-hover dark:hover:bg-theme-dark-hover transition text-purple-600 dark:text-purple-300"
            title="Переключить тему"
          >
            <Sun v-if="settings.isDark" class="w-5 h-5" />
            <Moon v-else class="w-5 h-5" />
          </button>

          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 dark:bg-purple-950/80 dark:text-purple-300 border border-purple-200 dark:border-purple-800">
            Семья: {{ auth.user?.family_group_id }}
          </span>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-8 bg-theme-light-bg dark:bg-theme-dark-bg">
        <div class="max-w-7xl mx-auto pb-12">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import { LayoutDashboard, CreditCard, CalendarDays, Tags, PiggyBank, Settings, LogOut, Sun, Moon, WalletCards } from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const settings = useSettingsStore();

onMounted(() => {
  settings.initTheme();
  settings.fetchRates(); // ИСПРАВЛЕНИЕ: Скачиваем курсы при входе
});

const navItems = [
  { label: 'Главная', path: '/', icon: LayoutDashboard },
  { label: 'Счета', path: '/accounts', icon: CreditCard },
  { label: 'Журнал операций', path: '/transactions', icon: CalendarDays },
  { label: 'Категории и лимиты', path: '/categories', icon: Tags },
  { label: 'Копилки', path: '/piggy-banks', icon: PiggyBank },
  { label: 'Настройки', path: '/settings', icon: Settings },
];

const pageTitle = computed(() => {
  const current = navItems.find((i) => i.path === route.path);
  return current ? current.label : 'Семейный бюджет';
});

function handleLogout() {
  auth.logout();
  router.push('/login');
}
</script>