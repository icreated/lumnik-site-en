from html.parser import HTMLParser
import html
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
# The visitor's path (lumnik-site spec 2026-10-25): understand on the home, see a replayed
# scenario, try lumnik Open. The same skeleton as lumnik.fr, composed in English.
PAGES = ("index.html", "try.html", "editions.html", "architecture.html", "why.html", "contact.html")
ALL_PAGES = PAGES + ("legal.html",)
TARGET_NAV = (
    ("Scenarios", "scenarios/"),
    ("Security", "architecture.html"),
    ("Editions", "editions.html"),
    ("Docs", "https://docs.lumnik.io"),
    ("Try it", "try.html"),
)
# GitHub Pages cannot redirect server-side: each retired page is a small relay. The fragments
# listed are the ones its target still answers, so an old bookmark lands on its section.
RELAYS = {
    "freeze.html": ("why.html", ("problem",)),
    "thaw.html": ("index.html", ("how", "facts", "meaning", "time")),
    "motion.html": ("scenarios/", ()),
}
# On the scenario pages too: claims this site once made and could not hold.
SITE_FORBIDDEN = (
    "real-time",
    "real time",
    "zero-risk",
    "forever",
    "cites its sources",
    "EU cloud",
    "walkthrough",
    "exists today",
    "cannot be erased",
)
# On the site's own pages only: the virtue words, an invented payload and conversation, a
# maturity copied away from its single source, and every offer of a demo — there is none for
# now; the visitor installs lumnik Open alone.
PAGE_FORBIDDEN = SITE_FORBIDDEN + (
    "honest",
    "zero risk",
    "cite their sources",
    "Book a",
    "quote_unmoved",
    "nobody outside",
    "proxy",
)
HOME_SECTIONS = ("situations", "how", "try", "trust")
# One replayed scenario per kind of problem; each card shows the title the catalogue serves.
FEATURED = (
    "dirty-order-statuses",
    "entity-resolution",
    "export-that-lies",
    "orders-where-they-sleep",
    "zombie-cmms",
    "purchasing-ask-abstains",
)
HERO_H1 = "<h1>Your software stays put.<br>Your data <em>gets back to work</em>.</h1>"
# The demo desk's P-1008 as lumnik fuses it (docs/entities.md, lumnik monorepo): the ERP and the
# CRM agree on the name, disagree on the city, and only the CRM has the email.
P1008 = ("P-1008", "Filtration Lyon 1008", "Lyon", "Villeurbanne", "GOLD", "contact@filtration-lyon.example")
# The two commands and the result line of docs/deploy.md (lumnik monorepo), as up.sh prints them.
CLONE = "git clone https://github.com/icreated/lumnik-open.git && cd lumnik-open"
UP = "./deploy/selfhost/up.sh --build"
HEALTHY = "==> hub is healthy"
DOCS = "https://docs.lumnik.io/"
CATALOGUE = {e["slug"]: e for e in json.loads((ROOT / "scenarios" / "index.json").read_text(encoding="utf-8"))["scenarios"]}


class SitePage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.buttons = []
        self.menu_lists = []
        self.current_links = []
        self.title_parts = []
        self.canonical = ""
        self.description = ""
        self._inside_title = False
        self.h1_count = 0
        self.title_count = 0
        self.canonical_count = 0
        self.description_count = 0
        self.open_graph = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        if tag == "a" and attrs.get("aria-current") == "page":
            self.current_links.append(attrs.get("href", ""))
        if tag == "button":
            self.buttons.append(attrs)
        if tag == "ul" and attrs.get("id") == "menu-principal":
            self.menu_lists.append(attrs)
        if tag == "title":
            self._inside_title = True
            self.title_count += 1
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "")
            self.canonical_count += 1
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content", "")
            self.description_count += 1
        if tag == "meta" and attrs.get("property", "").startswith("og:"):
            self.open_graph[attrs["property"]] = attrs.get("content", "")
        if tag == "h1":
            self.h1_count += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._inside_title = False

    def handle_data(self, data):
        if self._inside_title:
            self.title_parts.append(data)


def load_page(name):
    page = SitePage()
    page.feed((ROOT / name).read_text(encoding="utf-8"))
    return page


def text_of(name):
    return (ROOT / name).read_text(encoding="utf-8")


def between(text, start, end):
    head, sep, rest = text.partition(start)
    if not sep:
        raise AssertionError(f"marker not found: {start}")
    body, sep, _ = rest.partition(end)
    if not sep:
        raise AssertionError(f"marker not found: {end}")
    return body


def section(name, section_id):
    return between(text_of(name), f'id="{section_id}"', "</section>")


def visible(fragment, sep=""):
    """The text a reader sees: tags dropped (or replaced by `sep`), entities decoded."""
    return html.unescape(re.sub(r"<[^>]+>", sep, fragment))


def resolves(source, href):
    """A local href names a file, or a directory GitHub Pages serves through its index.html."""
    target = (ROOT / source).parent / href.partition("#")[0]
    return target.is_file() or (target / "index.html").is_file()


class SiteStructureTest(unittest.TestCase):
    def test_expected_pages_and_relays_exist(self):
        for name in ALL_PAGES + tuple(RELAYS):
            with self.subTest(name=name):
                self.assertTrue((ROOT / name).is_file())

    def test_every_page_exposes_the_global_navigation_in_order(self):
        for name in ALL_PAGES:
            menu = between(text_of(name), '<ul id="menu-principal">', "</ul>")
            items = [(label, href) for href, label in re.findall(r'<a\b[^>]*\bhref="([^"]+)"[^>]*>([^<]+)</a>', menu)]
            with self.subTest(name=name):
                self.assertEqual(list(TARGET_NAV), items)

    def test_the_light_pill_is_the_try_link(self):
        for name in ALL_PAGES:
            menu = between(text_of(name), '<ul id="menu-principal">', "</ul>")
            pills = re.findall(r'<a class="btn btn-lumiere nav-contact" href="([^"]+)"', menu)
            with self.subTest(name=name):
                self.assertEqual(["try.html"], pills)

    def test_mobile_menu_contract_is_present(self):
        for name in ALL_PAGES:
            page = load_page(name)
            menu_buttons = [b for b in page.buttons if b.get("aria-controls") == "menu-principal"]
            with self.subTest(name=name):
                self.assertEqual(1, len(menu_buttons))
                self.assertEqual("false", menu_buttons[0].get("aria-expanded"))
                self.assertEqual(1, len(page.menu_lists))

    def test_mobile_menu_script_supports_keyboard_close(self):
        script = text_of("site.js")
        self.assertIn('event.key === "Escape"', script)
        self.assertIn('setAttribute("aria-expanded"', script)

    def test_each_page_marks_its_own_link_as_current(self):
        current = {
            "index.html": ["index.html"],
            "try.html": ["try.html"],
            "editions.html": ["editions.html"],
            "architecture.html": ["architecture.html"],
            "why.html": [],
            "contact.html": [],
            "legal.html": [],
        }
        for name, expected in current.items():
            with self.subTest(name=name):
                self.assertEqual(expected, load_page(name).current_links)

    def test_every_page_has_unique_metadata(self):
        titles, descriptions = [], []
        for name in PAGES:
            page = load_page(name)
            title = "".join(page.title_parts).strip()
            with self.subTest(name=name):
                self.assertEqual(1, page.title_count)
                self.assertTrue(title)
                self.assertEqual(1, page.description_count)
                self.assertTrue(page.description.strip())
                self.assertEqual(title, page.open_graph.get("og:title"))
                # The meta description is written for a search result, the Open Graph one for
                # a social card: they may differ.
                self.assertTrue(page.open_graph.get("og:description", "").strip())
                self.assertEqual(page.canonical, page.open_graph.get("og:url"))
            titles.append(title)
            descriptions.append(page.description)
        self.assertEqual(len(PAGES), len(set(titles)))
        self.assertEqual(len(PAGES), len(set(descriptions)))

    def test_every_page_has_its_canonical_url(self):
        for name in PAGES:
            expected = "https://lumnik.io/" + ("" if name == "index.html" else name)
            page = load_page(name)
            with self.subTest(name=name):
                self.assertEqual(1, page.canonical_count)
                self.assertEqual(expected, page.canonical)

    def test_every_page_has_one_h1_and_a_working_skip_link(self):
        for name in ALL_PAGES:
            page = load_page(name)
            with self.subTest(name=name):
                self.assertEqual(1, page.h1_count)
                self.assertIn("contenu", page.ids)
                self.assertIn("#contenu", page.links)

    def test_local_links_and_fragments_resolve(self):
        for name in ALL_PAGES:
            for href in load_page(name).links:
                if href.startswith(("http://", "https://", "mailto:")):
                    continue
                target, _, fragment = href.partition("#")
                target = target or name
                with self.subTest(name=name, href=href):
                    self.assertTrue(resolves(name, target))
                    if fragment:
                        self.assertIn(fragment, load_page(target).ids)

    def test_no_page_links_a_relay(self):
        for name in ALL_PAGES:
            for href in load_page(name).links:
                with self.subTest(name=name, href=href):
                    self.assertNotIn(href.partition("#")[0], RELAYS)

    def test_only_the_homepage_announces_language_alternates(self):
        home = text_of("index.html")
        for lang in ('hreflang="en"', 'hreflang="fr"', 'hreflang="x-default"'):
            self.assertIn(lang, home)
        for name in ALL_PAGES[1:]:
            with self.subTest(name=name):
                self.assertNotIn("hreflang=", text_of(name))

    def test_every_footer_leads_to_the_scenarios_the_try_page_and_the_why(self):
        for name in ALL_PAGES:
            footer = between(text_of(name), "<footer>", "</footer>")
            for href in ("scenarios/", "try.html", "why.html", "contact.html", "legal.html"):
                with self.subTest(name=name, href=href):
                    self.assertIn(f'href="{href}"', footer)

    def test_fragment_destinations_clear_the_sticky_navigation(self):
        """Anchor geometry is one calculation, not three independent numbers.

        A fragment inside a .reveal is scrolled to while the reveal still holds its content
        down; the class lands a moment later and lifts everything. Without reserving that lift
        in the scroll-margin, the heading rises under the sticky bar.
        """
        styles = text_of("styles.css")
        self.assertIn("--nav-h: 64px;", styles)
        self.assertIn("--anchor-gap: 20px;", styles)
        self.assertIn("--reveal-lift: 30px;", styles)
        self.assertIn("[id] { scroll-margin-top: calc(var(--nav-h) + var(--anchor-gap)); }", styles)
        self.assertIn(
            ".reveal [id] { scroll-margin-top: "
            "calc(var(--nav-h) + var(--anchor-gap) + var(--reveal-lift)); }",
            styles,
        )
        self.assertIn("height: var(--nav-h);", styles)
        self.assertIn("transform: translateY(var(--reveal-lift));", styles)
        reduced = styles.split("@media (prefers-reduced-motion: reduce) {", 1)[1]
        self.assertIn(":root { --reveal-lift: 0px; }", reduced)

    def test_the_pill_keeps_dark_text_on_its_own_page(self):
        """`nav a[aria-current="page"]` paints the light yellow and outranks `nav .nav-contact`
        on specificity: on its own page the pill would read yellow on yellow. The pill rule,
        after the current-page one, keeps its ink dark."""
        styles = text_of("styles.css")
        self.assertIn('nav .nav-contact,\nnav a.nav-contact[aria-current="page"] { color: var(--nuit); }', styles)
        self.assertLess(
            styles.index('nav a[aria-current="page"] {'),
            styles.index('nav a.nav-contact[aria-current="page"]'),
        )

    def test_the_copy_avoids_the_ruled_out_wordings(self):
        for name in ALL_PAGES:
            page_text = text_of(name)
            for word in PAGE_FORBIDDEN:
                with self.subTest(name=name, word=word):
                    self.assertNotIn(word, page_text)


class HomepageTest(unittest.TestCase):
    def home(self):
        return text_of("index.html")

    def hero(self):
        return between(self.home(), '<header class="heros">', "</header>")

    def test_the_sections_follow_the_journey(self):
        after_hero = self.home().split("</header>", 1)[1]
        self.assertEqual(list(HOME_SECTIONS), re.findall(r'<section[^>]*\bid="([^"]+)"', after_hero))

    def test_the_hero_says_why_and_opens_both_doors(self):
        hero = self.hero()
        self.assertIn(HERO_H1, hero)
        ctas = between(hero, '<div class="heros-ctas">', "</div>")
        self.assertIn('href="scenarios/"', ctas)
        self.assertIn('href="try.html"', ctas)

    def test_the_hero_record_is_the_demo_desk_p1008(self):
        record = between(self.hero(), "<!-- record:start -->", "<!-- record:end -->")
        for value in P1008:
            with self.subTest(value=value):
                self.assertIn(value, record)
        self.assertIn("Fictional", record)
        self.assertIn(DOCS + "entities/", record)

    def test_the_featured_scenarios_are_published_and_titled_as_served(self):
        cards = dict(re.findall(r'<a class="porte scenario" href="scenarios/([a-z0-9-]+)/">(.*?)</a>',
                                section("index.html", "situations"), re.S))
        self.assertEqual(sorted(FEATURED), sorted(cards))
        for slug in FEATURED:
            card, served = cards[slug], CATALOGUE[slug]
            with self.subTest(slug=slug):
                self.assertTrue(resolves("index.html", f"scenarios/{slug}/"))
                self.assertEqual(served["title"], visible(between(card, "<h3>", "</h3>")))
                self.assertIn(f'<span class="edition">{served["edition"].capitalize()}</span>', card)

    def test_the_situations_lead_to_the_whole_catalogue(self):
        self.assertIn('<a class="btn btn-givre" href="scenarios/">', section("index.html", "situations"))

    def test_the_five_moves_answer_the_old_thaw_fragments(self):
        how = section("index.html", "how")
        for verb in ("Read", "Repair", "Merge", "Watch", "Serve"):
            with self.subTest(verb=verb):
                self.assertIn(f"<h3>{verb}</h3>", how)
        for fragment in ("facts", "meaning", "time"):
            with self.subTest(fragment=fragment):
                self.assertIn(f'id="{fragment}"', how)

    def test_the_try_section_shows_the_real_install(self):
        try_section = visible(section("index.html", "try"))
        for line in (CLONE, UP, HEALTHY):
            with self.subTest(line=line):
                self.assertIn(line, try_section)
        self.assertIn('href="try.html"', section("index.html", "try"))

    def test_trust_links_to_its_sources_and_opens_three_doors(self):
        trust = section("index.html", "trust")
        for href in (DOCS + "security/", DOCS + "where-lumnik-stands/", DOCS + "integration-as-code/",
                     "https://github.com/icreated/lumnik-open", "scenarios/", "architecture.html"):
            with self.subTest(href=href):
                self.assertIn(f'href="{href}"', trust)


class TryPageTest(unittest.TestCase):
    def test_the_try_page_walks_the_real_install(self):
        page = text_of("try.html")
        for line in (CLONE, UP, HEALTHY):
            with self.subTest(line=line):
                self.assertIn(line, visible(page))
        for href in ("https://github.com/icreated/lumnik-open/releases/latest",
                     DOCS + "quickstart/prerequisites/", DOCS + "quickstart/installer/", DOCS + "wow/",
                     "scenarios/", "editions.html"):
            with self.subTest(href=href):
                self.assertIn(f'href="{href}"', page)

    def test_the_try_page_asks_for_nothing(self):
        self.assertNotIn("<form", text_of("try.html"))


class EditionsPageTest(unittest.TestCase):
    def test_three_tiers_that_lead_to_try_or_to_contact(self):
        page = text_of("editions.html")
        self.assertEqual(3, page.count('<div class="tier'))
        hub = re.search(r'<div class="tier">(.*?)<div class="tier pro">', page, re.S).group(1)
        self.assertIn('href="try.html"', hub)
        self.assertIn('href="contact.html"', page)


class ContactPageTest(unittest.TestCase):
    def test_the_form_still_posts_where_it_did(self):
        page = text_of("contact.html")
        self.assertIn('action="https://formspree.io/f/xqpzpwow"', page)
        self.assertIn('<input type="hidden" name="objet" value="Contact lumnik.io">', page)


class SecurityPageTest(unittest.TestCase):
    def test_the_guarantees_an_it_team_can_check(self):
        page = text_of("architecture.html")
        self.assertIn('class="garanties"', page)
        # The application cannot rewrite the audit trail, and a retention purge trims it: the
        # page says both (the old "cannot be erased" was false).
        self.assertIn("365 days", page)
        for href in (DOCS + "security/", DOCS + "reversibility/", DOCS + "where-lumnik-stands/",
                     "https://github.com/icreated/lumnik-open"):
            with self.subTest(href=href):
                self.assertIn(f'href="{href}"', page)


class RelayTest(unittest.TestCase):
    def test_each_relay_sends_its_visitor_on_with_the_fragment(self):
        for old, (target, _) in RELAYS.items():
            text = text_of(old)
            canonical = "https://lumnik.io/" + ("" if target == "index.html" else target)
            with self.subTest(old=old):
                self.assertIn(f'<meta http-equiv="refresh" content="0; url={target}">', text)
                self.assertIn(f'<link rel="canonical" href="{canonical}">', text)
                self.assertIn('<meta name="robots" content="noindex">', text)
                self.assertIn(f'location.replace("{target}" + location.hash)', text)
                self.assertIn(f'href="{target}"', text)
                self.assertTrue(resolves(old, target))

    def test_every_kept_fragment_lands_on_its_section(self):
        for old, (target, anchors) in RELAYS.items():
            for anchor in anchors:
                with self.subTest(old=f"{old}#{anchor}"):
                    self.assertIn(anchor, load_page(target).ids)


# --- scenarios/: replayed scenarios, a publication artefact of lumnik-scenario -------------------
#
# Written only by lumnik-scenario's tools/scenario-site/publish.sh; the site checks what it serves.

SCENARIO_PAGES = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "scenarios").rglob("*.html"))


class ScenarioPagesTest(unittest.TestCase):
    def test_every_published_scenario_has_its_page(self):
        for slug in CATALOGUE:
            with self.subTest(slug=slug):
                self.assertIn(f"scenarios/{slug}/index.html", SCENARIO_PAGES)

    def test_local_links_resolve(self):
        for name in SCENARIO_PAGES:
            hrefs = load_page(name).links + re.findall(r'<(?:script|link)[^>]+(?:src|href)="([^"]+)"', text_of(name))
            for href in hrefs:
                if href.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                with self.subTest(name=name, href=href):
                    self.assertTrue(resolves(name, href))

    def test_the_copy_avoids_the_claims_this_site_could_not_hold(self):
        for name in SCENARIO_PAGES:
            text = visible(text_of(name), " ").lower()
            for word in SITE_FORBIDDEN:
                with self.subTest(name=name, word=word):
                    self.assertNotIn(word.lower(), text)


if __name__ == "__main__":
    unittest.main()
