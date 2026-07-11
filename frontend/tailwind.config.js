/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'ibm-blue':   '#0f62fe',
        'ibm-cyan':   '#1192e8',
        'ibm-purple': '#8a3ffc',
        'ibm-green':  '#24a148',
        'ibm-yellow': '#f1c21b',
        'ibm-red':    '#da1e28',
        'ibm-white':  '#f4f4f4',
        'ibm-gray':   '#161616',
        'ibm-gray-2': '#262626',
        'ibm-gray-3': '#393939',
        'ibm-gray-4': '#8d8d8d',
        'ibm-dark':   '#0f0f0f',
      },
      keyframes: {
        'fade-in':  { from: { opacity: '0' }, to: { opacity: '1' } },
        'slide-up': { from: { opacity: '0', transform: 'translateY(12px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
      },
      animation: {
        'fade-in':  'fade-in 0.3s ease-out',
        'slide-up': 'slide-up 0.4s ease-out',
      },
    },
  },
  plugins: [],
}
