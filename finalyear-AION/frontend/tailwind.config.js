/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        panel: "#0f141b",
        panel2: "#131b25",
        line: "#2a3644",
        neon: "#6be8ff",
        good: "#42d392",
        bad: "#ff7f8a",
        danger: "#ff6b6b",
        warn: "#ffc857"
      },
      borderRadius: {
        card: "18px"
      },
      boxShadow: {
        float: "0 24px 44px rgba(0,0,0,0.35)"
      }
    }
  },
  plugins: []
};
