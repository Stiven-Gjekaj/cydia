// @ts-check
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://stiven-gjekaj.github.io",
  // GitHub Pages serves the repository at /cydia/.
  base: "/cydia/",
  trailingSlash: "ignore",
});
