"""Regression checks for the independent play/help entry page."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class GameRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / 'game.html').read_text()
        cls.page = Page(cls.source)

    def test_existing_metadata_and_index_policy_preserved(self):
        self.assertIn('<title>Play Clues by Sam Online</title>', self.source)
        for tag, attrs in self.page.tags:
            if tag == 'meta' and attrs.get('name') == 'robots':
                self.assertEqual(attrs['content'], 'index, follow')
        canonicals = [a['href'] for t, a in self.page.tags if t == 'link' and a.get('rel') == 'canonical']
        self.assertEqual(canonicals, ['https://cluesbysam.net/game.html'])
        self.assertIn('data-adsense="off"', self.source)
        self.assertEqual(sum(t == 'h1' for t, _ in self.page.tags), 1)

    def test_no_game_embed_or_affiliation_claim(self):
        self.assertNotIn('<iframe', self.source)
        self.assertIn('does not host the game', self.source)
        self.assertIn('not affiliated with the official game', self.source)
        self.assertIn('not playable copies', self.source)

    def test_official_action_is_safe_and_primary(self):
        links = [a for t, a in self.page.tags if t == 'a' and 'btn' in a.get('class', '').split()]
        self.assertEqual(links[0]['href'], 'https://cluesbysam.com/')
        self.assertEqual(links[0]['target'], '_blank')
        self.assertIn('noopener', links[0]['rel'].split())
        self.assertEqual(links[1]['href'], '/')

    def test_contextual_help_links_are_static_and_exist(self):
        targets = ['/levels.html', '/blog/neighbor-logic.html', '/blog/color-tags.html']
        links = [a['href'] for t, a in self.page.tags if t == 'a']
        for target in targets:
            self.assertIn(target, links)
            self.assertTrue((ROOT / target.lstrip('/')).is_file())
        self.assertIn('Walkthroughs contain spoilers', self.source)

    def test_schema_and_styles_remain_page_scoped(self):
        import re
        schemas = re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', self.source, re.S)
        self.assertEqual(len(schemas), 1)
        graph = json.loads(schemas[0])['@graph']
        self.assertEqual(graph[1]['url'], 'https://cluesbysam.net/game.html')
        self.assertIn('.play-page .hero-player .official-play-card { height: auto; min-height: 0; }', self.source)
        self.assertIn('aria-labelledby="play-help-heading"', self.source)
        self.assertIn('id="play-help-heading"', self.source)


if __name__ == '__main__':
    unittest.main()
