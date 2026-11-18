# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Static marketing site for Mary's Pizza and Pasta (three locations: Speonk, Islip Terrace, Farmingdale, NY). Hand-written HTML + CSS + vanilla JS, assembled by two small Python 3 scripts (standard library only, no npm, no framework). Deployed on Netlify, which runs the build on every push (`netlify.toml`) and publishes `dist/`. The inquiry form relies on Netlify Forms.

## Commands

```bash
cd src && python3 build.py          # build into dist/ (also runs make_pages.py); fails on any check
cd dist && python3 -m http.server 8000   # preview at http://localhost:8000/
```

There are no tests or linter; the build's checks are the validation. Pages use root-relative URLs, so open them through a server, not via `file://`. Form submission only works when deployed on Netlify.

## How the build works

- `src/index.html` is the homepage **and** the master template. Everything before `<main id="main">` (the `<head>` with all site CSS in one `<style>`, header/nav, mobile menu) and everything after `</main>` (footer, shared JS) is shared by every page. Edit the header/footer/site CSS only here.
- `src/pages/<name>.main.html` holds only the `<main>` content of an inner page. `src/pages/menu.css` is extra CSS for the three menu pages, inlined at the end of their `<style>`.
- `src/make_pages.py` (step 1): `PAGES` dict (title, meta description, optional `css`/`js` files from `pages/`). Stitches HEAD + content + FOOT into `src/<name>.html` (git-ignored), swapping title, description and canonical via `must_replace` helpers that assert exactly one match, so a template change that breaks a replacement fails the build.
- `src/build.py` (step 2): wipes `dist/`, copies `src/assets/`, runs step 1, fills `TEXT` placeholders (`__ORDER_URL__` etc.; values containing `TODO` print a NOTE), validates, then writes clean URLs (`dist/<name>/index.html`, served at `/<name>/`) and `dist/sitemap.xml`. The production domain lives only in the homepage canonical.
- The build **fails** on: unreplaced `__TOKEN__`; relative links or links to `.html` (use `/page/`, `/#section`, `/assets/...`); links to pages not in `PAGES` (or `PLANNED`); `#fragment` links to ids that don't exist on the target page; missing/mis-capitalized asset files; inline `data:` images; wrong canonical; `<img>` without alt; `target="_blank"` without `rel="noopener"`; the Netlify form losing `data-netlify` or its hidden `form-name` input. `href="#"` placeholders (social icons) only print a NOTE.
- To add a page: create `src/pages/<name>.main.html` and add it to `PAGES` in `make_pages.py`. Old `.html` URLs of the menu pages are 301-redirected in `netlify.toml`; keep that if pages are renamed.
- Images live in `src/assets/images/` and are linked by root-relative path (`/assets/images/logo.png`), including the hero `url()` in the CSS. Don't inline images as base64. `TempPics/` holds unused source photos.

## Shared JS (in `src/index.html`, runs on every page)

- **Location switcher**: the `LOCATIONS` object (id → name, `orderUrl`, `takeoutMenuUrl`, `cateringMenuUrl`) drives everything location-specific. `applyLocation(id)` syncs the nav/mobile `<select>`s, all `.order-link` hrefs, `.loc-name` text, `.loc-pill`/`.loc-card` active states and `#takeoutMenuLink`/`#cateringMenuLink`, then persists to `localStorage` key `marysLocation` (so the choice carries across pages). `DEFAULT_LOC` is `farmingdale`. To add a location, update `LOCATIONS` plus the matching `data-loc` elements and `<option>`s.
- **Anchor scrolling**: links whose URL points to an id on the current page (`/#menu` on the homepage) are intercepted and scrolled with an offset for the sticky nav (`scrollToId`); from inner pages they navigate to the homepage, where a load-time hash fix applies the same offset. Don't rely on native anchor jumps or CSS `scroll-margin` alone.
- **Inquiry form** (`#inqForm`, homepage only, guarded with `if(form)`): Netlify form `inquiry` with honeypot `bot-field`, AJAX `fetch('/')` url-encoded; on completion `#formHost` gets `is-sent`. Netlify detects the form from the built HTML, so keep `data-netlify`, the hidden `form-name` input and field `name`s.
- Code that only applies to some pages must tolerate its elements being absent. `.reveal` elements fade in via IntersectionObserver (adds `.in`).
