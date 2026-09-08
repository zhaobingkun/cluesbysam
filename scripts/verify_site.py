#!/usr/bin/env python3
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_HOST = "cluesbysam.net"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonicals: list[str] = []
        self.hrefs: list[str] = []
        self.noindex = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")
        if tag == "link" and values.get("rel") == "canonical" and values.get("href"):
            self.canonicals.append(values["href"] or "")
        if tag == "meta" and values.get("name") == "robots":
            self.noindex = "noindex" in (values.get("content") or "").lower()


def local_target(url: str) -> Path | None:
    parsed = urlsplit(url)
    if parsed.scheme in {"mailto", "tel", "javascript", "data"}:
        return None
    if parsed.netloc and parsed.netloc != PUBLIC_HOST:
        return None
    path = unquote(parsed.path)
    if not path or path == "/":
        return ROOT / "index.html"
    candidate = ROOT / path.lstrip("/")
    if path.endswith("/"):
        return candidate / "index.html"
    return candidate


def main() -> int:
    errors: list[str] = []
    html_files = sorted(ROOT.glob("*.html")) + sorted((ROOT / "level").glob("*/index.html")) + sorted((ROOT / "blog").glob("*.html"))
    canonical_owners: dict[str, Path] = {}

    for page in html_files:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        if page.name != "404.html" and not parser.noindex:
            if len(parser.canonicals) != 1:
                errors.append(f"{page.relative_to(ROOT)}: expected one canonical, found {len(parser.canonicals)}")
            elif parser.canonicals[0] in canonical_owners:
                owner = canonical_owners[parser.canonicals[0]].relative_to(ROOT)
                errors.append(f"{page.relative_to(ROOT)}: duplicate canonical also used by {owner}")
            else:
                canonical_owners[parser.canonicals[0]] = page
        for href in parser.hrefs:
            target = local_target(href)
            if target is not None and not target.exists():
                errors.append(f"{page.relative_to(ROOT)}: broken internal link {href}")

    sitemap = ElementTree.parse(ROOT / "sitemap.xml")
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = [node.text or "" for node in sitemap.findall("sm:url/sm:loc", namespace)]
    for url in sitemap_urls:
        target = local_target(url)
        if target is None or not target.exists():
            errors.append(f"sitemap.xml: missing local target for {url}")

    four_oh_four = PageParser()
    four_oh_four.feed((ROOT / "404.html").read_text(encoding="utf-8"))
    if not four_oh_four.noindex:
        errors.append("404.html: missing noindex")

    if errors:
        print("Site verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Site verification passed: {len(html_files)} HTML files, {len(sitemap_urls)} sitemap URLs, no broken internal links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
