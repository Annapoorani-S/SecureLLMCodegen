/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['DM Mono', 'JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        // Core brand
        ink: '#07130f',
        surface: '#0d1d17',
        mint: '#8ce7b3',
        lime: '#c6f46b',
        // VS Code-style explorer
        editor: '#0e1e19',
        sidebar: '#091511',
        sidebarHover: '#112119',
        tabBar: '#0b1814',
        lineHighlight: '#14261f',
        gutter: '#1a2e25',
        statusBar: '#063010',
        // Semantic
        danger: '#f87171',
        warning: '#fbbf24',
        info: '#60a5fa',
        success: '#4ade80',
      },
      boxShadow: {
        glow: '0 0 50px rgba(140, 231, 179, 0.13)',
        panel: '0 4px 32px rgba(0,0,0,0.5)',
        tab: 'inset 0 -2px 0 #8ce7b3',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-in': 'slideIn 0.15s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideIn: { from: { opacity: 0, transform: 'translateX(-8px)' }, to: { opacity: 1, transform: 'translateX(0)' } },
        pulseSoft: { '0%,100%': { opacity: 1 }, '50%': { opacity: 0.5 } },
      },
    },
  },
  plugins: [],
}
