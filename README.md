# lumnik.io — English landing

The international face of Lumnik: a static site. No framework, no build — seven HTML pages,
one stylesheet, a 55-line script. It deploys to any static host.

This is deliberately **not** a translation of [lumnik.fr](https://lumnik.fr/), which stays the
full French commercial site. The two sites point at each other through `hreflang` and otherwise
evolve independently — but they share one spine: **freeze → thaw → motion**, one page per term.

## Structure

```
index.html          the hero and the manifesto — the axis, then the door to it
freeze.html         what the freeze is, and the three dead ends around it
thaw.html           facts, meaning, time — and the observation log
motion.html         the adapter (events, API) and five real cases
architecture.html   three commitments, the lm terminal, the guarantees, docs + code
contact.html        the form
legal.html          legal notice, host, personal data (GDPR)
styles.css          "the light in the freezer" — glacial night + one warm yellow
site.js             thaw bar (reading progress), reveal on scroll, mobile menu
CNAME               lumnik.io
```

The navigation names the three terms of the axis; `architecture.html` is where a security
officer lands, and every page carries the same bar and the same footer.

## Tests

`tests/site_structure_test.py` is the structural contract — Python standard library only, no
dependency, no CI. Run it by hand before a push:

```bash
python3 -m unittest tests/site_structure_test.py
```

It pins the navigation, the one-h1-per-page rule, the canonical URLs, the fact that every local
link and fragment resolves, the anchor geometry that keeps a fragment clear of the sticky bar,
and the claims the split must not roll back. That last one matters because git cannot flag a
stale copy: the six pages do not exist upstream, so a merge declares them up to date.

`site.js` is byte-for-byte the lumnik.fr one and `styles.css` shares its visual language: the
two sites look like one product. Changes are made there and copied here by hand — rare, and
cheaper than a shared build. The stylesheets have drifted where the two sites carry different
sections; the navigation, anchor geometry and mobile menu rules are kept identical.

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

No internal stack, no price list, no implementation detail of the honesty guards. The source
repository *is* linked now — the open-source edition shipped, and the sentence that promised
the link became the link. The site sells the *what* and the *why*; the deep *how* lives in
[docs.lumnik.io](https://docs.lumnik.io).
