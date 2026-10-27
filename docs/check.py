#!/usr/bin/env python3
"""Check the built site without third-party dependencies or network access."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re

SITE = Path(__file__).resolve().parent.parent / 'www'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.headings = 0
        self.current = 0
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate id: {attrs["id"]}'
            self.ids.add(attrs['id'])
        self.headings += tag == 'h1'
        self.current += attrs.get('aria-current') == 'page'
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])


pages = {path: Page(path) for path in SITE.rglob('*.html')}
assert pages, 'Build the site first: ruby docs/build.rb'
sources = list(Path(__file__).parent.glob('*.adoc'))
for source in sources:
    page = pages[SITE / source.with_suffix('.html').name]
    assert page.headings == 1, f'{source.name}: expected one page heading'
    assert page.current == 1, f'{source.name}: expected one active navigation link'
    for prefix in ('modules', 'modules/master'):
        redirect = SITE / prefix / source.with_suffix('.html').name
        assert redirect in pages, f'Missing legacy redirect: {redirect}'
        assert 'location.hash' in redirect.read_text(), 'Redirect must preserve sections'

for path, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        assert not url.path.startswith('/'), f'{path.name}: root-relative URL breaks project Pages: {link}'
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        assert target.is_relative_to(SITE), f'Link escapes site: {link}'
        assert target.is_file(), f'{path.name}: missing target {link}'
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, f'{path.name}: missing section {link}'
    assert not re.search(r'\{(?:lab_name|workshop_repo_url)\}', path.read_text()), f'{path}: unresolved attribute'

for css in (SITE / 'assets').glob('*.css'):
    for link in re.findall(r'url\(([^)]+)\)', css.read_text()):
        link = link.strip('"\'')
        if not urlsplit(link).scheme:
            assert (css.parent / link).is_file(), f'Missing CSS asset: {link}'

# This allowlist catches accidental publication of credentials or repository files.
allowed = {p.relative_to(SITE) for p in pages} | {Path('.nojekyll')}
allowed |= {Path('assets') / p.name for p in (Path(__file__).parent / 'assets').iterdir() if p.is_file()}
actual = {p.relative_to(SITE) for p in SITE.rglob('*') if p.is_file()}
assert actual == allowed, f'Unexpected or missing published files: {actual ^ allowed}'
print(f'Checked {len(sources)} lab pages, {len(pages) - len(sources)} legacy redirects, all local links, sections, and assets.')
