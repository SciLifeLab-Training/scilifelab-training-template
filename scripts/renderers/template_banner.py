"""The "Want to use this template?" banner on the overview page."""

USER_GUIDE_URL = (
    "https://scilifelab-training.github.io/"
    "scilifelab-training-template-user-guide/"
)


def render_template_banner(website):
    """The banner, shown only when website.template is true."""

    if website.get("template") is not True:
        return ""

    return (
        "::: {.template-banner}\n"
        "**Want to use this template?** Read the User Guide for "
        "step-by-step instructions on setting up and customising your "
        f"training page. [View the User Guide →]({USER_GUIDE_URL})\n"
        ":::\n"
    )
