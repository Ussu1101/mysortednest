import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import rehypeImgWebp from './scripts/rehype-img-webp.mjs';

export default defineConfig({
  site: 'https://mysortednest.life',
  output: 'static',
  integrations: [sitemap()],
  markdown: {
    // Rewrites article-body <img> tags to their WebP twins + width/height.
    rehypePlugins: [rehypeImgWebp],
  },
});
