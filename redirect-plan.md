# Redirect plan: old WordPress site → rebuild

Crawled 2026-11-27 from `https://maryspizzaandpasta.com` (Yoast sitemap index, all 5 sub-sitemaps, then every internal link followed). 44 URLs in the sitemap, all return 200; the crawl found no extra pages beyond WordPress system URLs. A `site:` search showed nothing else indexed. Two broken links (`/lincoln-wortman-ave/`, `/projects/`) come from a leftover theme demo page and already 404.

All redirects are 301s in `netlify.toml`. Netlify matches with or without the trailing slash, so one rule per path is enough.

## How the old site is structured

The nav (identical on every page) is the live site. Everything else is an orphaned draft or old version that is still public and indexable.

```
Home (/)                      location chooser → the 3 location homes
├─ Farmingdale                /home-farmingdale/
├─ Islip Terrace              /home-islip/
├─ Speonk                     /home-speonk/
About Us
├─ Islip Terrace              /about-us-islip/
├─ Farmingdale                /about-us-farmingdale/
├─ Speonk                     /about-us-speonk/
Gallery                       /gallery/
Menus                         /menus/            (Farmingdale + Islip hub)
├─ Farmingdale / Islip        /farmingdale-dineinmenu/  (Islip's "Dine In" link also points here, an old-site bug)
│                             /islip-farm-takeout-menu/
│                             /catering-menu-new/
│                             PDFs: Pasta Night, Chicken Night, Seafood Night, Holiday Menu, Black Friday
├─ Speonk                     /menus-speonk/     (Speonk hub)
│                             /speonk-dine-in-menu/  /speonk-drink-menu/  /speonk-takeout-menu/  /catering-menu-new/
│                             PDFs: Happy Hour Specials, Holiday Menu, Black Friday
Employment                    /employment-new/
Contact Us                    /contact-main/
Order Now                     HungerRush (external, unchanged)
```

## Redirect table

**⚠ Islip Terrace and Farmingdale location pages aren't built yet.** Rules that point at `/islip-terrace/` or `/farmingdale/` would land on the 404 page if we cut over before those pages exist. Either build them first, or point those rules at `/#locations` for now and switch them later (marked † below).

### Location pages (top priority: most likely what Google Business Profile and other listings link to)

| Old URL | New URL | Notes |
|---|---|---|
| `/home-speonk/` | `/speonk/` | in nav |
| `/home-islip/` | `/islip-terrace/` † | in nav |
| `/home-farmingdale/` | `/farmingdale/` † | in nav |
| `/home-islip-2024/` | `/islip-terrace/` † | old version |
| `/home-farmingdale-2025/` | `/farmingdale/` † | old version |
| `/about-us-speonk/` | `/speonk/` | in nav; store story lives on the location page now |
| `/about-us-islip/` | `/islip-terrace/` † | in nav |
| `/about-us-farmingdale/` | `/farmingdale/` † | in nav |

### Menus

| Old URL | New URL | Notes |
|---|---|---|
| `/menus/` | `/takeout-menu-farmingdale-islip/` | in nav; Farmingdale/Islip hub |
| `/menus-speonk/` | `/takeout-menu-speonk/` | in nav; Speonk hub |
| `/islip-farm-takeout-menu/` | `/takeout-menu-farmingdale-islip/` | in nav |
| `/take-out-menu/` | `/takeout-menu-farmingdale-islip/` | orphan, 2022 |
| `/speonk-takeout-menu/` | `/takeout-menu-speonk/` | in nav |
| `/speonk-takeoutmenu/` | `/takeout-menu-speonk/` | orphan, 2021 |
| `/farmingdale-dineinmenu/` | `/takeout-menu-farmingdale-islip/` | in nav; **no dine-in menu on the rebuild** (decision 1) |
| `/islip-dine-in-menu/` | `/takeout-menu-farmingdale-islip/` | orphan; same |
| `/dine-in-menu/` | `/takeout-menu-farmingdale-islip/` | orphan, 2022 |
| `/2021-dine-in-menu/` | `/takeout-menu-farmingdale-islip/` | orphan, 2021 |
| `/speonk-dine-in-menu/` | `/takeout-menu-speonk/` | in nav; same |
| `/speonk-drink-menu/` | `/speonk/` | in nav; **no drink menu on the rebuild** (decision 2) |
| `/catering-menu-new/` | `/catering-menu/` | in nav |
| `/catering-25/` | `/catering-menu/` | orphan |
| `/speonk-catering-menu/` | `/catering-menu/` | orphan, 2021 |

### Contact, employment, gallery

| Old URL | New URL | Notes |
|---|---|---|
| `/contact-main/` | `/contact/` | in nav |
| `/contact-2/` | `/contact/` | orphan |
| `/contact-speonk-2/` | `/contact/` | orphan |
| `/contact-farmingdale/` | `/contact/` | orphan |
| `/contact-islip-old/` | `/contact/` | orphan |
| `/contact-islip-terrace-2024/` | `/contact/` | orphan |
| `/employment-new/` | `/contact/` | in nav; **no employment page on the rebuild** (decision 3) |
| `/gallery/` | (none) | same URL on the rebuild, no rule needed |
| `/bwg_gallery/marys-pizza/` | `/gallery/` | gallery plugin page (noindex) |
| `/bwg_gallery/new-gallery/` | `/gallery/` | same |

### Old homepages and drafts → `/`

`/homepage/`, `/homepage2021/`, `/home2020/`, `/landing-old22/` (still lists a Wantagh location), `/land/`, `/welcome-to-marys-pizza-and-pasta3/`

These were real homepages at some point and may be bookmarked or linked, so they redirect.

### No rule: let these 404

Pages that were never real content. Redirecting them to `/` gains nothing (Google treats irrelevant redirects to the homepage as a "soft 404" anyway), so they get the new site's 404 page.

| Old URL | What it is |
|---|---|
| `/home-2/` | theme demo page ("Heritage Builders") |
| `/2020/04/28/hello-world/` | WordPress default "Hello world!" post |
| `/2020/04/`, `/category/uncategorized/`, `/author/admin/` | archives listing only that post |
| `/wp-login.php`, `/wp-admin/*`, `/feed/`, `/comments/feed/`, `/xmlrpc.php` | WordPress system URLs |

### PDFs (`/wp-content/uploads/...`)

The site links 28 PDFs; the 8 linked from the current nav are the ones that matter (they may also be in social posts and QR codes).

| Old URL | New URL |
|---|---|
| `/wp-content/uploads/2026/11/Holiday2026.pdf` | `/promotions/` (Holiday Packages card) |
| `/wp-content/uploads/2026/11/BlackFriday2026.pdf` | `/promotions/` (Gift Card Sale card, which ends today) |
| `/wp-content/uploads/2026/01/football-flyer26.pdf` | `/promotions/` (Football Specials card) |
| `/wp-content/uploads/2026/04/FINALFarmIslp-TakeOutMenu2026Web.pdf` | `/takeout-menu-farmingdale-islip/` |
| `/wp-content/uploads/2026/04/2026SpeonkTakeOutMenuWeb.pdf` | `/takeout-menu-speonk/` |
| `/wp-content/uploads/2026/08/catering-menu-new-2026.pdf` | `/catering-menu/` |
| `/wp-content/uploads/2022/07/DineinMenuPastaNite2022WEB.pdf` | decision 4 |
| `/wp-content/uploads/2024/09/CHICKEN-NIGHT-2.pdf`, `/2026/01/chicken-night26.pdf` | decision 4 |
| `/wp-content/uploads/2024/09/Seafood-Night.pdf` | decision 4 |
| `/wp-content/uploads/2024/09/happy-hour-3.pdf` | decision 4 |

The other ~20 are 2020–2025 menus and flyers. Suggest letting them 404 (or one catch-all `/wp-content/uploads/*` → `/` if we'd rather never show a 404). Gallery images under `/wp-content/uploads/photo-gallery/` also 404.

## Decisions needed

1. **Dine-in menus.** The rebuild only has takeout menus. Send dine-in URLs to the takeout menu for that location (as above), or add dine-in menus to the rebuild?
2. **Speonk drink menu.** Send it to `/speonk/` (as above), or add a drink menu, since the bar is a selling point at Speonk?
3. **Employment.** There's no jobs page. Send it to `/contact/` (would need a "Job inquiry" type on the form), to `/`, or build a small `/employment/` page?
4. **Weekly specials** (Pasta Night, Chicken Night, Seafood Night, Happy Hour). Are they still running? If so, they could go on `/promotions/` as cards and the PDFs redirect there. If not, redirect them to the menu pages or let them 404.
5. **Islip Terrace and Farmingdale pages.** Build them before cutover, or cut over with the † rules pointing at `/#locations` for now?

## Before cutover

- Check which URL each Google Business Profile, OpenTable, Yelp, DoorDash/Uber Eats and Instagram listing links to as the website. Those are probably the highest-traffic old URLs, and some may not be in this list.
- If Google Search Console is set up for the old domain, export the top pages report as a cross-check.
- After going live, request a few old URLs and confirm each returns 301 to the right page, then submit the new `sitemap.xml` in Search Console.
