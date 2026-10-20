# Project Experience

## Current Notes
- 2026-09-08 23:15 CST: GSC P0 added raw HTML Open Graph/Twitter metadata and page-specific JSON-LD to the homepage, archive, and play entry pages. `assets/js/site.js` now avoids duplicate WebSite schema on those pages and uses `.net`-consistent guide branding. Added `scripts/verify_site.py` to verify canonicals, sitemap targets, internal links, and 404 noindex; the initial run exposed and fixed an indexable `404.html`.
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

## 2026-08-02 Daily sync publishing
- The macOS launchd entry still runs `/Users/zhaobingkun/dev/Python/spider/run_cluesbysam_daily.sh` every day at 10:45.
- That wrapper now delegates to `scripts/run_daily_and_publish.sh`, which runs the fetcher, refuses to overwrite a dirty site repo, commits generated site changes, and pushes `origin/main` so Vercel can deploy.
- YouTube titles may use abbreviated English months such as `1 Aug 2026`; both the fetcher and site generator accept full and abbreviated month names.
- If a push fails after a local commit, the next run can retry the push because the site repo remains clean and the commit is still ahead of `origin/main`.
- The first real replay added level 320 for `1st Aug 2026`; the generated commit pushed successfully and `https://cluesbysam.net/level/320/` returned HTTP 200.

## 2026-08-04 Codex daily task
- Codex automation `clues-by-sam` runs daily at 11:15 as a health check and failure retry for the primary macOS launchd run at 10:45.
- It skips duplicate fetching when the 10:45 run succeeded and the repo is clean and synchronized; otherwise it invokes `/Users/zhaobingkun/dev/Python/spider/run_cluesbysam_daily.sh` and verifies the push/live result.

## 2026-10-21 Single-page SEO routing experiment

- User selected Clues after the ten-site checks. Only /game.html is changed: clearer latest-guide/archive/spoiler-free-help routes, three contextual static links, and a page-scoped auto-height override for the old game-embed card. Existing official external action and fan-made disclosure are preserved, not newly invented. No daily puzzle data or historical dates changed.
- GSC complete data ends 2026-10-18. Exact game URL 28d (09/21–10/18):86 clicks/35,857 impressions/0.2398%/position~4.63; prior28d74/34,264/0.2160%/~4.87. Strict90d(07/21–10/18):266/108,453/0.2453%/~4.83. Brand/navigation queries dominate; low CTR is not proof of bad titles. Keep title/H1/meta/OG/Twitter/canonical/noindex policy stable.
- GA4 property519866319, stream13294881969, tagG-99Y6YPMSV8 matches site.js; outbound-click enhanced measurement is already on, no settings changed. Same28d Organic Search landing /game.html:122 sessions/82 active/75 new/6 seconds; previous28d151/85/77/7 seconds. Short sessions may mean successful outbound navigation, not failure. Key event definitions remain unverified; zero is not zero business value.
- GSC page-filtered country/device totals differ from daily/page totals (28d72 vs86 clicks; three-month223 vs273). Preserve raw exports in the summary project and do not infer device shares or causes from the mismatch.
- Five new regression tests and verify_site.py pass (396HTML/393sitemap). Desktop and390px visual checks pass; mobile scrollWidth390 equals viewport390. sitemap game entry lastmod updated to2026-10-21, URL list unchanged. No global stylesheet, homepage, archive, analytics, ad settings, redirect or generator changes.
- This page is hand-maintained; daily sync only refreshes its navigation max. Do not run a whole-site rebuild for this edit. Daily wrapper refuses dirty repos, so commit only this bounded change after validation. Production/push evidence belongs in the independent report in the summary project; do not claim success before verifying. Review7/14/28days from actual publication.
