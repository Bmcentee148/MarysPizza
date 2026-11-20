#!/usr/bin/env python3
"""Step 1 of the build: stitch the inner pages together from the homepage template.

index.html is both the homepage and the master template. Everything before
<main id="main"> (the <head> with all site CSS, the header/nav, the mobile menu)
is HEAD, and everything after </main> (the footer and shared JS) is FOOT.
Each inner page is HEAD + pages/<name>.main.html + FOOT, with its own <title>,
meta description and canonical swapped in, so the header, footer and styles
are written once and can never drift apart between pages.

Generated pages are written to src/<name>.html (git-ignored). Run build.py,
which calls this, rather than running it directly.
"""
from pathlib import Path

SRC = Path(__file__).resolve().parent

# Per-page config. The key is the page name: pages/<name>.main.html holds the
# content and the page is served at /<name>/.
#   css: extra stylesheets from pages/, inlined at the end of the site <style>
#   js:  extra scripts from pages/, inlined before </body>
PAGES = {
    "takeout-menu-speonk": {
        "title": "Takeout Menu — Speonk | Mary's Pizza and Pasta",
        "description": "Full takeout menu for Mary's Pizza and Pasta at the Olde Speonk Inn — pizza, pasta, chicken, steak, and more.",
        "css": ["menu.css"],
    },
    "takeout-menu-farmingdale-islip": {
        "title": "Takeout Menu — Farmingdale &amp; Islip Terrace | Mary's Pizza and Pasta",
        "description": "Full takeout menu for Mary's Pizza and Pasta in Farmingdale and Islip Terrace, NY — pizza, pasta, heroes, wings, entrees, and more.",
        "css": ["menu.css"],
    },
    "catering-menu": {
        "title": "Catering Menu — Mary's Pizza and Pasta | Speonk, Islip Terrace &amp; Farmingdale",
        "description": "Catering menu for Mary's Pizza and Pasta — platters, packages, entrees, and party heroes for offices, parties, and events. Serving Speonk, Islip Terrace, and Farmingdale, NY.",
        "css": ["menu.css"],
    },
    "gallery": {
        "title": "Gallery | Mary's Pizza and Pasta",
        "description": "Photos of the food, dining room and bar at Mary's Pizza and Pasta on Long Island: pizza, pasta, chicken parm and more.",
        "css": ["gallery.css"],
        "js": ["gallery.js"],
    },
    "contact": {
        "title": "Contact | Mary's Pizza and Pasta",
        "description": "Call Mary's Pizza and Pasta in Speonk, Islip Terrace or Farmingdale, or send us a note about catering, private events and big orders.",
        "css": ["contact.css"],
    },
}

MAIN_OPEN = '<main id="main">'
MAIN_CLOSE = "</main>"


def must_replace(text, old, new, what):
    """Replace exactly one occurrence of `old`, or fail the build.

    If the template changes and a replacement no longer matches, we want a
    loud failure instead of silently shipping a page with the wrong title etc.
    """
    count = text.count(old)
    assert count == 1, f"{what}: expected exactly 1 match for {old!r}, found {count}"
    return text.replace(old, new)


def between(text, start, end, what):
    """Return the text between the unique `start` and the next `end` (exclusive)."""
    assert text.count(start) == 1, f"{what}: expected exactly 1 {start!r}"
    i = text.index(start) + len(start)
    j = text.index(end, i)
    return text[i:j]


def split_template(index_html):
    assert index_html.count(MAIN_OPEN) == 1, f"index.html must contain exactly one {MAIN_OPEN}"
    assert index_html.count(MAIN_CLOSE) == 1, f"index.html must contain exactly one {MAIN_CLOSE}"
    head, rest = index_html.split(MAIN_OPEN)
    _, foot = rest.split(MAIN_CLOSE)
    return head + MAIN_OPEN + "\n", "\n" + MAIN_CLOSE + foot


def make_page(name, cfg, head, foot, home_canonical):
    page_head = head
    home_title = between(head, "<title>", "</title>", "index.html <title>")
    page_head = must_replace(page_head, f"<title>{home_title}</title>",
                             f"<title>{cfg['title']}</title>", f"{name} title")
    home_desc = between(head, '<meta name="description" content="', '"', "index.html meta description")
    page_head = must_replace(page_head, f'<meta name="description" content="{home_desc}"',
                             f'<meta name="description" content="{cfg["description"]}"', f"{name} description")
    page_head = must_replace(page_head, f'<link rel="canonical" href="{home_canonical}"',
                             f'<link rel="canonical" href="{home_canonical}{name}/"', f"{name} canonical")

    for css_file in cfg.get("css", []):
        css = (SRC / "pages" / css_file).read_text(encoding="utf-8")
        page_head = must_replace(page_head, "</style>", "\n" + css.rstrip() + "\n</style>", f"{name} css {css_file}")

    page_foot = foot
    for js_file in cfg.get("js", []):
        js = (SRC / "pages" / js_file).read_text(encoding="utf-8")
        page_foot = must_replace(page_foot, "</body>", "<script>\n" + js.rstrip() + "\n</script>\n</body>", f"{name} js {js_file}")

    content = (SRC / "pages" / f"{name}.main.html").read_text(encoding="utf-8")
    return page_head + content.strip("\n") + page_foot


def make_pages():
    """Generate every inner page into src/<name>.html. Returns the written paths."""
    index_html = (SRC / "index.html").read_text(encoding="utf-8")
    head, foot = split_template(index_html)
    home_canonical = between(head, '<link rel="canonical" href="', '"', "index.html canonical")
    assert home_canonical.startswith("https://") and home_canonical.endswith("/"), \
        f"homepage canonical must be an absolute https URL ending in /: {home_canonical!r}"

    written = []
    for name, cfg in PAGES.items():
        out = SRC / f"{name}.html"
        out.write_text(make_page(name, cfg, head, foot, home_canonical), encoding="utf-8")
        written.append(out)
    return written


if __name__ == "__main__":
    for path in make_pages():
        print(f"generated {path.relative_to(SRC)}")
