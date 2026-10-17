import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://mysortednest.life',
  output: 'static',
  integrations: [sitemap()],
});
