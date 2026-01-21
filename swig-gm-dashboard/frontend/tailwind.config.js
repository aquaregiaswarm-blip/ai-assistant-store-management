/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Swig Brand Colors
        swig: {
          red: '#EF3D4E',
          'red-dark': '#D32F3F',
          'red-light': '#F5737E',
          navy: '#0A1F44',
          'navy-light': '#1A3A6E',
          slate: '#8EA1AF',
          'slate-light': '#B8C5CE',
          bg: '#FFFFFF',
          card: '#F4F6F8',
          // Legacy alias for compatibility
          pink: '#EF3D4E',
          'pink-dark': '#D32F3F',
          'pink-light': '#F5737E',
        }
      },
      fontFamily: {
        display: ['Quicksand', 'sans-serif'],
        body: ['Open Sans', 'sans-serif'],
      },
      borderRadius: {
        'pill': '50px',
        'card': '16px',
      },
      boxShadow: {
        'card': '0 4px 12px rgba(0, 0, 0, 0.05)',
        'card-hover': '0 6px 16px rgba(0, 0, 0, 0.08)',
      },
    },
  },
  plugins: [],
}
