import forms from "@tailwindcss/forms";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: { "2xl": "1440px" },
    },
    extend: {
      colors: {
        canvas: "hsl(var(--bg-canvas) / <alpha-value>)",
        surface: "hsl(var(--bg-surface) / <alpha-value>)",
        elevated: "hsl(var(--bg-elevated) / <alpha-value>)",
        border: "hsl(var(--border-subtle) / <alpha-value>)",
        ink: {
          DEFAULT: "hsl(var(--text-primary) / <alpha-value>)",
          muted: "hsl(var(--text-muted) / <alpha-value>)",
          subtle: "hsl(var(--text-subtle) / <alpha-value>)",
        },
        accent: {
          DEFAULT: "hsl(var(--accent-primary) / <alpha-value>)",
          secondary: "hsl(var(--accent-secondary) / <alpha-value>)",
          success: "hsl(var(--accent-success) / <alpha-value>)",
          danger: "hsl(var(--accent-danger) / <alpha-value>)",
          info: "hsl(var(--accent-info) / <alpha-value>)",
        },
        cell: {
          empty: "#1e293b",
          obstacle: "#52525b",
          mud: "#a16207",
          food: "#10b981",
          danger: "#e11d48",
          target: "#a78bfa",
          start: "#38bdf8",
        },
      },
      fontFamily: {
        serif: ['"Fraunces"', "ui-serif", "Georgia", "serif"],
        sans: ['"Inter"', "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        glow: "0 0 24px -4px hsl(var(--accent-primary) / 0.45)",
        "glow-amber": "0 0 24px -4px hsl(var(--accent-secondary) / 0.45)",
        soft: "0 1px 0 0 hsl(var(--border-subtle) / 0.6), 0 8px 24px -16px rgba(0,0,0,0.6)",
      },
      animation: {
        "pulse-soft": "pulse-soft 2.4s ease-in-out infinite",
        "fade-in": "fade-in 0.25s ease-out both",
        "slide-up": "slide-up 0.25s ease-out both",
      },
      keyframes: {
        "pulse-soft": {
          "0%, 100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.85", transform: "scale(1.04)" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "slide-up": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [forms],
};
