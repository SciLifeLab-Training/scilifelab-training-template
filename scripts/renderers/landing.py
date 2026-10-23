"""
Render the landing page sections from the data files.

Each function returns a Quarto fragment that is written to
_generated/ and included by the matching file in _sections/.
The HTML classes are the same as in the original hand-written
sections, so styles.css applies unchanged.
"""

import html


USER_GUIDE_URL = (
    "https://scilifelab-training.github.io/"
    "scilifelab-training-template-user-guide/"
)


def _attr(value):
    """Escape a value for use in an HTML attribute."""

    return html.escape(str(value or ""), quote=True)


def _text(value):
    """Return a value as a single-line string, or "" when empty."""

    if value is None:
        return ""

    return " ".join(str(value).split())


def _list(values):
    """Return a list of non-empty single-line strings."""

    return [_text(value) for value in (values or []) if _text(value)]


def _names(team, role):
    """Return the names of the team members with a role."""

    return [
        _text(member.get("name"))
        for member in team.get("members") or []
        if role in (member.get("roles") or [])
        and _text(member.get("name"))
    ]


# ---------------------------------------------------------
# Template banner
# ---------------------------------------------------------

def render_template_banner(website):
    """The "Want to use this template?" banner, in template mode only."""

    if website.get("template") is not True:
        return ""

    return f"""
::: {{.template-banner}}
**Want to use this template?** Read the User Guide for step-by-step instructions on setting up and customising your training page. [View the User Guide →]({USER_GUIDE_URL})
:::
""".strip() + "\n"


# ---------------------------------------------------------
# Hero
# ---------------------------------------------------------

# Height of a logo in pixels when website.yml gives none.
DEFAULT_LOGO_HEIGHT = 56


def _logo_height(logo):
    """The height of a logo in pixels: its height in website.yml, or
    the default. On smaller screens, all logos shrink in proportion."""

    height = logo.get("height")

    if height in (None, ""):
        return DEFAULT_LOGO_HEIGHT

    return f"{float(height):g}"


def render_hero_brand(website):
    """The logos at the top of the landing page."""

    logos = (website.get("hero") or {}).get("logos") or []

    # The primary logo (primary: true) is always shown last, on the
    # right. The other logos keep the order of the list.
    logos = sorted(logos, key=lambda logo: logo.get("primary") is True)

    items = [
        '<div class="hero__brand-item">\n'
        f'  <img src="{_attr(logo.get("src"))}" '
        f'alt="{_attr(logo.get("alt"))}" class="hero__partner-logo" '
        f'style="--logo-height: {_logo_height(logo)}px;">\n'
        "</div>"
        for logo in logos
        if logo.get("src")
    ]

    return "\n".join(items) + "\n"


def render_hero_copy(course):
    """The training title and subtitle."""

    parts = [
        ":::{.hero__title}\n"
        f"{_text(course.get('title'))}\n"
        ":::"
    ]

    subtitle = _text(course.get("subtitle"))

    if subtitle:
        parts.append(
            ":::{.hero__subtitle}\n"
            f"{subtitle}\n"
            ":::"
        )

    return "\n\n".join(parts) + "\n"


# ---------------------------------------------------------
# Information cards
# ---------------------------------------------------------

def _card(card_class, icon, heading, body):
    """One information card with an icon, a heading and a body."""

    return f"""
:::{{.info-card .{card_class}}}
<div class="info-card__header">
  <span class="info-card__icon" aria-hidden="true">
    <img src="img/icons/{icon}" alt="" class="info-card__icon-img">
  </span>
  <h2 class="info-card__heading">{html.escape(heading)}</h2>
</div>

{body}
:::
""".strip()


def _card_copy(markdown):
    return f":::{{.card-copy}}\n{markdown.strip()}\n:::"


def _people_list(names):
    items = "\n".join(f"- {name}" for name in names)
    return f":::{{.people-list}}\n{items}\n:::"


def render_top_cards(course):
    """
    The training content, learning outcomes, keywords and topics
    cards. A card without content is left out.
    """

    cards = []

    description = str(course.get("description") or "").strip()

    if description:
        cards.append(_card(
            "info-card--course-content",
            "book-stack.svg",
            "Training content",
            _card_copy(description),
        ))

    outcomes = _list(course.get("learning_outcomes"))

    if outcomes:
        cards.append(_card(
            "info-card--learning-outcomes",
            "target.svg",
            "Learning outcomes",
            _card_copy("\n".join(
                f"{number}. {outcome}"
                for number, outcome in enumerate(outcomes, start=1)
            )),
        ))

    keywords = _list(course.get("keywords"))

    if keywords:
        cards.append(_card(
            "info-card--keywords",
            "tag.svg",
            "Keywords",
            _card_copy("\n".join(f"- {keyword}" for keyword in keywords)),
        ))

    topics = _list(course.get("topics"))

    if topics:
        cards.append(_card(
            "info-card--topics-covered",
            "lightbulb.svg",
            "Topics covered",
            _card_copy("\n".join(f"- {topic}" for topic in topics)),
        ))

    if not cards:
        return ""

    return (
        ":::{.cards-grid .cards-grid--top}\n"
        + "\n\n".join(cards)
        + "\n:::\n"
    )


def render_bottom_cards(team):
    """The founders and contributors cards, from data/team.yml."""

    cards = []

    founders = _names(team, "Founder")

    if founders:
        cards.append(_card(
            "info-card--founders",
            "person.svg",
            "Founders",
            _people_list(founders),
        ))

    contributors = _names(team, "Contributor")

    if contributors:
        cards.append(_card(
            "info-card--contributors",
            "group.svg",
            "Contributors",
            _people_list(contributors),
        ))

    if not cards:
        return ""

    return (
        ":::{.cards-grid .cards-grid--bottom}\n"
        + "\n\n".join(cards)
        + "\n:::\n"
    )


# ---------------------------------------------------------
# "All training instances" banner
# ---------------------------------------------------------

def render_instances_band_media(website):
    """The decorative image of the "All training instances" banner."""

    image = _text((website.get("instances_band") or {}).get("image"))

    if not image:
        return ""

    return (
        '<div class="instances-band__media" aria-hidden="true">\n'
        f'  <img src="{_attr(image)}" alt="" class="instances-band__image">\n'
        "</div>\n"
    )
