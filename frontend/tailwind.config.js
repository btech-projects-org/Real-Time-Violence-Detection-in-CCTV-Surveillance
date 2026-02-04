/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Semantic Colors
        brand: {
          50: '#eff6ff',
          500: '#3b82f6', // Standard Blue
          600: '#2563eb',
          900: '#1e3a8a',
        },
        danger: {
          500: '#ef4444', // Alert Red
          900: '#7f1d1d',
        },
        success: {
          500: '#22c55e', // Safe Green
        },
        warning: {
          500: '#f59e0b',
        },
        
        // Dark UI Surface Colors (Slate)
        surface: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569', // Borders
          700: '#334155', // Secondary BG
          800: '#1e293b', // Card BG
          900: '#0f172a', // Sidebar/Header
          950: '#020617', // Main BG
        }
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"], 
        mono: ["JetBrains Mono", "monospace"],
      },
      // Custom Utilities
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
