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
MAX_HTML_GLOBS = ["*.html", "blog/*.html", "level/*/index.html"]

MONTHS = {
    "January": 1,
    "Jan": 1,
    "February": 2,
    "Feb": 2,
    "March": 3,
    "Mar": 3,
    "April": 4,
    "Apr": 4,
    "May": 5,
    "June": 6,
    "Jun": 6,
    "July": 7,
    "Jul": 7,
    "August": 8,
    "Aug": 8,
    "September": 9,
    "Sep": 9,
    "October": 10,
    "Oct": 10,
    "November": 11,
    "Nov": 11,
    "December": 12,
    "Dec": 12,
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
    "Need the Clues by Sam answer for {date}? This page covers the daily board with a direct walkthrough and quick archive links for nearby puzzles.",
    "Use this Clues by Sam answer page for {date}. The video walkthrough below covers the daily puzzle and links back to the full archive.",
    "This Clues by Sam guide collects the {date} answer, the video walkthrough, and nearby dates so you can keep moving through the archive.",
]

BRIEF_LINES = [
    "Stuck on this Clues by Sam puzzle? Use the first two confirmed innocents to narrow the criminal chain, then compare every touching square before committing a guess.",
    "Stuck on this Clues by Sam puzzle? Start by marking any clue that forces a row or column split, then verify all diagonal neighbors before locking criminals.",
    "Stuck on this Clues by Sam puzzle? Clear the most restricted clue zone first, then use the newly safe tiles to unlock the next deduction.",
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


def date_to_datetime(date_text: str) -> datetime:
    day_text, month_name, year_text = date_text.split()
    day = int(re.sub(r"(st|nd|rd|th)$", "", day_text))
    month = MONTHS[month_name]
    year = int(year_text)
    return datetime(year, month, day)


def build_existing_keys(entries: list[dict]) -> tuple[set[str], set[str]]:
    existing_video_ids: set[str] = set()
    existing_dates: set[str] = set()
    for entry in entries:
        video_id = str(entry.get("videoId", "")).strip()
        if video_id:
            existing_video_ids.add(video_id)
        try:
            existing_dates.add(extract_date_for_entry(entry))
        except ValueError:
            continue
    return existing_video_ids, existing_dates


def merge_entries_by_date(existing: list[dict], new_entries: list[dict]) -> list[dict]:
    merged = list(existing)
    ordered_new = sorted(new_entries, key=lambda item: date_to_datetime(extract_date(item["title"])), reverse=True)
    for new_entry in ordered_new:
        new_date = date_to_datetime(extract_date(new_entry["title"]))
        insert_at = len(merged)
        for idx, entry in enumerate(merged):
            try:
                current_date = date_to_datetime(extract_date_for_entry(entry))
            except ValueError:
                insert_at = idx
                break
            if current_date < new_date:
                insert_at = idx
                break
        merged.insert(insert_at, new_entry)
    return merged


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
        f'        <span class="badge">{date_text}</span>\n'
        f'        <img class="card-thumb" src="https://img.youtube.com/vi/{video_id}/{image_kind}.jpg" alt="Clues by Sam {date_text} answer thumbnail" loading="lazy" width="320" height="180">\n'
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


def build_entry_by_level(entries: list[dict]) -> dict[int, dict]:
    return {int(entry["level"]): entry for entry in entries if "level" in entry}


def build_dated_entries(entries: list[dict]) -> list[dict]:
    dated_entries = []
    for entry in entries:
        try:
            date_text = extract_date_for_entry(entry)
            date_value = date_to_datetime(date_text)
        except (KeyError, ValueError):
            continue
        dated_entries.append(entry | {"dateText": date_text, "dateValue": date_value})
    return sorted(dated_entries, key=lambda item: item["dateValue"])


def render_related_links(level: int, dated_entries: list[dict]) -> str:
    current_index = next(
        (idx for idx, entry in enumerate(dated_entries) if int(entry["level"]) == int(level)),
        None,
    )
    if current_index is None:
        return ""
    start = max(0, current_index - 6)
    end = min(len(dated_entries), current_index + 2)
    links = []
    for entry in dated_entries[start:end]:
        num = int(entry["level"])
        label = entry["dateText"]
        links.append(f'<a href="/level/{num}/">{label}</a>')
    return "".join(links)


def render_level_page(
    level: int,
    video_id: str,
    date_text: str,
    max_level: int,
    dated_entries: list[dict],
) -> str:
    intro = INTRO_LINES[level % len(INTRO_LINES)].format(level=level, date=date_text)
    brief = BRIEF_LINES[level % len(BRIEF_LINES)]
    focus = FOCUS_LINES[level % len(FOCUS_LINES)]
    mistake = MISTAKE_LINES[level % len(MISTAKE_LINES)]
    notes = NOTE_LINES[level % len(NOTE_LINES)]
    related = render_related_links(level, dated_entries)
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
  <meta name="description" content="Find the Clues by Sam answer for the {date_text} puzzle, including the video walkthrough, archive links, and quick solve notes.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://cluesbysam.net/level/{level}/">
  <link rel="stylesheet" href="/assets/css/style.css">
  <link rel="icon" type="image/png" href="/assets/images/favicon.png">
  <link rel="icon" href="/assets/images/favicon.ico">
  <script>
    window.addEventListener('load', function () {{
      var userAgent = navigator.userAgent || '';
      var isAndroidWebView = /Android/i.test(userAgent) &&
        (userAgent.indexOf('; wv)') !== -1 ||
         userAgent.indexOf(' wv)') !== -1 ||
         (userAgent.indexOf('Version/4.0') !== -1 && userAgent.indexOf('Chrome/') !== -1));
      var adsDisabled = document.body && document.body.dataset.adsense === 'off';
      if (isAndroidWebView || adsDisabled) return;

      var loaded = false;
      function loadAds() {{
        if (loaded) return;
        loaded = true;
        var script = document.createElement('script');
        script.async = true;
        script.crossOrigin = 'anonymous';
        script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6428701926694635';
        document.head.appendChild(script);
      }}

      var timer = window.setTimeout(loadAds, 8000);
      ['scroll', 'pointerdown', 'keydown'].forEach(function (eventName) {{
        window.addEventListener(eventName, function () {{
          window.clearTimeout(timer);
          loadAds();
        }}, {{ once: true, passive: true }});
      }});
    }});
  </script>
</head>
<body class="level-page">
<header>
  <div class="container navbar">
    <a class="brand" href="/"><span>Clues by Sam Guide</span></a>
    <nav class="nav-links">
      <a href="/">Home</a>
      <a href="/levels.html">Levels</a>
      <a href="/game.html">Play Online</a>
      <a href="/blog.html">Blog</a>
      <a href="/contact.html">Contact</a>
    </nav>
    <div class="nav-actions">
      <input type="number" min="1" max="{max_level}" placeholder="Jump to archive" data-nav-jump-input>
      <button data-nav-jump-btn>Go</button>
      <button data-nav-toggle style="background:#fff;color:var(--ink);border:1px solid #cbe7e2;">Menu</button>
    </div>
  </div>
</header>

<main>
  <section class="hero">
    <div class="container">
      <span class="badge">{date_text}</span>
      <h1>{title_html}</h1>
      <p>{intro}</p>
      <p class="small level-brief">{brief}</p>
      <div class="nav-actions">
        <input type="number" min="1" max="{max_level}" placeholder="Jump to archive" data-nav-jump-input>
        <button data-nav-jump-btn>Go</button>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="container split">
      <div>
        <div class="level-photo"><img src="https://img.youtube.com/vi/{video_id}/hqdefault.jpg" alt="Clues by Sam {date_text} answer preview"></div>
        <div class="video-frame" data-video-id="{video_id}" data-title="{title_attr}"></div>
        <div class="share-box">
          <h3>Share This Daily Guide</h3>
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
          <h3>Nearby dates</h3>
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
          <p>Need the Clues by Sam answer for {date_text}? Use the video walkthrough below, then check nearby dates if you are catching up on the archive.</p>
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
    <p>Clues by Sam daily puzzles get tuned occasionally, so layouts or solutions may change between app updates. If this guide doesn't match perfectly, use the screenshot and video above to adjust.</p>
    <p>Clues by Sam 关卡有时会调整，不同版本可能导致布局或解法略有差异。如发现与当前关卡不完全一致，请参考上方图片与视频自行微调。</p>
  </div>
</main>
<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div><strong>Clues by Sam Guide</strong><p class="small">Fan-made logic walkthroughs and video solutions.</p></div>
      <div><strong>Quick Links</strong><p><a href="/levels.html">All Dates</a><br><a href="/game.html">Play Online</a><br><a href="/blog.html">Blog</a></p></div>
      <div><strong>Legal</strong><p><a href="/privacy.html">Privacy</a><br><a href="/terms-of-service.html">Terms</a></p></div>
    </div>
    <p class="small">Not affiliated with the official game. Copyright <span data-year></span> CluesBySam.net</p>
  </div>
</footer>
<script src="/assets/js/playlist-data.js?v=dates-20260603" defer></script>
<script src="/assets/js/levels.js?v=dates-20260603" defer></script>
<script src="/assets/js/site.js?v=dates-20260603" defer></script>
</body>
</html>
"""


def update_index_html(entries: list[dict], max_level: int) -> None:
    text = INDEX_HTML.read_text()
    dated_entries = build_dated_entries(entries)
    if not dated_entries:
        raise ValueError("Unable to find dated entries for homepage update")
    latest = max(dated_entries, key=lambda entry: entry["dateValue"])
    latest_date = latest["dateText"]
    latest_title_html = format_title(latest_date, html=True)
    latest_title_attr = format_title(latest_date, html=False)
    text = re.sub(r'max="\d+"', f'max="{max_level}"', text)
    text = re.sub(r"1-\d+", f"1-{max_level}", text)
    text = re.sub(r"📅 \d+\+ Daily (?:Levels|Guides)", f"📅 {max_level}+ Daily Guides", text)
    text = re.sub(
        r'(<div class="card home-play-latest answer-video-card">.*?<h2>).*?(</h2>)',
        rf"\g<1>{latest_title_html}\g<2>",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'(<div class="video-frame\b[^>]*data-video-id=")[^"]+(" data-title=")[^"]+(" data-priority="high")',
        rf"\g<1>{latest['videoId']}\g<2>{latest_title_attr}\g<3>",
        text,
        count=1,
    )
    text = re.sub(
        r'(<img src="https://i\.ytimg\.com/vi_webp/)[^/]+(/hqdefault\.webp" alt="Clues by Sam )[^" ]+(?: [^" ]+)*( answer thumbnail")',
        rf"\g<1>{latest['videoId']}\g<2>{latest_date}\g<3>",
        text,
        count=1,
    )
    text = re.sub(
        r'(<a class="btn btn-secondary" href=")/level/\d+(/">Open today&apos;s answer</a>)',
        rf'\1/level/{latest["level"]}\2',
        text,
        count=1,
    )
    text = re.sub(
        r'(<a class="btn" href=")/level/\d+(/">Open today&apos;s answer</a>)',
        rf'\1/level/{latest["level"]}\2',
        text,
        count=1,
    )
    text = re.sub(
        r'(<a class="btn btn-secondary" href=")/level/\d+(/">Read today&apos;s guide</a>)',
        rf'\1/level/{latest["level"]}\2',
        text,
        count=1,
    )
    text = re.sub(
        r'(<a href=")/level/\d+(/">Latest answer page</a>)',
        rf'\1/level/{latest["level"]}\2',
        text,
        count=1,
    )
    home_cards = "\n".join(
        build_card(entry["level"], entry["videoId"], extract_date_for_entry(entry), "mqdefault")
        for entry in sorted(dated_entries, key=lambda entry: entry["dateValue"], reverse=True)[:6]
    )
    text = replace_cards_block(text, 'data-home-grid', home_cards + "\n")
    INDEX_HTML.write_text(text)


def update_levels_html(entries: list[dict], max_level: int) -> None:
    text = LEVELS_HTML.read_text()
    text = re.sub(r'max="\d+"', f'max="{max_level}"', text)
    text = re.sub(r"1-\d+", f"1-{max_level}", text)

    month_groups: list[tuple[str, list[int]]] = []
    seen_months: dict[str, list[int]] = {}
    for entry in entries:
        try:
            date_text = extract_date_for_entry(entry)
        except ValueError:
            continue
        parts = date_text.split()
        if len(parts) < 3:
            continue
        month_name, year_text = parts[-2], parts[-1]
        if month_name not in MONTHS or not year_text.isdigit():
            continue
        key = f"{month_name} {year_text}"
        if key not in seen_months:
            seen_months[key] = []
            month_groups.append((key, seen_months[key]))
        seen_months[key].append(entry["level"])

    jumps = [
        f'<a class="archive-jump" href="/level/{max_level}/"><strong>Latest answers</strong><span>The newest date-based Clues by Sam answers and walkthroughs.</span></a>'
    ]
    recent_groups = month_groups[:5]
    for label, levels in recent_groups:
        month_max = max(levels)
        jumps.append(
            f'<a class="archive-jump" href="/level/{month_max}/"><strong>{label}</strong><span>Daily answer guides from the {label} puzzle run.</span></a>'
        )
    older_2025 = []
    for entry in entries:
        try:
            date_text = extract_date_for_entry(entry)
        except ValueError:
            continue
        if date_text.endswith("2025"):
            older_2025.append(entry["level"])
    if older_2025:
        jumps.append(
            f'<a class="archive-jump" href="/level/{max(older_2025)}/"><strong>2025 Archive</strong><span>Date-based answer guides from September to December 2025.</span></a>'
        )
    archive_jump_html = "\n        ".join(jumps)
    archive_pattern = re.compile(r'(<div class="archive-jumps">\n)(.*?)(\n\s*</div>)', re.S)
    text = archive_pattern.sub(
        lambda match: match.group(1) + "        " + archive_jump_html + match.group(3),
        text,
        count=1,
    )
    level_cards = "\n".join(
        build_card(entry["level"], entry["videoId"], extract_date_for_entry(entry), "hqdefault")
        for entry in entries[:30]
    )
    text = replace_cards_block(text, 'data-level-grid', level_cards + "\n")
    LEVELS_HTML.write_text(text)


def refresh_level_pages(entries: list[dict], max_level: int) -> None:
    dated_entries = build_dated_entries(entries)
    for entry in entries:
        level = entry["level"]
        date_text = extract_date_for_entry(entry)
        try:
            date_to_datetime(date_text)
        except (KeyError, ValueError):
            continue
        page = ROOT / "level" / str(level) / "index.html"
        if not page.exists():
            continue
        page.write_text(render_level_page(level, entry["videoId"], date_text, max_level, dated_entries))


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
            updated = re.sub(r'max="\d+"', f'max="{max_level}"', text)
            updated = re.sub(r"1-\d+", f"1-{max_level}", updated)
            if updated != text:
                path.write_text(updated)


def write_level_pages(new_entries: list[dict], max_level: int, dated_entries: list[dict]) -> None:
    for entry in new_entries:
        level_dir = ROOT / "level" / str(entry["level"])
        level_dir.mkdir(parents=True, exist_ok=True)
        page = render_level_page(entry["level"], entry["videoId"], extract_date(entry["title"]), max_level, dated_entries)
        (level_dir / "index.html").write_text(page)


def main() -> None:
    args = parse_args()
    playlist_items = parse_playlist_ini(Path(args.playlist_ini))
    if not playlist_items:
        raise SystemExit("No playlist items parsed from playlist.ini")

    existing = load_playlist_data()
    existing_video_ids, existing_dates = build_existing_keys(existing)
    missing_items: list[tuple[str, str, str]] = []
    seen_video_ids: set[str] = set()
    seen_dates: set[str] = set()
    for video_id, title in playlist_items:
        if video_id in existing_video_ids or video_id in seen_video_ids:
            continue
        try:
            date_text = extract_date(title)
        except ValueError:
            continue
        if date_text in existing_dates or date_text in seen_dates:
            continue
        seen_video_ids.add(video_id)
        seen_dates.add(date_text)
        missing_items.append((video_id, title, date_text))
    new_entries: list[dict] = []
    entries = existing
    if missing_items:
        max_existing_level = max(item["level"] for item in existing)
        ordered_missing = sorted(missing_items, key=lambda item: date_to_datetime(item[2]))
        for offset, (video_id, title, _date_text) in enumerate(ordered_missing, start=1):
            level = max_existing_level + offset
            new_entries.append(build_entry(level, video_id, title))
        entries = merge_entries_by_date(existing, new_entries)
        write_playlist_data(entries)

    max_level = max(item["level"] for item in entries)
    dated_entries = build_dated_entries(entries)
    if new_entries:
        write_level_pages(sorted(new_entries, key=lambda item: item["level"]), max_level, dated_entries)
    update_html_max_values(max_level)
    update_index_html(entries, max_level)
    update_levels_html(entries, max_level)
    refresh_level_pages(entries, max_level)
    if new_entries:
        update_sitemap(entries, new_entries)
        print(
            "Added levels "
            f"{min(item['level'] for item in new_entries)}-{max(item['level'] for item in new_entries)}"
        )
    else:
        print("No new levels found. Refreshed title text.")


if __name__ == "__main__":
    main()
