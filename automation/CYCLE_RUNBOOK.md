# MY SORTED NEST — AUTOPILOT RUNBOOK
For the cron agent running the article cycle. Follow exactly, in order.

## 0. Run discipline (added 2026-10-14 after repeated worker failures — read first)
- Hard budget: the whole run must finish inside 2h. If you hit 90 minutes and are not at step 6 yet, skip remaining optional work, do the bookkeeping, and report plainly.
- Per-step watchdog: no single step (subagent spawn, browser task, npm build) may run silently longer than 40 minutes. If it does, abandon it, record what was attempted, and either continue with what is available or stop and report. NEVER burn the full run budget waiting on one stuck step — the 2026-10-14 01:07 run timed out after ~5h without even picking an article.
- Fail fast, report exactly: if any step fails twice, stop immediately, stamp last_error into the relevant JSON (queue.json / pins-queue.json), append a memory log entry, and report the exact step and error. A fast honest failure beats a silent timeout.
- Pre-flight (2 min max): verify automation/queue.json is readable JSON and /home/hatch/workspace/mysortednest exists before spawning anything. If not, stop and report.
- Subagents: put an explicit time box in every spawned subagent's prompt ("return within 40 minutes; if you cannot finish, return what you have plus what is missing").
- Deploy (step 6): the 6a session check is mandatory and must be a REPORT-ONLY task. If SESSION EXPIRED: try the saved login ONCE; if it fails, stop and report — no retry loops, no guessing, no burning the budget on login attempts.

## 1. Pick the next article
- Read `/home/hatch/workspace/mysortednest/automation/queue.json`.
- Take the FIRST article with `"status": "pending"`. If none pending, GENERATE new topics yourself (do not stop):
  - Create 5 new article entries following the niche pillars: small-space organization, closet & wardrobe, kitchen storage, storage hacks/DIY, entryway, bathroom, laundry, home office.
  - Each needs: SEO title (listicle "15–21 ideas" or how-to, long-tail keyword in title), primary + 2-3 secondary keywords, 6-8 bullet H2 outline, category (one of: small-spaces, closet-organization, kitchen, storage-ideas, decorating), 150-160 char description with keyword, 3 image_prompts (hero + 2 detail, same warm editorial style), slug (kebab-case from title), status "pending".
  - Append to queue.json and continue with the first one. Topics must not duplicate existing slugs/titles.

## 2. Write the article (subagent)
- Spawn a writer subagent. Its prompt: "Read /home/hatch/workspace/mysortednest/automation/ARTICLE_WRITER_BRIEF.md and follow it exactly. Article specs: [paste title, keywords, intent, outline, category, image filenames from queue]. Write to /home/hatch/workspace/mysortednest/src/content/blog/<slug>.md. Report word count, H2 count, idea count."
- Image filenames for the article = keys of the article's `image_prompts` + ".jpg" (e.g. `entryway-hero.jpg`).

## 3. Generate images (subagent, parallel with step 2)
- Spawn an image subagent: "Use media.generate_image (max 4 calls/turn). Generate 5 images: 1 hero + 4 detail shots. Style for every prompt: 'Warm editorial interior photography, Scandinavian minimalism, warm ivory/cream/beige palette with sage green and terracotta accents, soft natural daylight, uncluttered, serene, photorealistic, no people, no text or watermarks.' Output dir /home/hatch/workspace/mysortednest/public/images, format jpg. Use the article's image_prompts from queue.json for the first 3, then invent 2 MORE detail-shot prompts yourself in the same style covering other outline sections (close-ups, process shots). Name stems: <slug>-hero, <slug>-01, <slug>-02, <slug>-03, <slug>-04. Verify all are valid JPEGs." Pass the 5 filenames to the writer for inline placement (one visual per ~300 words).

## 4. QA gate (you run this)
- `python3 /home/hatch/workspace/mysortednest/automation/qa-check.py <article-path> "<primary keyword>" <idea-count-from-title>`
- If FAIL: fix the article yourself (edit the markdown) and re-run until it passes. Max 3 fix rounds; if still failing, mark article "needs-review" in queue.json and stop.

## 5. Build + QA (local)
- `cd /home/hatch/workspace/mysortednest && npm run build`
- Build must complete with no ERROR lines.
- Verify: new article page exists in dist/blog/<slug>/, exactly 1 `<h1` in it, sitemap includes the URL.
- (2026-11-24: `npm run build` auto-runs `prebuild` → `scripts/optimize-images.mjs`, which generates a max-800px WebP twin for every JPG in public/images + `src/data/image-dims.json`. Templates and article-body images serve the WebP automatically. New article JPGs need NO extra step — just upload the JPGs as usual and the build handles the rest. NEVER commit .webp files or the dims manifest; both are gitignored and regenerated on every build, including on the Actions runner.)
- (2026-10-17: Netlify zip-deploy is RETIRED. Site now deploys from GitHub repo Ussu1101/mysortednest via GitHub Pages. No zip packaging.)

## 6. Deploy (git push → GitHub Pages)
- Push the new/changed files to the GitHub repo (owner Ussu1101, repo mysortednest, branch main) via the GitHub connector:
  `/opt/hatch/bin/github call-tool --name push_files --arguments-json '{"owner":"Ussu1101","repo":"mysortednest","branch":"main","message":"<slug>: new article","files":[{"path":"src/content/blog/<slug>.md","content":"<full file content>"},{"path":"public/images/<img1>","content":"<base64 — NOT supported, see below>"}]}'`
- TEXT files (article .md): push via the API as above. Keep each call's arguments JSON under ~110KB (shell arg limit); split into multiple pushes if needed.
- IMAGE files (public/images/*.jpg): the API takes string content only — binary images CANNOT go through push_files. Upload images via a browser task instead: `browser.spawn_task` with `files: [{"path": "workspace/mysortednest/public/images/<img>"}]`, initial_url `https://github.com/Ussu1101/mysortednest/upload/main/public/images`, task: attach all granted files, wait for uploads to finish, commit directly to main with message "Article images: <slug>".
- New articles also need NO other repo changes (workflow builds automatically on push).
- After pushing, wait ~2-4 min for the Actions "Deploy to GitHub Pages" run to complete, then verify https://mysortednest.life/blog/<slug>/ returns 200 and shows the article title (H1).
- If the GitHub API returns 403 "Resource not accessible by integration": wait 2 min and retry ONCE. If it still 403s, do the whole push via browser web UI (create/upload files at github.com/Ussu1101/mysortednest) and report the 403 to HULK.
- If the deploy fails twice, report the failure and stop (do not mark published).
- (2026-10-21: a connector push did not fire the Actions "Deploy to GitHub Pages" workflow run — push event did not trigger. If the article page is not live ~5 min after pushing, check Actions for the run; if absent, manually dispatch "Deploy to GitHub Pages" via workflow_dispatch and re-verify before declaring a deploy failure.)
- (2026-10-17: Never use Netlify for this site again. The Netlify site vermillion-boba-535ed9 is retired; DNS points to GitHub Pages.)

### 6b. Submit the new article to IndexNow (Bing) — added 2026-11-21
- Only AFTER the article page is verified live (200). The IndexNow key lives at `/home/hatch/workspace/msn-indexnow/key.txt` and its key file is hosted at `https://mysortednest.life/<key>.txt` (verified live 2026-11-21). Submit just the new article URL:
```bash
python3 -c "
import json, urllib.request
key = open('/home/hatch/workspace/msn-indexnow/key.txt').read().strip()
payload = json.dumps({'host': 'mysortednest.life', 'key': key, 'keyLocation': f'https://mysortednest.life/{key}.txt', 'urlList': ['https://mysortednest.life/blog/<slug>/']}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=payload, headers={'Content-Type': 'application/json; charset=utf-8'})
print('IndexNow:', urllib.request.urlopen(req).status)
"
```
- Expect `IndexNow: 200` or `202` (accepted). Retry once on failure and report the status in the run report. Never submit the same URL twice in one run.

## 7. Create 4 pins
- Generate 4 FRESH vertical background images (portrait orientation) via a subagent — same style as article images, varied angles/details related to the article topic. Save to /home/hatch/workspace/mysortednest/pins/<slug>/bg1.jpg … bg4.jpg.
- Write 4 DIFFERENT pin titles (hooks/angles, each ≤90 chars) and 4 DIFFERENT descriptions (each 1-2 lines, include keywords naturally, no duplicates across pins).
- Build pinspec JSON and run `python3 /home/hatch/workspace/mysortednest/automation/make-pins.py pinspec.json` → pin1.jpg … pin4.jpg in the same folder.
- Append to `/home/hatch/workspace/mysortednest/automation/pins-queue.json`: entries {pin, title, description, url, status: "queued"}. Do NOT assign board here — the poster assigns boards by rotation.

## 8. Update queue + report
- Set the article's status to "published" in queue.json, add "published_at" date.
- Report to the user: article title + URL, QA result, deploy status, pins created (count). Keep it short.
