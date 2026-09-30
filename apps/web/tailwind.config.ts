import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        ocean: "#2f7dd1",
        evergreen: "#18715f"
      }
    }
  },
  plugins: []
} satisfies Config;
