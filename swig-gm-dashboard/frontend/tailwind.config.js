/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        swig: {
          pink: '#E91E63',
          'pink-dark': '#C2185B',
          'pink-light': '#F8BBD9',
        }
      }
    },
  },
  plugins: [],
}
