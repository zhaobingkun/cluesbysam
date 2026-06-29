# Project Experience

## Current Notes
- `README.md` and `PROJECT-MEMORY.md` existed before `agents.md` / `memory.md`; keep using them as historical context.
- The homepage has an embedded official game iframe and a latest answer video block near the top. If a homepage area disappears, check iframe blocking, external media requests, and JavaScript-rendered cards first.

## 2026-06-29 iframe Display Issue
- `https://cluesbysam.com/` currently returns `Content-Security-Policy: frame-ancestors 'none'` and `X-Frame-Options: DENY`.
- Because browsers enforce those headers, `cluesbysam.net` cannot embed the official game in an iframe while those headers remain.
- The homepage and `/game.html` should use a direct external link to the official game instead of an embedded iframe.
