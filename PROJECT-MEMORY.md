# Project Memory

## Project Identity
- Path: `/Users/zhaobingkun/dev/cluesbysam/cluesbysam.org`
- Live domain: `https://cluesbysam.net`
- Important note: local folder is `.org`, but canonical URLs, sitemap, robots, email, and branding all use `.net`
- Site type: static SEO walkthrough site for the daily logic puzzle game **Clues by Sam**

## Current Content State
- Current level count: `256`
- Current max level: `256`
- Current `index.html` count: `257`
  - `256` level pages under `level/<n>/index.html`
  - `1` root homepage `index.html`
- Top-level static pages include:
  - `index.html`
  - `levels.html`
  - `game.html`
  - `blog.html`
  - `contact.html`
  - `privacy.html`
  - `terms-of-service.html`
  - `404.html`
- Blog content currently includes:
  - `blog/color-tags.html`
  - `blog/neighbor-logic.html`

## Core Data And Files
- Main data source: `assets/js/playlist-data.js`
- Main frontend logic:
  - `assets/js/levels.js`
  - `assets/js/site.js`
- Main stylesheet:
  - `assets/css/style.css`
- Sitemap:
  - `sitemap.xml`
- Robots:
  - `robots.txt`
- Main sync script:
  - `scripts/sync_from_playlist_ini.py`

## Title And Copy Rules
- User-facing guide titles were changed from `Level N` style to **date-first** style
- Current preferred title format:
  - `Clues by Sam Answer & Walkthrough | 7th April 2026`
- This format is used on:
  - level page `<title>`
  - level page `<h1>`
  - homepage cards
  - `levels.html` cards
  - video `data-title`
- Homepage latest-video wording was also changed to emphasize the daily guide:
  - badge: `Today's video guide`
  - CTA: `Open today’s answer`

## Homepage / Layout Notes
- Homepage was adjusted so the playable game iframe and the latest answer video can appear together more clearly
- The “latest answer” / “today’s video guide” block was moved beside the game section
- This site intentionally signals:
  - play the puzzle
  - watch the daily answer video
  - browse archived daily guides

## Level Import Workflow
- Recent additions were imported from:
  - `/Users/zhaobingkun/dev/cluesbysam/cluesbysam_txt/list22.rtf`
- Historical workflow also used:
  - `/Users/zhaobingkun/dev/cluesbysam/playlist.ini`
- Standard maintenance flow:
  1. Parse new video links and titles
  2. Append new items into `assets/js/playlist-data.js`
  3. Generate missing `level/<n>/index.html`
  4. Refresh homepage cards and `levels.html`
  5. Update `sitemap.xml`

## Recent Known State
- Latest imported range: `229-256`
- Homepage latest answer currently reflects late May 2026 content
- Canonical URLs and contact info already point to `cluesbysam.net`

## Known Cleanup / Technical Debt
- Old playlist history includes a few non-standard video titles that are not clean daily date entries
  - examples found in `assets/js/playlist-data.js`:
    - `Double Monday | Clues by Sam`
    - `Double CbS Monday! 26th January 2026`
    - `Maybe a lesson on perseverance?`
  - the sync script now skips irregular titles when building month archive jump links
- Month archive summaries are now generated from parsed entry dates, but they are still descriptive ranges rather than exact calendar-complete coverage notes

## Domain / Branding Rules
- Keep using `.net` in:
  - canonical
  - sitemap URLs
  - robots sitemap line
  - contact email
  - schema / metadata
- Do not switch branding back to `.org`; `.org` is only the local folder name

## Suggested Next Work
- Keep adding new daily pages when new walkthrough links appear
- Continue using date-first titles
- If future playlist exports add more irregular/non-date videos, keep them out of homepage/month archive grouping logic
- If improving SEO further:
  - strengthen homepage latest-answer section
  - keep archive cards updated
  - add more blog/support content around puzzle logic

## Re-entry Checklist
- When returning to this project, check these first:
  1. `assets/js/playlist-data.js`
  2. `scripts/sync_from_playlist_ini.py`
  3. `index.html`
  4. `levels.html`
  5. `sitemap.xml`
  6. whether the current max level has moved beyond `256`
