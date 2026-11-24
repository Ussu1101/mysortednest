// Rehype plugin: rewrites <img> tags inside article markdown to their
// build-time WebP twins and adds width/height (CLS fix). Reads the manifest
// written by scripts/optimize-images.mjs (prebuild step); if the manifest
// is missing or an image has no entry, the tag is left untouched.
import fs from 'node:fs';
import path from 'node:path';

const manifestPath = path.resolve('src/data/image-dims.json');
let manifest = {};
try {
  manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
} catch {
  // No manifest yet (e.g. plain `astro build` without prebuild) — no-op.
}

export default function rehypeImgWebp() {
  return (tree) => {
    const walk = (node) => {
      if (node.type === 'element' && node.tagName === 'img') {
        const src = node.properties?.src;
        if (typeof src === 'string' && manifest[src]) {
          const d = manifest[src];
          node.properties.src = d.webp;
          node.properties.width = d.w;
          node.properties.height = d.h;
          if (!node.properties.loading) node.properties.loading = 'lazy';
          node.properties.decoding = 'async';
        }
      }
      if (node.children) node.children.forEach(walk);
    };
    walk(tree);
  };
}
