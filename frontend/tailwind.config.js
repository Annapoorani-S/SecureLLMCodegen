/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: { ink: '#07130f', surface: '#0d1d17', mint: '#8ce7b3', lime: '#c6f46b' },
      boxShadow: { glow: '0 0 50px rgba(140, 231, 179, 0.13)' },
    },
  },
  plugins: [],
}
