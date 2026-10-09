export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        theme: {
          dark: {
            bg: '#151022',
            surface: '#1f1735',
            card: '#2b1f4a',
            border: '#44316f',
            hover: '#3a2b61',
            text: '#f3e8ff',
            muted: '#a894c7',
          },
          light: {
            bg: '#fdfbf7',       // Исправлено: Теплый кремовый фон
            surface: '#ffffff',
            card: '#ffffff',
            border: '#e8e1d5',   // Исправлено: Более теплые рамки
            hover: '#f5f0e6',    // Исправлено: Теплый ховер
            text: '#3d312a',     // Исправлено: Мягкий темно-коричневый текст
            muted: '#8c7d70',    // Исправлено: Теплый приглушенный
          },
          accent: {
            primary: '#8b5cf6',
            hover: '#7c3aed',
            lavender: '#c499f3',
            plum: '#4c1d95',
            success: '#10b981',
            danger: '#ef4444',
            warning: '#f59e0b',
          }
        }
      }
    },
  },
  plugins: [],
}