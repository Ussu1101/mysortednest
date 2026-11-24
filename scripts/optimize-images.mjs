// Build-time image optimizer for My Sorted Nest.
// Runs automatically before `astro build` (package.json "prebuild") — also on
// the GitHub Actions runner, so the .webp files are NEVER committed to git.
// For every JPG/PNG in public/images it generates a max-800px-wide WebP
// (quality 78) next to the original, and writes src/data/image-dims.json
// mapping each original path -> { webp, w, h } for width/height attributes.
// Incremental: skips images whose .webp is already newer than the source.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const imgDir = path.join(root, 'public', 'images');
const manifestPath = path.join(root, 'src', 'data', 'image-dims.json');
const MAX_W = 800;
const MAX_BYTES = 100 * 1024; // Screaming Frog flags images over 100 KB
const QUALITIES = [78, 60, 45]; // retry ladder for files still over MAX_BYTES
const CONCURRENCY = 4;

const files = fs.readdirSync(imgDir).filter((f) => /\.(jpe?g|png)$/i.test(f));
let made = 0, skipped = 0, failed = 0, savedBytes = 0, origBytes = 0;
const manifest = {};

// Keep an existing manifest's entries for images that no longer need work
// (so a partial run never drops entries).
try {
  Object.assign(manifest, JSON.parse(fs.readFileSync(manifestPath, 'utf8')));
} catch { /* first run */ }

async function processOne(file) {
  const srcPath = path.join(imgDir, file);
  const webpFile = file.replace(/\.(jpe?g|png)$/i, '.webp');
  const webpPath = path.join(imgDir, webpFile);
  const url = '/images/' + file;
  try {
    const srcStat = fs.statSync(srcPath);
    let webpStat = null;
    try { webpStat = fs.statSync(webpPath); } catch { /* missing */ }
    if (webpStat && webpStat.mtimeMs > srcStat.mtimeMs && webpStat.size <= MAX_BYTES) {
      // WebP already fresh and under the size cap — just record its
      // dimensions in the manifest.
      const wmeta = await sharp(webpPath).metadata();
      manifest[url] = { webp: '/images/' + webpFile, w: wmeta.width, h: wmeta.height };
      skipped++;
      origBytes += srcStat.size;
      savedBytes += srcStat.size - webpStat.size;
      return;
    }
    const img = sharp(srcPath);
    const meta = await img.metadata();
    // Quality ladder: start at 78, drop to 60 then 45 while the file is
    // still over the 100 KB cap (keeps the sharpest version that fits).
    let done = null;
    for (const q of QUALITIES) {
      await sharp(srcPath).resize({ width: MAX_W, withoutEnlargement: true }).webp({ quality: q }).toFile(webpPath);
      done = fs.statSync(webpPath);
      if (done.size <= MAX_BYTES) break;
    }
    manifest[url] = {
      webp: '/images/' + webpFile,
      w: Math.min(meta.width, MAX_W),
      h: Math.round(meta.height * Math.min(1, MAX_W / meta.width)),
    };
    made++;
    origBytes += srcStat.size;
    savedBytes += srcStat.size - done.size;
  } catch (e) {
    failed++;
    console.error('  FAIL', file, e.message);
  }
}

let i = 0;
async function worker() {
  while (i < files.length) {
    const file = files[i++];
    await processOne(file);
  }
}
await Promise.all(Array.from({ length: CONCURRENCY }, worker));

fs.mkdirSync(path.dirname(manifestPath), { recursive: true });
fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 0) + '\n');
const mb = (n) => (n / 1048576).toFixed(1) + ' MB';
console.log(`optimize-images: ${files.length} sources, ${made} webp built, ${skipped} skipped, ${failed} failed`);
console.log(`  originals ${mb(origBytes)} -> webp saves ~${mb(savedBytes)} (${origBytes ? Math.round(savedBytes / origBytes * 100) : 0}%)`);
