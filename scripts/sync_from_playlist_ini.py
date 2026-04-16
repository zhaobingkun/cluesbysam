#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAYLIST_JS = ROOT / "assets/js/playlist-data.js"
SITEMAP_XML = ROOT / "sitemap.xml"
INDEX_HTML = ROOT / "index.html"
LEVELS_HTML = ROOT / "levels.html"
MAX_HTML_GLOBS = ["*.html", "level/*/index.html"]

MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

HREF_AND_TITLE_RE = re.compile(
    r'href="/watch\?v=([A-Za-z0-9_-]{11})[^"]*"(?:(?!href="/watch\?v=).)*?title="(Clues by Sam \| [^"]+)"',
    re.S,
)

FOCUS_LINES = [
    "Resolve the overlap between the tightest clue groups before checking isolated tiles.",
    "Start with the strictest edge clue, then verify every diagonal neighbor before expanding.",
    "Use the first fully satisfied clue to mark safe squares before testing center clusters.",
    "Compare the smallest clue zones first so the remaining chain of suspects stays manageable.",
]

MISTAKE_LINES = [
    "Do not skip diagonal neighbors. Most wrong counts happen when one touching corner is ignored.",
    "Avoid locking a criminal shape too early. Re-check every overlapping clue before committing.",
    "Do not carry a guess across the board. Confirm each forced safe square before moving on.",
    "Watch for clue overlap. A tile that fits one clue can still break the next if you rush it.",
]

NOTE_LINES = [
    "Start by isolating every square touched by the strictest clue. Once those candidates shrink, the remaining answer path usually becomes mechanical.",
    "Open with the smallest confirmed clue on the board, then expand only after every diagonal count still checks out.",
    "Use the first solved region to mark guaranteed safe tiles, then sweep the rest of the board for forced contradictions.",
    "Treat the board like a chain of small deductions rather than one big guess. The cleanest path usually starts at the edge.",
]

INTRO_LINES = [
    "Need the Clues by Sam answer for level {level}? This page covers the {date} board with a direct walkthrough and quick archive links for nearby puzzles.",
    "Use this Clues by Sam answer page for level {level}. The video walkthrough below covers the {date} puzzle and links back to the full archive.",
    "This Clues by Sam level {level} guide collects the {date} answer, the video walkthrough, and nearby levels so you can keep moving through the archive.",
]

BRIEF_LINES = [
    "Stuck on this Clues by Sam level? Use the first two confirmed innocents to narrow the criminal chain, then compare every touching square before committing a guess.",
    "Stuck on this Clues by Sam level? Start by marking any clue that forces a row or column split, then verify all diagonal neighbors before locking criminals.",
    "Stuck on this Clues by Sam level? Clear the most restricted clue zone first, then use the newly safe tiles to unlock the next deduction.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync new Clues by Sam levels from a playlist HTML dump.")
    parser.add_argument("playlist_ini", help="Path to playlist.ini")
    return parser.parse_args()


def load_playlist_data() -> list[dict]:
    text = PLAYLIST_JS.read_text()
    prefix = "window.CLUES_PLAYLIST = "
    if not text.startswith(prefix):
        raise ValueError("Unexpected playlist-data.js format")
    payload = text[len(prefix):].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    items = json.loads(payload)
    for item in items:
        if "level" not in item:
            item["level"] = item.get("levelEnd", item.get("levelStart"))
    return items


def write_playlist_data(items: list[dict]) -> None:
    PLAYLIST_JS.write_text(
        "window.CLUES_PLAYLIST = " + json.dumps(items, indent=2, ensure_ascii=True) + ";\n"
    )


def parse_playlist_ini(path: Path) -> list[tuple[str, str]]:
    text = path.read_text()
    items: list[tuple[str, str]] = []
    for video_id, title in HREF_AND_TITLE_RE.findall(text):
        if items and items[-1][0] == video_id:
            continue
        items.append((video_id, title))
    return items


def extract_date(title: str) -> str:
    if "|" in title:
        return title.split("|", 1)[1].strip()
    match = re.search(r"(\d{1,2}(?:st|nd|rd|th) [A-Za-z]+ \d{4})$", title)
    if match:
        return match.group(1)
    raise ValueError(f"Unable to extract date from title: {title}")


def extract_date_for_entry(entry: dict) -> str:
    for key in ("title", "subtitle"):
        value = entry.get(key, "")
        if not value:
            continue
        try:
            return extract_date(value)
        except ValueError:
            continue
    level = entry.get("level", entry.get("levelEnd"))
    if level is not None:
        page = ROOT / "level" / str(level) / "index.html"
        if page.exists():
            text = page.read_text()
            match = re.search(r"<title>.*?\|\s*([^<]+)</title>", text, re.S)
            if match:
                return match.group(1).strip()
    raise ValueError(f"Unable to extract date for level {level}")


def date_to_iso(date_text: str) -> str:
    day_text, month_name, year_text = date_text.split()
    day = int(re.sub(r"(st|nd|rd|th)$", "", day_text))
    month = MONTHS[month_name]
    year = int(year_text)
    return datetime(year, month, day).strftime("%Y-%m-%d")


def build_entry(level: int, video_id: str, title: str) -> dict:
    return {
        "level": level,
        "title": title,
        "videoId": video_id,
        "subtitle": title,
        "href": f"https://www.youtube.com/watch?v={video_id}",
        "levelStart": level,
        "levelEnd": level,
        "slug": f"level-{level}",
    }


def format_title(date_text: str, *, html: bool) -> str:
    amp = "&amp;" if html else "&"
    return f"Clues by Sam Answer {amp} Walkthrough | {date_text}"


def build_card(level: int, video_id: str, date_text: str, image_kind: str) -> str:
    return (
        '      <div class="level-card">\n'
        f'        <span class="badge">Level {level}</span>\n'
        f'        <img class="card-thumb" src="https://img.youtube.com/vi/{video_id}/{image_kind}.jpg" alt="Clues by Sam Level {level} answer thumbnail" loading="lazy" width="320" height="180">\n'
        f'        <h3>{format_title(date_text, html=True)}</h3>\n'
        f'        <p class="small">{date_text}</p>\n'
        f'        <a class="btn btn-secondary" href="/level/{level}/">Open guide</a>\n'
        "      </div>"
    )


def replace_cards_block(text: str, data_attr: str, replacement: str) -> str:
    pattern = re.compile(
        rf'(<div class="cards" {re.escape(data_attr)}>\n)(.*?)(\n\s*</div>\n\s*</div>\n\s*</section>)',
        re.S,
    )
    updated, count = pattern.subn(rf"\1{replacement}\3", text, count=1)
    if count != 1:
        raise ValueError(f"Unable to replace cards block for {data_attr}")
    return updated


def render_related_links(level: int, max_level: int) -> str:
    start = max(1, level - 6)
    end = min(max_level, level + 1)
    return "".join(f'<a href="/level/{num}/">{num}</a>' for num in range(start, end + 1))


def render_level_page(level: int, video_id: str, date_text: str, max_level: int) -> str:
    intro = INTRO_LINES[level % len(INTRO_LINES)].format(level=level, date=date_text)
    brief = BRIEF_LINES[level % len(BRIEF_LINES)]
    focus = FOCUS_LINES[level % len(FOCUS_LINES)]
    mistake = MISTAKE_LINES[level % len(MISTAKE_LINES)]
    notes = NOTE_LINES[level % len(NOTE_LINES)]
    related = render_related_links(level, max_level)
    title_html = format_title(date_text, html=True)
    title_attr = format_title(date_text, html=False)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://i.ytimg.com">
  <link rel="preconnect" href="https://www.youtube-nocookie.com">
  <title>{title_html}</title>
  <meta name="description" content="Find the Clues by Sam level {level} answer for the {date_text} puzzle, including the video walkthrough, archive links, and quick solve notes.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://cluesbysam.net/level/{level}/">
  <link rel="stylesheet" href="/assets/css/style.css">
  <link rel="icon" type="image/png" href="/assets/images/favicon.png">
  <link rel="icon" href="/assets/images/favicon.ico">
</head>
<body class="level-page">
<header>
  <div class="container navbar">
    <a class="brand" href="/index.html"><span>Clues by Sam Guide</span></a>
    <nav class="nav-links">
      <a href="/index.html">Home</a>
      <a href="/levels.html">Levels</a>
      <a href="/game.html">Play Online</a>
      <a href="/blog.html">Blog</a>
      <a href="/contact.html">Contact</a>
    </nav>
    <div class="nav-actions">
      <input type="number" min="1" max="{max_level}" placeholder="Jump to level" data-nav-jump-input>
      <button data-nav-jump-btn>Go</button>
      <button data-nav-toggle style="background:#fff;color:var(--ink);border:1px solid #cbe7e2;">Menu</button>
    </div>
  </div>
</header>

<main>
  <section class="hero">
    <div class="container">
      <span class="badge">Level {level}</span>
      <h1>{title_html}</h1>
      <p>{intro}</p>
      <p class="small level-brief">{brief}</p>
      <div class="nav-actions">
        <input type="number" min="1" max="{max_level}" placeholder="Jump to level" data-nav-jump-input>
        <button data-nav-jump-btn>Go</button>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="container split">
      <div>
        <div class="level-photo"><img src="https://img.youtube.com/vi/{video_id}/hqdefault.jpg" alt="Clues by Sam level {level} answer preview"></div>
        <div class="video-frame" data-video-id="{video_id}" data-title="{title_attr}"></div>
        <div class="share-box">
          <h3>Share This Level Guide</h3>
          <p>Help other players by sharing this walkthrough guide.</p>
          <div class="share-actions">
            <button type="button" class="share-btn share-facebook" data-share="facebook">Facebook</button>
            <button type="button" class="share-btn share-twitter" data-share="twitter">Twitter</button>
            <button type="button" class="share-btn share-reddit" data-share="reddit">Reddit</button>
            <button type="button" class="share-btn share-whatsapp" data-share="whatsapp">WhatsApp</button>
            <button type="button" class="share-btn share-copy" data-share="copy">Copy Link</button>
          </div>
        </div>
        <div class="level-nav"></div>
      </div>
      <div>
        <div class="related-levels">
          <h3>Nearby levels</h3>
          <div class="related-grid">
          {related}
          </div>
        </div>
        <div class="card">
          <span class="badge">Puzzle date</span>
          <p class="small">{date_text}</p>
          <span class="badge">Best first check</span>
          <p class="small solve-focus">{focus}</p>
          <span class="badge">Common mistake</span>
          <p class="small solve-mistake">{mistake}</p>
          <span class="badge">Quick plan</span>
          <p>Need the Clues by Sam answer for level {level}? Use the {date_text} video walkthrough below, then check nearby levels if you are catching up on the archive.</p>
          <ul>
            <li>Every clue is honest; chain deductions safely.</li>
            <li>Neighbors include diagonals; count up to eight.</li>
            <li>Mark proven innocents to unlock more clues.</li>
            <li>Use color tags to track hypotheses.</li>
          </ul>
          <a class="btn btn-secondary" href="https://www.youtube.com/watch?v={video_id}" target="_blank" rel="noopener">Watch on YouTube</a>
        </div>
        <div class="card solve-notes">
          <span class="badge">Solve notes</span>
          <p>{notes}</p>
          <p class="small">If a clue becomes fully satisfied, mark every remaining touching square as safe immediately.</p>
        </div>
      </div>
    </div>
  </section>
  <div class="notice-box">
    <h3>Version Differences 更新提示</h3>
    <p>Clues by Sam levels get tuned occasionally, so layouts or solutions may change between app updates. If this guide doesn't match perfectly, use the screenshot and video above to adjust.</p>
    <p>Clues by Sam 关卡有时会调整，不同版本可能导致布局或解法略有差异。如发现与当前关卡不完全一致，请参考上方图片与视频自行微调。</p>
  </div>
</main>
<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div><strong>{{brand}}</strong><p class="small">Fan-made logic walkthroughs and video solutions.</p></div>
      <div><strong>Quick Links</strong><p><a href="/levels.html">All Levels</a><br><a href="/game.html">Play Online</a><br><a href="/blog.html">Blog</a></p></div>
      <div><strong>Legal</strong><p><a href="/privacy.html">Privacy</a><br><a href="/terms-of-service.html">Terms</a></p></div>
    </div>
    <p class="small">Not affiliated with the official game. Copyright <span data-year></span> CluesBySam.net</p>
  </div>
</footer>
<script src="/assets/js/playlist-data.js" defer></script>
<script src="/assets/js/levels.js" defer></script>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def update_index_html(entries: list[dict], max_level: int) -> None:
    text = INDEX_HTML.read_text()
    latest = entries[0]
    latest_date = extract_date_for_entry(latest)
    latest_title_html = format_title(latest_date, html=True)
    latest_title_attr = format_title(latest_date, html=False)
    text = text.replace('max="212"', f'max="{max_level}"')
    text = text.replace("1-212", f"1-{max_level}")
    text = re.sub(r"📅 \d+\+ Daily Levels", f"📅 {max_level}+ Daily Levels", text)
    text = re.sub(
        r"<h2 style=\"margin:0 0 0.5rem;\">.*?</h2>",
        f"<h2 style=\"margin:0 0 0.5rem;\">{latest_title_html}</h2>",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'<div class="video-frame" style="min-height:280px;" data-video-id="[^"]+" data-title="[^"]+" data-priority="high">',
        f'<div class="video-frame" style="min-height:280px;" data-video-id="{latest["videoId"]}" data-title="{latest_title_attr}" data-priority="high">',
        text,
        count=1,
    )
    text = re.sub(
        r'<img src="https://i\.ytimg\.com/vi_webp/[^/]+/hqdefault\.webp" alt="Clues by Sam Level \d+ answer thumbnail"',
        f'<img src="https://i.ytimg.com/vi_webp/{latest["videoId"]}/hqdefault.webp" alt="Clues by Sam Level {latest["level"]} answer thumbnail"',
        text,
        count=1,
    )
    text = re.sub(
        r'<a class="btn btn-secondary" href="/level/\d+/">Open latest answer</a>',
        f'<a class="btn btn-secondary" href="/level/{latest["level"]}/">Open latest answer</a>',
        text,
        count=1,
    )
    home_cards = "\n".join(
        build_card(entry["level"], entry["videoId"], extract_date_for_entry(entry), "mqdefault")
        for entry in entries[:6]
    )
    text = replace_cards_block(text, 'data-home-grid', home_cards + "\n")
    INDEX_HTML.write_text(text)


def update_levels_html(entries: list[dict], max_level: int) -> None:
    text = LEVELS_HTML.read_text()
    text = text.replace('max="212"', f'max="{max_level}"')
    text = text.replace("1-212", f"1-{max_level}")
    text = re.sub(
        r'<a class="archive-jump" href="/level/\d+/"><strong>Latest 30</strong><span>.*?</span></a>',
        f'<a class="archive-jump" href="/level/{max_level}/"><strong>Latest 30</strong><span>Levels {max(1, max_level - 29)}-{max_level} with the newest answers and walkthroughs.</span></a>',
        text,
        count=1,
    )
    text = re.sub(
        r'<a class="archive-jump" href="/level/206/"><strong>April 2026</strong><span>.*?</span></a>',
        f'<a class="archive-jump" href="/level/206/"><strong>April 2026</strong><span>Levels 206-{max_level} covering 1st-{extract_date(entries[0]["title"]).split()[0]} April 2026.</span></a>',
        text,
        count=1,
    )
    level_cards = "\n".join(
        build_card(entry["level"], entry["videoId"], extract_date_for_entry(entry), "hqdefault")
        for entry in entries[:30]
    )
    text = replace_cards_block(text, 'data-level-grid', level_cards + "\n")
    LEVELS_HTML.write_text(text)


def refresh_level_page_titles(entries: list[dict]) -> None:
    for entry in entries:
        level = entry["level"]
        date_text = extract_date_for_entry(entry)
        title_html = format_title(date_text, html=True)
        title_attr = format_title(date_text, html=False)
        page = ROOT / "level" / str(level) / "index.html"
        if not page.exists():
            continue
        text = page.read_text()
        text = re.sub(r"<title>.*?</title>", f"<title>{title_html}</title>", text, count=1, flags=re.S)
        text = re.sub(r"<h1>.*?</h1>", f"<h1>{title_html}</h1>", text, count=1, flags=re.S)
        text = re.sub(
            r'(<div class="video-frame"[^>]*data-video-id="[^"]+"\s+data-title=")[^"]+("></div>)',
            rf"\1{title_attr}\2",
            text,
            count=1,
        )
        page.write_text(text)


def update_sitemap(entries: list[dict], new_entries: list[dict]) -> None:
    text = SITEMAP_XML.read_text()
    latest_iso = date_to_iso(extract_date_for_entry(entries[0]))
    text = re.sub(
        r"(<url><loc>https://cluesbysam\.net/</loc><lastmod>)([^<]+)(</lastmod></url>)",
        rf"\g<1>{latest_iso}\g<3>",
        text,
        count=1,
    )
    text = re.sub(
        r"(<url><loc>https://cluesbysam\.net/levels\.html</loc><lastmod>)([^<]+)(</lastmod></url>)",
        rf"\g<1>{latest_iso}\g<3>",
        text,
        count=1,
    )
    text = re.sub(
        r"(<url><loc>https://cluesbysam\.net/game\.html</loc><lastmod>)([^<]+)(</lastmod></url>)",
        rf"\g<1>{latest_iso}\g<3>",
        text,
        count=1,
    )
    new_urls = "\n".join(
        f'  <url><loc>https://cluesbysam.net/level/{entry["level"]}/</loc><lastmod>{date_to_iso(extract_date_for_entry(entry))}</lastmod></url>'
        for entry in sorted(new_entries, key=lambda item: item["level"])
    )
    text = text.replace("\n</urlset>\n", f"\n{new_urls}\n</urlset>\n")
    SITEMAP_XML.write_text(text)


def update_html_max_values(max_level: int) -> None:
    for pattern in MAX_HTML_GLOBS:
        for path in ROOT.glob(pattern):
            text = path.read_text()
            updated = text.replace('max="212"', f'max="{max_level}"').replace("1-212", f"1-{max_level}")
            if updated != text:
                path.write_text(updated)


def write_level_pages(new_entries: list[dict], max_level: int) -> None:
    for entry in new_entries:
        level_dir = ROOT / "level" / str(entry["level"])
        level_dir.mkdir(parents=True, exist_ok=True)
        page = render_level_page(entry["level"], entry["videoId"], extract_date(entry["title"]), max_level)
        (level_dir / "index.html").write_text(page)


def main() -> None:
    args = parse_args()
    playlist_items = parse_playlist_ini(Path(args.playlist_ini))
    if not playlist_items:
        raise SystemExit("No playlist items parsed from playlist.ini")

    existing = load_playlist_data()
    latest_existing_video = existing[0]["videoId"]
    prefix: list[tuple[str, str]] = []
    for video_id, title in playlist_items:
        if video_id == latest_existing_video:
            break
        prefix.append((video_id, title))
    new_entries: list[dict] = []
    entries = existing
    if prefix:
        max_existing_level = max(item["level"] for item in existing)
        for offset, (video_id, title) in enumerate(prefix):
            level = max_existing_level + len(prefix) - offset
            new_entries.append(build_entry(level, video_id, title))
        entries = new_entries + existing
        write_playlist_data(entries)

    max_level = entries[0]["level"]
    if new_entries:
        write_level_pages(sorted(new_entries, key=lambda item: item["level"]), max_level)
    update_html_max_values(max_level)
    update_index_html(entries, max_level)
    update_levels_html(entries, max_level)
    refresh_level_page_titles(entries)
    if new_entries:
        update_sitemap(entries, new_entries)
        print(f"Added levels {min(item['level'] for item in new_entries)}-{max_level}")
    else:
        print("No new levels found. Refreshed title text.")


if __name__ == "__main__":
    main()
