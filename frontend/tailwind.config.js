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
            border: '#4a3778',
            hover: '#3a2b61',
            text: '#ffffff',       // Основной текст — чистый белый
            muted: '#d8b4fe',      // Контрастный сочный светло-лавандовый
          },
          light: {
            bg: '#fdfbf7',
            surface: '#ffffff',
            card: '#ffffff',
            border: '#e8e1d5',
            hover: '#f5f0e6',
            text: '#3d312a',
            muted: '#8c7d70',
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