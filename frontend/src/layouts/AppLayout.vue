<template>
  <div class="flex h-screen bg-slate-100">
    <!-- Боковая панель для ПК -->
    <aside class="w-64 bg-slate-900 text-slate-300 flex flex-col justify-between shadow-xl">
      <div>
        <div class="h-16 flex items-center px-6 bg-slate-950 font-bold text-lg text-white tracking-wide border-b border-slate-800">
          💰 Family Finance
        </div>
        <nav class="mt-6 px-3 space-y-1">
          <RouterLink
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition"
            :class="[$route.path === item.path ? 'bg-brand-600 text-white' : 'hover:bg-slate-800 hover:text-white']"
          >
            <span>{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </RouterLink>
        </nav>
      </div>

      <!-- Пользователь внизу панели -->
      <div class="p-4 border-t border-slate-800 bg-slate-950/50 flex items-center justify-between">
        <div class="overflow-hidden">
          <p class="text-sm font-semibold text-white truncate">{{ auth.user?.name }}</p>
          <p class="text-xs text-slate-400 capitalize">{{ auth.user?.role }}</p>
        </div>
        <button @click="handleLogout" title="Выйти" class="text-slate-400 hover:text-rose-400 transition text-sm">
          🚪
        </button>
      </div>
    </aside>

    <!-- Основной контент -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Верхняя шапка -->
      <header class="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between shadow-sm">
        <h1 class="text-xl font-bold text-slate-800">{{ pageTitle }}</h1>
        <div class="flex items-center gap-4">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
            Семья: {{ auth.user?.family_group_id }}
          </span>
        </div>
      </header>

      <!-- Контейнер страниц -->
      <main class="flex-1 overflow-y-auto p-8">
        <div class="max-w-7xl mx-auto">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const navItems = [
  { label: 'Главная и счета', path: '/', icon: '💳' },
  { label: 'Операции', path: '/transactions', icon: '📝' },
  { label: 'Категории и лимиты', path: '/categories', icon: '🏷️' },
  { label: 'Копилки', path: '/piggy-banks', icon: '🐖' },
  { label: 'Аналитика', path: '/analytics', icon: '📊' },
];

const pageTitle = computed(() => {
  const current = navItems.find((i) => i.path === route.path);
  return current ? current.label : 'Финансы';
});

function handleLogout() {
  auth.logout();
  router.push('/login');
}
</script>