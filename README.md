# lumnik.io — English landing

The international face of Lumnik: a static, focused landing page. No framework, no build —
two HTML pages, one stylesheet, a 30-line script. It deploys to any static host.

This is deliberately **not** a translation of [lumnik.fr](https://lumnik.fr/), which stays the
full French commercial site. This page carries the hero, the three thaws, the adapter, the
honesty bar, the docs and a contact form — nothing else. The two sites point at each other
through `hreflang` and otherwise evolve independently.

## Structure

```
index.html   the landing (hero, the problem, three thaws, time, the adapter,
             honesty, docs + open-source teaser, contact)
legal.html   legal notice, host, personal data (GDPR)
styles.css   "the light in the freezer" — glacial night + one warm yellow
site.js      thaw bar (reading progress) + reveal on scroll
CNAME        lumnik.io
```

`styles.css` and `site.js` are copied byte-for-byte from the lumnik.fr repository: the two
sites share one visual language. Changes to it are made there and copied here by hand — rare,
and cheaper than a shared build.

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

## What this page deliberately does not say

No internal stack, no price list, no implementation detail of the honesty guards, and no link
to the source repository until the open-source edition ships in September 2026 — a dead link
would be worse than a promise. The page sells the *what* and the *why*; the deep *how* lives
in [docs.lumnik.io](https://docs.lumnik.io).
