/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0a",
        surface: "#141414",
        border: "rgba(255,255,255,0.06)",
        green: "#25D366",
        red: "#ff4444",
        blue: "#4d9fff",
        primary: "#f5f5f5",
        secondary: "#888888",
      },
      fontFamily: { sans: ["Outfit", "system-ui", "sans-serif"] },
      borderRadius: {
        none: "0px",
        sm: "2px",
        DEFAULT: "2px",
        md: "4px",
        lg: "6px",
      },
    },
  },
  plugins: [],
};
