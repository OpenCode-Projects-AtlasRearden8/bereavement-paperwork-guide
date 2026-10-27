"""Tests for the Bereavement Paperwork Guide build.

Run:  python3 -m unittest discover -s tests -v
"""

import http.client
import csv
import re
import shutil
import socket
import socketserver
import tempfile
import threading
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys_path = str(ROOT)

import sys  # noqa: E402

if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

import build  # noqa: E402

DOCS = ROOT / "docs"
SLUGS = [s for s, _ in build.PAGES]


def _fake_site_root() -> tuple:
    tmp = Path(tempfile.mkdtemp(prefix="bpg-test-"))
    shutil.copytree(ROOT / "worksheets", tmp / "worksheets")
    return tmp, tmp / "site"


def _restore_build_site(site_dir: Path, rc: int) -> None:
    real = build.SITE
    build.SITE = site_dir
    try:
        rc = build.build()
    finally:
        build.SITE = real
    assert rc == 0


# ---------------------------------------------------------------- helpers

class TagBalanceParser(HTMLParser):
    """Checks that every opened tag is closed (void elements excepted)."""

    VOID = {"meta", "br", "hr", "img", "input", "link", "col"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack:
            self.errors.append(f"unexpected </{tag}> at {self.getpos()}")
            return
        open_tag, pos = self.stack.pop()
        if open_tag != tag:
            self.errors.append(
                f"mismatch: <{open_tag}> opened at {pos} closed by </{tag}> "
                f"at {self.getpos()}"
            )


def doc_text(slug: str) -> str:
    return (DOCS / f"{slug}.md").read_text(encoding="utf-8")


def headings_of(md: str, level: int = 2):
    for line in md.split("\n"):
        m = re.match(r"^#{%d}\s+(.+)$" % level, line.strip())
        if m:
            yield build.slugify(m.group(1))


# ---------------------------------------------------------------- converter

class TestMarkdown(unittest.TestCase):
    def test_headings_get_ids(self):
        h = build.md_to_html("# One\n\n## Two Things!")
        self.assertIn('<h1 id="one">One</h1>', h)
        self.assertIn('<h2 id="two-things">Two Things!</h2>', h)

    def test_inline_styles_escape(self):
        h = build.md_to_html("Text with <b> & **bold** *em*")
        self.assertIn(
            "&lt;b&gt; &amp; <strong>bold</strong> <em>em</em>", h
        )

    def test_link_and_code(self):
        h = build.md_to_html("See [the doc](x.md) and `code()`")
        self.assertIn('<a href="x.md">the doc</a>', h)
        self.assertIn("<code>code()</code>", h)

    def test_lists_nested_and_ordered(self):
        h = build.md_to_html("- a\n  - a1\n- b\n\n1. one\n2. two")
        self.assertIn("<ul>", h)
        self.assertIn("<li>a\n<ul>\n<li>a1</li>\n</ul>\n</li>", h)
        self.assertIn("<ol>\n<li>one</li>\n<li>two</li>\n</ol>", h)

    def test_checkboxes(self):
        h = build.md_to_html("- [ ] open\n- [x] closed")
        self.assertIn('<input type="checkbox"> open', h)
        self.assertIn('<input type="checkbox" checked> closed', h)

    def test_table(self):
        h = build.md_to_html("| A | B |\n| --- | --- |\n| 1 | 2 |")
        self.assertIn("<table><thead><tr><th>A</th><th>B</th>", h)
        self.assertIn("<tbody><tr><td>1</td><td>2</td></tr>", h)

    def test_quote_and_code_fence(self):
        h = build.md_to_html("> note **bold**\n\n```\nraw <text>\n```")
        self.assertIn(
            "<blockquote>note <strong>bold</strong></blockquote>", h
        )
        self.assertIn("<pre><code>raw &lt;text&gt;", h)

    def test_hr(self):
        self.assertIn("<hr>", build.md_to_html("a\n\n---\n\nb"))

    def test_paragraph_soft_wrap(self):
        h = build.md_to_html("first line\nsecond line")
        self.assertEqual(h, "<p>first line second line</p>")

    def test_quotes_get_paragraph_free_join(self):
        h = build.md_to_html("> one\n> two")
        self.assertEqual(h, "<blockquote>one two</blockquote>")


# ---------------------------------------------------------------- links util

class TestLinkRewrite(unittest.TestCase):
    def test_plain_md_link(self):
        self.assertIn(
            "08-call-log.html",
            build.convert_links("pre [y](08-call-log.md)"),
        )

    def test_md_link_with_anchor(self):
        self.assertIn(
            "07-self-pacing.html#the-ten-tabs",
            build.convert_links("pre [x](07-self-pacing.md#the-ten-tabs)"),
        )

    def test_csv_links_untouched(self):
        md = "[a](../worksheets/call-log.csv)"
        self.assertEqual(build.convert_links(md), md)


# ---------------------------------------------------------------- content

class TestDocs(unittest.TestCase):
    def test_all_docs_exist(self):
        for slug in SLUGS:
            self.assertTrue(
                (DOCS / f"{slug}.md").exists(), f"missing docs/{slug}.md"
            )

    def test_every_doc_starts_with_title(self):
        for slug in SLUGS:
            text = doc_text(slug)
            self.assertTrue(
                text.split("\n", 1)[0].startswith("# "),
                f"{slug}.md must start with an H1 title",
            )

    def test_expected_key_phrases(self):
        expected = {
            "01-first-week": "week-one checklist",
            "02-who-to-call": "in what order",
            "03-what-to-keep": "forever file",
            "04-accounts-and-subscriptions": "subscriptions-tracker.csv",
            "05-mail-and-benefits": "survivor benefits",
            "06-predatory-help-red-flags": "gift card",
            "07-self-pacing": "988",
            "08-call-log": "Ref / case #",
            "09-binder-checklist": "The ten tabs",
            "10-glossary": "Power of attorney (POA)",
        }
        for slug, phrase in expected.items():
            self.assertIn(phrase, doc_text(slug), f"{slug} missing {phrase}")

    def test_distinctness_from_sibling_projects(self):
        text = doc_text("index")
        for name in ("caregiver-coordination-guide", "digital-legacy-handbook"):
            self.assertIn(name, text, f"index must mention {name}")
        read_me = (ROOT / "README.md").read_text(encoding="utf-8")
        for name in ("caregiver-coordination-guide", "digital-legacy-handbook"):
            self.assertIn(name, read_me)

    def test_disclaimers_present(self):
        read_me = (ROOT / "README.md").read_text("utf-8")
        low = re.sub(r"\s+", " ", read_me.lower())
        self.assertIn("not legal advice", low)
        self.assertIn("not grief counseling", low)
        self.assertIn("education", low)
        idx = re.sub(r"\s+", " ", doc_text("index").lower())
        self.assertIn("not legal advice", idx)
        self.assertIn("not grief counseling", idx)

    def test_no_url_guessing_or_placeholders(self):
        for slug in SLUGS:
            text = doc_text(slug)
            for bad in ("example.invalid", "example.com", "TODO", "FIXME"):
                self.assertNotIn(bad, text, f"{slug} contains {bad}")

    def test_csv_links_resolve(self):
        for slug in SLUGS:
            text = doc_text(slug)
            for target in re.findall(r"\]\(([^)]+?\.csv)\)", text):
                path = (DOCS / target).resolve()
                self.assertTrue(
                    path.is_file(), f"{slug} links missing CSV {target}"
                )

    def test_md_links_resolve_including_anchors(self):
        for slug in SLUGS:
            text = doc_text(slug)
            for m in re.finditer(r"\]\(([^)#\s]+?\.md)(#[^)\s]+)?\)", text):
                target, anchor = m.group(1), m.group(2)
                self.assertFalse(
                    target.startswith("../"),
                    f"{slug} has root-escaping md link {target}",
                )
                tpath = DOCS / target
                self.assertTrue(
                    tpath.exists(), f"{slug} links missing {target}"
                )
                if anchor:
                    slugs = set(headings_of(tpath.read_text("utf-8")))
                    self.assertIn(
                        anchor[1:], slugs,
                        f"{slug} anchor {anchor} not a heading in {target}",
                    )

    def test_anchor_links_resolve_within_own_page(self):
        for slug in SLUGS:
            text = doc_text(slug)
            own = set()
            for level in (1, 2, 3):
                own |= set(headings_of(text, level))
            for m in re.finditer(r"\]\((#[a-z0-9-]+)\)", text):
                self.assertIn(
                    m.group(1)[1:], own, f"{slug} broken in-page anchor"
                )


# ---------------------------------------------------------------- build

class TestBuiltSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp, cls.site_dir = _fake_site_root()
        _restore_build_site(cls.site_dir, 0)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_pages_and_print_pages_exist(self):
        for slug in SLUGS:
            self.assertTrue(
                (self.site_dir / f"{slug}.html").exists(),
                f"missing {slug}.html",
            )
        for slug in build.PRINT_SLUGS:
            self.assertTrue(
                (self.site_dir / "print" / f"{slug}.html").exists(),
                f"missing print/{slug}.html",
            )

    def test_worksheets_copied(self):
        for csv_path in sorted((ROOT / "worksheets").glob("*.csv")):
            self.assertTrue(
                (self.site_dir / "worksheets" / csv_path.name).exists(),
                f"missing site/worksheets/{csv_path.name}",
            )

    def test_pages_are_well_formed(self):
        for path in sorted(self.tmp.rglob("*.html")):
            parser = TagBalanceParser()
            parser.feed(path.read_text(encoding="utf-8"))
            self.assertFalse(parser.errors, f"{path.name}: {parser.errors}")
            self.assertEqual(parser.stack, [])

    def test_footer_on_every_content_page(self):
        for slug in SLUGS:
            html = (self.site_dir / f"{slug}.html").read_text("utf-8")
            self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC", html)
            self.assertIn(
                "never legal, tax, or grief-counseling advice", html
            )
            self.assertIn('<nav class="toc">', html)

    def test_print_pages_have_no_nav_or_footer(self):
        for slug in build.PRINT_SLUGS:
            html = (self.site_dir / "print" / f"{slug}.html").read_text("utf-8")
            self.assertNotIn('<nav class="toc">', html)
            self.assertNotIn("<footer>", html)

    def test_nav_lists_every_page(self):
        html = (self.site_dir / "index.html").read_text("utf-8")
        for slug, name in build.PAGES:
            self.assertIn(f'href="{slug}.html">{name}</a>', html)

    def test_no_raw_markdown_leftovers(self):
        for path in sorted(self.tmp.rglob("*.html")):
            html = path.read_text("utf-8")
            self.assertNotIn("](http", html, path.name)
            for line in html.split("\n"):
                self.assertFalse(
                    line.startswith("# "), f"{path.name} leaked heading"
                )

    def test_all_local_hrefs_resolve(self):
        for path in sorted(self.tmp.rglob("*.html")):
            html = path.read_text("utf-8")
            for href in re.findall(r'href="([^"]+)"', html):
                if href.startswith(("http", "mailto:")) or href.startswith("#"):
                    continue
                file_ref = href.split("#", 1)[0] or ""  # strip fragment
                target = (path.parent / file_ref).resolve()
                self.assertTrue(
                    target.exists() and target.is_file(),
                    f"{path.name} broken link {href}",
                )

    def test_anchors_resolve_in_built_pages(self):
        for path in sorted(self.site_dir.glob("*.html")):
            html = path.read_text("utf-8")
            ids = set(re.findall(r'id="([^"]+)"', html))
            for href in re.findall(r'href="#([^"]+)"', html):
                self.assertIn(href, ids, f"{path.name} missing #{href}")

    def test_rebuild_is_deterministic(self):
        first = (self.site_dir / "index.html").read_bytes()
        tmp2, site2 = _fake_site_root()
        try:
            _restore_build_site(site2, 0)
            self.assertEqual(first, (site2 / "index.html").read_bytes())
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)


# ---------------------------------------------------------------- csv

class TestWorksheets(unittest.TestCase):
    def _rows(self, name):
        with (ROOT / "worksheets" / name).open(
            newline="", encoding="utf-8"
        ) as fh:
            return list(csv.reader(fh))

    def test_call_log_structure(self):
        rows = self._rows("call-log.csv")
        self.assertEqual(len(rows[0]), 9)
        self.assertIn("Ref / case number", rows[0])
        self.assertTrue(all(len(r) == 9 for r in rows))

    def test_subscriptions_structure(self):
        rows = self._rows("subscriptions-tracker.csv")
        self.assertEqual(len(rows[0]), 8)
        self.assertTrue(all(len(r) == 8 for r in rows))

    def test_sample_rows_marked(self):
        call = self._rows("call-log.csv")
        subs = self._rows("subscriptions-tracker.csv")
        self.assertTrue(any("SAMPLE" in c for r in call[1:] for c in r))
        self.assertTrue(any("SAMPLE" in c for r in subs[1:] for c in r))


# ---------------------------------------------------------------- repo

class TestRepo(unittest.TestCase):
    def test_license_copyright_line_exact(self):
        lic = (ROOT / "LICENSE").read_text("utf-8")
        self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC", lic)
        self.assertIn(
            "Copyright (c) 2026 Asdale Dynamics, LLC", lic.split("\n")[:5]
        )

    def test_readme_credits_llc(self):
        read_me = (ROOT / "README.md").read_text("utf-8")
        self.assertIn("**Asdale Dynamics, LLC**", read_me)
        self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC", read_me)

    def test_build_flags_documented_in_readme(self):
        read_me = (ROOT / "README.md").read_text("utf-8")
        for flag in ("--serve", "--clean"):
            self.assertIn(flag, read_me)

    def test_no_secrets_anywhere(self):
        patterns = [
            r"AKIA[0-9A-Z]{16}",
            r"ghp_[A-Za-z0-9]{20,}",
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
            r"AIza[0-9A-Za-z_\-]{20,}",
            r"xox[bp]-[A-Za-z0-9\-]{10,}",
            r"sk-live-[A-Za-z0-9]{10,}",
        ]
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or ".git" in path.parts:
                continue
            if path.suffix in {".pyc", ".png", ".jpg", ".gif"}:
                continue
            text = path.read_text("utf-8", errors="ignore")
            for pat in patterns:
                self.assertFalse(
                    re.search(pat, text),
                    f"possible secret {pat} in {path.relative_to(ROOT)}",
                )

    def test_static_serve_smoke(self):
        self.assertEqual(build.build(), 0)
        with socketserver.TCPServer(("127.0.0.1", 0), build.Handler) as httpd:
            port = httpd.server_address[1]
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()
            try:
                conn = http.client.HTTPConnection(
                    "127.0.0.1", port, timeout=5
                )
                conn.request("GET", "/index.html")
                resp = conn.getresponse()
                body = resp.read()
                self.assertEqual(resp.status, 200)
                self.assertIn(b"Bereavement Paperwork Guide", body)
                conn.close()
            finally:
                httpd.shutdown()
                httpd.server_close()


if __name__ == "__main__":
    unittest.main()
