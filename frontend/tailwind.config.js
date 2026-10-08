export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Пурпурная гамма по вашему рисунку
        theme: {
          dark: {
            bg: '#151022',       // Основной глубокий ночной фон
            surface: '#1f1735',  // Фон панелей и сайдбара
            card: '#2b1f4a',     // Фиолетовые карточки
            border: '#44316f',   // Разделители
            hover: '#3a2b61',
            text: '#f3e8ff',     // Светло-лиловый текст
            muted: '#a894c7',    // Второстепенный текст
          },
          light: {
            bg: '#f7f3fc',       // Светлый нежно-лавандовый фон
            surface: '#ffffff',  // Белые панели
            card: '#ffffff',     // Карточки
            border: '#e7dcf5',   // Светлые сиреневые рамки
            hover: '#f0e6fb',
            text: '#22133b',     // Глубокий сливовый текст
            muted: '#7a6894',    // Приглушённый текст
          },
          accent: {
            primary: '#8b5cf6',   // Основной фиолетовый акцент
            hover: '#7c3aed',
            lavender: '#c499f3',
            plum: '#4c1d95',
            success: '#10b981',   // Доходы (зеленый)
            danger: '#ef4444',    // Расходы (красный)
            warning: '#f59e0b',   // Инвестиции (янтарный)
          }
        }
      }
    },
  },
  plugins: [],
}