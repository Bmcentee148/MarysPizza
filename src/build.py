#!/usr/bin/env python3
"""Step 2 of the build: generate pages, fill placeholders, validate, write dist/.

Usage (from the repo root or anywhere):  cd src && python3 build.py

dist/ is wiped and rebuilt every time; never edit it by hand. Netlify runs this
same command on every push (see netlify.toml) and publishes dist/.
Standard library only, no installs needed.
"""
import re
from datetime import date
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from make_pages import PAGES, make_pages, between

SRC = Path(__file__).resolve().parent
DIST = SRC.parent / "dist"

# Shared text placeholders. Write __NAME__ in any page or in the template and
# it is replaced with the value here, so a value changes in one place.
# Any value containing "TODO" prints a NOTE on every build until it's filled in.
TEXT = {
    "__ORDER_URL__": "https://maryspizza.hungerrush.com/Order/OrderType",
    # OpenTable pages (Farmingdale takes reservations by phone only)
    "__RESERVE_SPEONK__": "https://www.opentable.com/r/marys-pizza-and-pasta-speonk",
    "__RESERVE_ISLIP__": "https://www.opentable.com/r/marys-pizza-and-restaurant-islip-terrace",
}

# Pages that are linked to but not built yet (e.g. "/about/"). Links to these
# don't fail the build. Keep empty unless you're adding a page in stages.
PLANNED = {"/islip-terrace/", "/farmingdale/"}

TOKEN_RE = re.compile(r"__[A-Z0-9]+(?:_[A-Z0-9]+)*__")


class PageScan(HTMLParser):
    """Collects what the checks need: ids, links, assets, scripts, canonicals."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.refs = []        # (tag, attr, value, attrs-dict)
        self.canonicals = []
        self.imgs_without_alt = []
        self.forms = []
        self.hidden_inputs = []
        self.mains = 0
        self._in = None
        self.scripts = []
        self.styles = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        for attr in ("href", "src"):
            if a.get(attr) is not None:
                self.refs.append((tag, attr, a[attr], a))
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href"))
        if tag == "img" and not a.get("alt"):
            self.imgs_without_alt.append(a.get("src"))
        if tag == "form":
            self.forms.append(a)
        if tag == "input" and a.get("type") == "hidden":
            self.hidden_inputs.append(a)
        if tag == "main":
            self.mains += 1
        if tag in ("script", "style"):
            self._in = tag

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._in = None

    def handle_data(self, data):
        if self._in == "script":
            self.scripts.append(data)
        elif self._in == "style":
            self.styles.append(data)


def url_for(name):
    return "/" if name == "index" else f"/{name}/"


def out_path(name):
    # Clean URLs: /catering-menu/ is served from dist/catering-menu/index.html.
    # index.html (and a future 404.html) stay at the root.
    if name in ("index", "404"):
        return DIST / f"{name}.html"
    return DIST / name / "index.html"


def exists_exact_case(path):
    """True if path exists with exactly this capitalization (Netlify is case-sensitive,
    a Mac's disk usually isn't, so a plain exists() would hide mistakes)."""
    path = path.resolve()
    try:
        rel = path.relative_to(DIST.resolve())
    except ValueError:
        return False
    cur = DIST.resolve()
    for part in rel.parts:
        if not cur.is_dir() or part not in {p.name for p in cur.iterdir()}:
            return False
        cur = cur / part
    return cur.is_file()


def check_page(name, html, scans, site_url, errors, notes):
    scan = scans[name]
    where = url_for(name)

    def err(msg):
        errors.append(f"{where}: {msg}")

    for token in sorted(set(TOKEN_RE.findall(html))):
        err(f"unreplaced placeholder {token} (add it to TEXT in build.py?)")

    # canonical: exactly one, absolute, self-referencing
    if PAGES.get(name, {}).get("noindex"):
        if scan.canonicals:
            err(f"noindex page shouldn't have a canonical, found {scan.canonicals!r}")
    else:
        expected = site_url.rstrip("/") + where
        if scan.canonicals != [expected]:
            err(f"canonical should be exactly [{expected!r}], found {scan.canonicals!r}")

    if scan.mains != 1:
        err(f"expected exactly one <main>, found {scan.mains}")

    for src in scan.imgs_without_alt:
        err(f"<img src={src!r}> is missing alt text")

    # every link / asset reference in markup and CSS
    refs = [(tag, attr, value, a) for tag, attr, value, a in scan.refs]
    for css in scan.styles + re.findall(r'style="([^"]*)"', html):
        for value in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", css):
            refs.append(("css", "url", value, {}))
    # internal page URLs written as strings in JS (e.g. LOCATIONS menu URLs)
    for js in scan.scripts:
        for value in re.findall(r"['\"](/[\w./#-]*)['\"]", js):
            refs.append(("script", "string", value, {}))
        for value in re.findall(r"['\"]([^'\"\s]+\.html)['\"]", js):
            err(f"script references {value!r}: link to clean URLs like /page/, not .html files")

    placeholders = 0
    for tag, attr, value, a in refs:
        value = value.strip()
        if value.startswith(("http://", "https://")):
            if a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""):
                err(f'external link {value!r} opens a new tab but lacks rel="noopener"')
            continue
        if value.startswith(("mailto:", "tel:", "data:")) or (tag == "link" and attr == "href" and value.startswith("//")):
            if value.startswith("data:") and tag != "script":
                err(f"inline data: URI found; put the file in src/assets/ and link to it instead")
            continue
        if value == "#":
            placeholders += 1
            continue
        if value.startswith("#"):
            if value[1:] not in scan.ids:
                err(f'{tag} {attr}="{value}" points to an id that doesn\'t exist on this page')
            continue
        if not value.startswith("/") or value.startswith("//"):
            err(f'{tag} {attr}="{value}" is relative; use a root-relative path like "/assets/..." or "/page/"')
            continue

        parts = urlsplit(value)
        path, frag = parts.path, parts.fragment
        if path.endswith(".html"):
            err(f'{tag} {attr}="{value}" links to a .html file; use the clean URL ("/page/")')
            continue
        pages_by_url = {url_for(n): n for n in scans}
        if path in pages_by_url:
            target = pages_by_url[path]
            if frag and frag not in scans[target].ids:
                err(f'{tag} {attr}="{value}": #{frag} doesn\'t exist on {path}')
            continue
        if path in PLANNED:
            continue
        if path.startswith("/assets/"):
            if not exists_exact_case(DIST / path.lstrip("/")):
                err(f'{tag} {attr}="{value}": file not found in src/assets/ (check spelling and capitalization)')
            continue
        if path.rstrip("/") and not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
            err(f'{tag} {attr}="{value}": page URLs need a trailing slash ("{path}/")')
            continue
        err(f'{tag} {attr}="{value}" points to a page that isn\'t built (typo? add it to PAGES or PLANNED)')

    if placeholders:
        notes.append(f'{where}: {placeholders} placeholder link(s) with href="#" (e.g. social icons)')


def check_site_rules(scans, errors):
    """Project-specific content rules."""
    page = scans["contact"]  # the inquiry form lives on /contact/
    netlify_forms = [f for f in page.forms if "data-netlify" in f]
    if not netlify_forms:
        errors.append('/contact/: the inquiry form must keep data-netlify="true" so Netlify Forms detects it')
    for f in netlify_forms:
        if not any(i.get("name") == "form-name" and i.get("value") == f.get("name") for i in page.hidden_inputs):
            errors.append(f'/contact/: Netlify form {f.get("name")!r} needs <input type="hidden" name="form-name" value="{f.get("name")}">')


def check_promo_dates(pages, errors, notes):
    """Promotions carry data-ends="YYYY-MM-DD" (last day shown). The page hides them
    after that date; this reminds you to delete the expired ones."""
    today = date.today()
    for name, html in pages.items():
        for value in re.findall(r'data-ends="([^"]*)"', html):
            try:
                ends = date.fromisoformat(value)
            except ValueError:
                errors.append(f'{url_for(name)}: data-ends="{value}" must be a date like 2026-12-31')
                continue
            if ends < today:
                notes.append(f"{url_for(name)}: a promotion ended on {value} and is hidden; remove it from src/pages/{name}.main.html")


def write_sitemap(site_url, names):
    base = site_url.rstrip("/")
    urls = "".join(f"  <url><loc>{base}{url_for(n)}</loc></url>\n" for n in names)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}</urlset>\n",
        encoding="utf-8",
    )


def fill_text(html):
    # longest token first, so a token that's a prefix of another can't clobber it
    for token in sorted(TEXT, key=len, reverse=True):
        html = html.replace(token, TEXT[token])
    return html


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(SRC / "assets", DIST / "assets")

    generated = make_pages()
    sources = {"index": SRC / "index.html"}
    sources.update({p.stem: p for p in generated})
    assert set(sources) == {"index", *PAGES}

    pages = {name: fill_text(path.read_text(encoding="utf-8")) for name, path in sources.items()}
    # __SITE_URL__ (e.g. in structured data) = the production domain from the homepage canonical
    site_url = between(pages["index"], '<link rel="canonical" href="', '"', "index.html canonical")
    pages = {name: html.replace("__SITE_URL__", site_url.rstrip("/")) for name, html in pages.items()}
    scans = {}
    for name, html in pages.items():
        scans[name] = PageScan()
        scans[name].feed(html)


    errors, notes = [], []
    for token, value in TEXT.items():
        if "TODO" in value:
            notes.append(f"TEXT {token} is still a TODO: {value!r}")
    for name, html in pages.items():
        check_page(name, html, scans, site_url, errors, notes)
    check_site_rules(scans, errors)
    check_promo_dates(pages, errors, notes)

    if errors:
        print("BUILD FAILED:\n  " + "\n  ".join(errors), file=sys.stderr)
        shutil.rmtree(DIST)
        sys.exit(1)

    for name, html in pages.items():
        out = out_path(name)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"  {str(out.relative_to(DIST.parent)):<46} {url_for(name):<34} {len(html.encode()) / 1024:6.1f} KB")
    write_sitemap(site_url, [n for n in pages if not PAGES.get(n, {}).get("noindex")])
    print("  dist/sitemap.xml")
    for note in notes:
        print(f"NOTE: {note}")
    print(f"Built {len(pages)} pages into {DIST.relative_to(SRC.parent)}/")


if __name__ == "__main__":
    build()
