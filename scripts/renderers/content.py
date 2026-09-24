from pathlib import Path

from renderers.navbar import (
    render_navbar_meta,
    render_navbar_links,
)

from renderers.footer import render_footer


ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = ROOT / "content"

def render_content_navigation(sections):
    if not sections:
        return ""

    html = []

    html.append("""
<aside class="course-content-navigation">
<div class="course-content-navigation-title">
Course content
</div>
""".strip())

    for section in sections:
        html.append(
            f"""
<div class="course-content-navigation-section">
<div class="course-content-navigation-section-title">
{section["title"]}
</div>
<ul>
""".strip()
        )

        for page in section["pages"]:
            href = page["path"].relative_to(CONTENT_DIR).with_suffix(".html")

            html.append(
                f"""
<li>
<a
    href=""
    data-content-page="{href}">
    {page["title"]}
</a>
</li>
""".strip()
            )

        html.append("""
</ul>
</div>
""".strip())

    html.append("""
</aside>
""".strip())

    return "\n".join(html)

def render_content_navbar(course, website, available_pages):
    meta = render_navbar_meta(course)
    links = render_navbar_links(website, available_pages)

    return """
<div class="course-navbar">
<div class="course-navbar-layout">
<div class="course-navbar-content">
<div class="course-navbar-title">
""" + meta + """
</div>
<div class="course-navbar-menu">
<div class="course-navbar-links">
""" + links + """
</div>
</div>
</div>
<div class="course-navbar-brand">
<img
    src=""
    data-course-asset="img/scilifelab-logo-full-neg.png"
    class="course-navbar-logo"
    alt="SciLifeLab Training">
</div>
</div>
</div>

<script>
document.documentElement.classList.add("course-content-page");

document.addEventListener("DOMContentLoaded", function () {

    const navbar = document.querySelector(".course-navbar");
    const footer = document.querySelector(".landing-footer");

    /*
     * Move the shared site chrome outside Quarto's
     * main-content / TOC grid.
     */

    if (navbar) {
        document.body.insertBefore(navbar, document.body.firstChild);
    }

    if (footer) {
        document.body.appendChild(footer);
    }

    const pathname = window.location.pathname;
    const contentMarker = "/content/";

    const siteRoot = pathname.includes(contentMarker)
        ? pathname.split(contentMarker)[0] + "/"
        : "/";

    document.querySelectorAll(
        ".course-content-navigation a[data-content-page]"
    ).forEach(function (link) {

        const page = link.dataset.contentPage;
        const href = siteRoot + "content/" + page;

        link.href = href;

        if (pathname.endsWith("/" + page)) {
            link.classList.add("course-content-navigation-link-active");
        }

    });

    const isContentPage =
        pathname.includes("/content/");

    const currentPage =
        pathname.split("/").pop() || "index.html";

    document.querySelectorAll(
        ".course-navbar-link, .course-navbar-dropdown-link"
    ).forEach(function (link) {

        const page = link.dataset.page;

        if (!page) {
            return;
        }

        let href;

        if (page === "content/index.qmd") {
            href = siteRoot + "content/index.html";
        } else {
            href = siteRoot + page.replace(".qmd", ".html");
        }

        link.href = href;

        if (
            isContentPage
                ? page === "content/index.qmd"
                : href.endsWith(currentPage)
        ) {
            link.classList.add("course-navbar-link-active");
        }

    });

    document.querySelectorAll("[data-course-asset]").forEach(function (image) {
        image.src = siteRoot + image.dataset.courseAsset;
    });

    const contentNavigation =
        document.querySelector(".course-content-navigation");

    const documentContent =
        document.querySelector("#quarto-document-content");

    if (contentNavigation && documentContent) {

        const layout = document.createElement("div");

        layout.className = "course-content-layout";

        documentContent.parentNode.insertBefore(
            layout,
            documentContent
        );

        layout.appendChild(contentNavigation);
        layout.appendChild(documentContent);
    }

});
</script>
""".strip()


def render_content_footer(website):
    footer = render_footer(website)

    footer = footer.replace(
        'src="img/github-neg.png"',
        'src="" data-course-asset="img/github-neg.png"'
    )

    return footer