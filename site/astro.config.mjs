// @ts-check
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  site: "https://stiven-gjekaj.github.io",
  // GitHub Pages serves the repository at /cydia/.
  base: "/cydia/",
  trailingSlash: "ignore",
  vite: { plugins: [tailwindcss()] },
});
