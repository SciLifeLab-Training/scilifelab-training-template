"""
The registration banner on the overview page.

The banner has three states, decided by the dates in data/website.yml:

- before the opening date: "Registration opens soon";
- from the opening date to the closing date: "Registration is open",
  with the link to the registration page;
- after the closing date: "Registration is closed", or nothing at all
  (after_closing: hide).

All states are written into the page, and a small script shows the
right one, based on the visitor's date. The banner therefore changes on
the opening and closing day by itself, without rebuilding the website.
Without JavaScript, the state on the day the website was built is shown.
"""

from datetime import date, datetime
from html import escape


def _parse_date(value):

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return datetime.strptime(
        str(value),
        "%Y-%m-%d",
    ).date()


def _format_date(value):

    return _parse_date(value).strftime("%-d %B %Y")


def _before_banner(opening_date):
    """Registration has not opened yet."""

    return f"""
<div class="course-registration">

<div class="course-registration-content">

<div class="course-registration-title">
Registration opens soon
</div>

<div class="course-registration-message">
Registration for this training opens on {_format_date(opening_date)}.
</div>

</div>

</div>
""".strip()


def _open_banner(registration, closing_date):
    """Registration is open. Needs a registration link."""

    url = registration.get("url")

    if not url:
        return ""

    cost = registration.get("cost") or {}

    amount = cost.get("amount")
    currency = cost.get("currency")
    note = cost.get("note")

    details_html = []

    if closing_date:
        details_html.append(
            '<div class="course-registration-deadline">'
            f"Register by {_format_date(closing_date)}."
            "</div>"
        )

    if amount is not None and currency:
        details_html.append(
            '<div class="course-registration-fee">'
            f"Cost: {amount} {currency}"
            "</div>"
        )

    if note:
        details_html.append(
            '<div class="course-registration-note">'
            f"{note}"
            "</div>"
        )

    details_html = "\n".join(details_html)

    return f"""
<div class="course-registration">

<div class="course-registration-content">

<div class="course-registration-title">
Registration is open
</div>

{details_html}

</div>

<a
    class="course-registration-button"
    href="{escape(str(url), quote=True)}">
    Register for this training →
</a>

</div>
""".strip()


def _closed_banner(after_closing):
    """Registration has closed. Nothing when after_closing is "hide"."""

    if after_closing == "hide":
        return ""

    return """
<div class="course-registration">

<div class="course-registration-content">

<div class="course-registration-title">
Registration is closed
</div>

<div class="course-registration-message">
Registration for this training is now closed.
</div>

<div class="course-registration-note">
For questions or more information, please contact the training team.
</div>

</div>

</div>
""".strip()


def _state(today, opening_date, closing_date):
    """The state of registration on a given day."""

    if today < opening_date:
        return "before"

    if closing_date is None or today <= closing_date:
        return "open"

    return "closed"


# Shows the banner that matches the visitor's date. The dates are
# compared as YYYY-MM-DD text, which sorts the same way as the dates.
SWITCH_SCRIPT = """
<script>
(function () {
  var banner = document.currentScript.previousElementSibling;
  if (!banner || !banner.dataset.opening) {
    return;
  }

  var now = new Date();
  var today = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, "0"),
    String(now.getDate()).padStart(2, "0")
  ].join("-");

  var opening = banner.dataset.opening;
  var closing = banner.dataset.closing;
  var state =
    today < opening ? "before" :
    (!closing || today <= closing) ? "open" :
    "closed";

  banner.querySelectorAll("[data-registration-state]").forEach(function (part) {
    part.hidden = part.dataset.registrationState !== state;
  });
})();
</script>
""".strip()


def render_registration(registration, today=None):

    if not registration.get("enabled"):
        return ""

    opening_date = registration.get("opening_date")
    closing_date = registration.get("closing_date")
    after_closing = registration.get("after_closing", "hide")

    if not opening_date:
        return ""

    opening_date = _parse_date(opening_date)
    closing_date = _parse_date(closing_date) if closing_date else None

    banners = {
        "before": _before_banner(opening_date),
        "open": _open_banner(registration, closing_date),
        "closed": _closed_banner(after_closing),
    }

    # The state on the day the website is built: shown when JavaScript
    # is not available, and before the script has run.
    build_state = _state(today or date.today(), opening_date, closing_date)

    parts = [
        f'<div data-registration-state="{state}"'
        f'{"" if state == build_state else " hidden"}>\n\n'
        f"{html}\n\n"
        "</div>"
        for state, html in banners.items()
        if html
    ]

    if not parts:
        return ""

    closing_attribute = (
        f' data-closing="{closing_date.isoformat()}"' if closing_date else ""
    )

    return (
        '<div class="course-registration-switch" '
        f'data-opening="{opening_date.isoformat()}"{closing_attribute}>\n\n'
        + "\n\n".join(parts)
        + "\n\n</div>\n"
        + SWITCH_SCRIPT
    )
