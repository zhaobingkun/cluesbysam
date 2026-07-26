# Project Experience

## Current Notes
- `README.md` and `PROJECT-MEMORY.md` existed before `agents.md` / `memory.md`; keep using them as historical context.
- The homepage has an embedded official game iframe and a latest answer video block near the top. If a homepage area disappears, check iframe blocking, external media requests, and JavaScript-rendered cards first.

## 2026-06-29 iframe Display Issue
- `https://cluesbysam.com/` currently returns `Content-Security-Policy: frame-ancestors 'none'` and `X-Frame-Options: DENY`.
- Because browsers enforce those headers, `cluesbysam.net` cannot embed the official game in an iframe while those headers remain.
- The homepage and `/game.html` should use a direct external link to the official game instead of an embedded iframe.

## 2026-06-29 Homepage Repositioning
- After iframe embedding stopped working, the homepage should lead with `today's answer + video walkthrough + full archive`.
- Treat the official game link as a supporting external action, not the main product surface.
- Keep the homepage SEO focused on `Clues by Sam answer`, `walkthrough`, `daily guide`, and `archive`.

## 2026-07-26 AdSense invalid-traffic hardening

- AdSense Auto ads retained, but Ad intents, anchor ads, and vignette ads were disabled; side-rail and in-page banner formats remain enabled.
- Auto optimize and automatic experiment adoption were disabled.
- All static pages now defer the AdSense loader until the first user interaction or 8 seconds after load.
- Android WebView traffic does not load AdSense, while normal analytics remain unaffected.
- `404.html`, `contact.html`, `privacy.html`, `terms-of-service.html`, and `game.html` carry `data-adsense="off"` and do not load ads.
- Keep the generator template in `scripts/sync_from_playlist_ini.py` aligned so regenerated level pages retain the same loader.
