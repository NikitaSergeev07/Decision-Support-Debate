/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Space Grotesk', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['IBM Plex Mono', 'JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        surface: 'rgba(15, 14, 28, 0.7)',
        border: 'rgba(255, 255, 255, 0.07)',
      },
      animation: {
        'thinking': 'thinking 1.4s ease-in-out infinite',
        'spin-slow': 'spin 2s linear infinite',
        'pulse-ring': 'pulse-ring 1.5s ease-out infinite',
      },
      keyframes: {
        thinking: {
          '0%, 80%, 100%': { transform: 'scale(0)', opacity: '0.3' },
          '40%': { transform: 'scale(1)', opacity: '1' },
        },
        'pulse-ring': {
          '0%': { transform: 'scale(1)', opacity: '0.8' },
          '100%': { transform: 'scale(2)', opacity: '0' },
        },
      },
    },
  },
}
