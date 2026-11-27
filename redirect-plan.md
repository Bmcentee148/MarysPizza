# Redirect plan: old WordPress site → rebuild

Crawled 2026-11-27 from `https://maryspizzaandpasta.com` (Yoast sitemap index, all 5 sub-sitemaps, then every internal link followed). 44 URLs in the sitemap, all return 200; the crawl found no extra pages beyond WordPress system URLs. A `site:` search showed nothing else indexed. Two broken links (`/lincoln-wortman-ave/`, `/projects/`) come from a leftover theme demo page and already 404.

**Status: written.** All 49 rules are in `netlify.toml` (301s), and the build fails if a target stops being a real page. Netlify matches with or without the trailing slash, so one rule per path is enough.

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

**Location pages:** `/speonk/` and `/islip-terrace/` are built (Islip Terrace still has photo placeholders). `/farmingdale/` will be built before cutover; its rules already point at it, so don't switch the domain until it exists.

### Location pages (top priority: most likely what Google Business Profile and other listings link to)

| Old URL | New URL | Notes |
|---|---|---|
| `/home-speonk/` | `/speonk/` | in nav |
| `/home-islip/` | `/islip-terrace/` | in nav |
| `/home-farmingdale/` | `/farmingdale/` | in nav |
| `/home-islip-2024/` | `/islip-terrace/` | old version |
| `/home-farmingdale-2025/` | `/farmingdale/` | old version |
| `/about-us-speonk/` | `/speonk/` | in nav; store story lives on the location page now |
| `/about-us-islip/` | `/islip-terrace/` | in nav |
| `/about-us-farmingdale/` | `/farmingdale/` | in nav |

### Menus

| Old URL | New URL | Notes |
|---|---|---|
| `/menus/` | `/takeout-menu-farmingdale-islip/` | in nav; Farmingdale/Islip hub |
| `/menus-speonk/` | `/takeout-menu-speonk/` | in nav; Speonk hub |
| `/islip-farm-takeout-menu/` | `/takeout-menu-farmingdale-islip/` | in nav |
| `/take-out-menu/` | `/takeout-menu-farmingdale-islip/` | orphan, 2022 |
| `/speonk-takeout-menu/` | `/takeout-menu-speonk/` | in nav |
| `/speonk-takeoutmenu/` | `/takeout-menu-speonk/` | orphan, 2021 |
| `/farmingdale-dineinmenu/` | `/dine-in-menu-farmingdale/` | in nav |
| `/islip-dine-in-menu/` | `/dine-in-menu-islip-terrace/` | orphan (the old nav linked Islip to the Farmingdale page) |
| `/dine-in-menu/` | `/dine-in-menu-farmingdale/` | orphan, 2022; old shared dine-in menu, either store fits |
| `/2021-dine-in-menu/` | `/dine-in-menu-farmingdale/` | orphan, 2021; same |
| `/speonk-dine-in-menu/` | `/dine-in-menu-speonk/` | in nav |
| `/speonk-drink-menu/` | `/dine-in-menu-speonk/` | in nav; the Speonk dine-in menu has the full drink list (its Drinks section is one tap away; redirects skip the `#drinks` part because Netlify may not keep it) |
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
| `/employment-new/` | `/contact/?type=employment` | in nav; opens the form with Employment selected |
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
| `/wp-content/uploads/2022/07/DineinMenuPastaNite2022WEB.pdf` | `/promotions/` (weekly specials) |
| `/wp-content/uploads/2024/09/CHICKEN-NIGHT-2.pdf`, `/2026/01/chicken-night26.pdf` | `/promotions/` (weekly specials) |
| `/wp-content/uploads/2024/09/Seafood-Night.pdf` | `/promotions/` (weekly specials) |
| `/wp-content/uploads/2024/09/happy-hour-3.pdf` | `/promotions/` (weekly specials) |

The other ~20 are 2020–2025 menus and flyers. Suggest letting them 404 (or one catch-all `/wp-content/uploads/*` → `/` if we'd rather never show a 404). Gallery images under `/wp-content/uploads/photo-gallery/` also 404.

## Decisions

1. **Dine-in menus. Done:** separate dine-in and takeout menus. Each store has its own dine-in page (`/dine-in-menu-speonk/`, `/dine-in-menu-farmingdale/`, `/dine-in-menu-islip-terrace/`); takeout stays at `/takeout-menu-speonk/` and the shared `/takeout-menu-farmingdale-islip/`.
2. **Speonk drink menu. Changed:** the Speonk dine-in menu includes the full bar and wine list, so `/speonk-drink-menu/` redirects to that page (`/dine-in-menu-speonk/`, whose Drinks section is one tap away).
3. **Employment. Done:** `/employment-new/` redirects to `/contact/?type=employment`, which opens the form with the new Employment inquiry type selected.
4. **Weekly specials. Done:** no full specials menus on the site. The `#weekly-specials` card on `/promotions/` summarizes Chicken Night (Mon–Wed 4–9pm, $28) and Seafood Night (Thursday 4–9pm, $30), Farmingdale and Islip Terrace only; Speonk has no weekly specials. All old specials PDFs redirect to `/promotions/`, including Pasta Night and Happy Hour, which aren't on the card (not confirmed as running).
5. **Islip Terrace and Farmingdale pages. Decided:** both get built before cutover, and their rules point straight at them.

## Before cutover

- Check which URL each Google Business Profile, OpenTable, Yelp, DoorDash/Uber Eats and Instagram listing links to as the website. Those are probably the highest-traffic old URLs, and some may not be in this list.
- If Google Search Console is set up for the old domain, export the top pages report as a cross-check.
- After going live, request a few old URLs and confirm each returns 301 to the right page, then submit the new `sitemap.xml` in Search Console.
