// @ts-check
import { defineConfig } from 'astro/config';

// Deployed to GitHub Pages (see ops/run_watcher.sh). If a custom domain is
// ever attached, set SITE_URL to it and drop BASE_PATH.
export default defineConfig({
  site: process.env.SITE_URL || 'http://localhost:4321',
  base: process.env.BASE_PATH || '/',
});
