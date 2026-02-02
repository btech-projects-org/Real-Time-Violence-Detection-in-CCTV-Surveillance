/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'surveillance-dark': '#0f172a',
        'surveillance-card': '#1e293b',
        'threat-red': '#ef4444',
      },
    },
  },
  plugins: [],
}
