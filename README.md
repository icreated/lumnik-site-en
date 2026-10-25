# lumnik.io — English landing

The international face of Lumnik: a static site. No framework, no build — seven HTML pages,
one stylesheet, a 55-line script. It deploys to any static host.

Since 2026-10-25 it shares the skeleton of [lumnik.fr](https://lumnik.fr/) — the visitor's path
is the same: understand on the home, see a replayed scenario, install lumnik Open. The copy is
composed in English, never translated. No demo is offered. The spec lives in the French repo:
`lumnik-site/docs/superpowers/specs/2026-10-25-sites-simplification-design.md`.

## Structure

```
index.html          the home: the hero (the P-1008 record), six scenarios, five moves, try it, trust
try.html            install lumnik Open, step by step — no form
editions.html       Hub (lumnik Open, free) · Pro · Enterprise
architecture.html   "Security": the guarantees an IT team can verify, and where
why.html            the manifesto: freeze → thaw → motion, and the name (footer)
contact.html        the form
legal.html          legal notice, host, personal data (GDPR)
freeze.html, thaw.html, motion.html
                    relays to why.html, the home and the scenarios, fragment included
styles.css          "the light in the freezer" — glacial night + one warm yellow
site.js             thaw bar (reading progress), reveal on scroll, mobile menu
CNAME               lumnik.io
scenarios/          the replayed scenarios — a PUBLICATION ARTEFACT, see below
```

The six home cards show the titles `scenarios/index.json` serves: a scenario renamed or retired
fails the structural test.

## `scenarios/` — never edit it here

It comes from the `lumnik-scenario` repository and is rewritten whole by
`tools/scenario-site/publish.sh` (one branch, one PR) from each scenario's validated candidate.
Fix the scenario, replay it, publish again.

## Tests

`tests/site_structure_test.py` is the structural contract — Python standard library only, no
dependency, no CI. Run it by hand before a push:

```bash
python3 -m unittest tests/site_structure_test.py
```

It pins the pages and the relays, the navigation and the current page, the one-h1-per-page rule,
the canonical URLs, every local link and fragment, the P-1008 values, the scenario cards, the real
install commands, the guarantees (with the 365-day audit purge), and the wordings this site once
used and could not hold ("cites its sources", "EU cloud", "exists today", a demo offer…).

`site.js` is byte-for-byte the lumnik.fr one and `styles.css` shares its visual language: the
two sites look like one product. Changes are made there and copied here by hand — rare, and
cheaper than a shared build. The navigation, anchor geometry and mobile menu rules are kept
identical, and so is the block « Le passage de simplification (2026-10-25) » at the end of both
sheets: copy the block, never diff the files.

## Visual direction

- **Metaphor:** frozen data (glacial night, frost, grain texture) crossed by ONE warm light —
  the yellow `#ffd24a`, treated as actual light (hero halo, thawing words, CTAs, progress bar).
- **Type:** Fraunces (headings) · Archivo (body) · IBM Plex Mono (technical labels),
  loaded from Google Fonts.
- Honors `prefers-reduced-motion`.

## Deployment

GitHub Pages serves `main` from the repository root: zero build, zero workflow — a push to
`main` is deployed as-is. `CNAME` pins the apex domain. On the DNS side, four A records point at
the GitHub Pages addresses.

Test locally: `python3 -m http.server 8000`, then http://localhost:8000

## What the site deliberately does not say

No internal stack, no price list, no implementation detail of the guards. The source
repository *is* linked now — the open-source edition shipped, and the sentence that promised
the link became the link. The site sells the *what* and the *why*; the deep *how* lives in
[docs.lumnik.io](https://docs.lumnik.io).
