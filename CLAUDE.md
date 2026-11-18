# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Static marketing site for Mary's Pizza and Pasta (three locations: Speonk, Islip Terrace, Farmingdale, NY). Plain hand-written HTML with inline `<style>` and `<script>` — no build step, package manager, framework, linter, or tests. Deployed on Netlify (the inquiry form relies on Netlify Forms).

To preview locally, serve the directory and open it in a browser, e.g. `python3 -m http.server 8000`. The form submission only works when deployed on Netlify.

## Pages

- `index.html` — the main single-page site (nav, hero, menu, loyalty, catering, events, locations, inquiry form, footer). Sections are anchored by id (`#menu`, `#catering`, `#locations`, `#order`, …); the sub-pages link back to these anchors.
- `takeout-menu-speonk.html`, `takeout-menu-farmingdale-islip.html` (shared by those two locations), `catering-menu.html` — standalone menu pages with their own copy of the nav/footer and a slimmer stylesheet.

Each page is fully self-contained: CSS is duplicated per file (same `:root` color tokens — `--cream`, `--red`, `--ink`, `--gold`, etc.), so a shared style or nav/footer change must be applied to every page by hand. Fonts come from Google Fonts (Archivo, Libre Franklin, plus DM Serif Display on `index.html`). The site forces a light color scheme even in dark mode.

## Working with the files

- **Images are embedded as base64 `data:` URIs**, so some lines are 65K–235K characters long (the logo alone is ~87K and repeats on every page). Don't `cat`/`Read` whole files or print raw grep matches — truncate output (e.g. `cut -c1-200`) and use line ranges. Edit around these lines, not through them.
- `TempPics/` holds source photos; they are not referenced by the pages (images are inlined instead).

## `index.html` JavaScript

- **Location switcher**: the `LOCATIONS` object (id → name, `orderUrl`, `takeoutMenuUrl`, `cateringMenuUrl`) drives everything location-specific. `applyLocation(id)` syncs the nav/mobile `<select>`s, all `.order-link` hrefs, `.loc-name` text, `.loc-pill` and `.loc-card` active states, and the `#takeoutMenuLink` / `#cateringMenuLink` hrefs, then persists the choice to `localStorage` key `marysLocation`. `DEFAULT_LOC` is `farmingdale`. To add or change a location, update `LOCATIONS` plus the matching `data-loc` elements and `<option>`s in the markup.
- **Anchor scrolling**: in-page `#` links are intercepted and scrolled with an offset for the sticky nav height (`scrollToId`); loading with a hash re-applies the scroll after load to correct for late layout shifts. Don't rely on native anchor jumps or CSS `scroll-margin` alone.
- **Inquiry form** (`#inqForm`): Netlify form named `inquiry` with honeypot `bot-field`, submitted via AJAX `fetch('/')` (url-encoded); on completion `#formHost` gets class `is-sent`. Keep the hidden `form-name` input and `data-netlify` attribute intact, and if fields are added keep their `name` attributes, since Netlify detects the form from the static HTML.
- Elements with class `.reveal` fade in via an IntersectionObserver (adds `.in`).
