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
<nav class="course-content-navigation" aria-label="Course content">
    <div class="course-content-navigation-inner">
        <div class="course-content-navigation-scroll">
""".strip())

    html.append("""
<a
    class="course-content-navigation-toggle course-content-navigation-introduction"
    href=""
    data-content-page="index.html">
    Introduction
</a>
""".strip())

    for section in sections:
        label = section["label"]
        title = section["title"]

        html.append(
            f"""
<div class="course-content-navigation-dropdown">
    <button
        class="course-content-navigation-toggle"
        type="button"
        aria-haspopup="true"
        aria-expanded="false"
        title="{title}">
        {label}
        <i class="bi bi-chevron-down course-content-navigation-icon"></i>
    </button>
    <div class="course-content-navigation-menu">
""".strip()
        )

        for page in section["pages"]:
            href = page["path"].relative_to(CONTENT_DIR).with_suffix(".html")

            html.append(
                f"""
<a
    class="course-content-navigation-link"
    href=""
    data-content-page="{href}">
    {page["title"]}
</a>
""".strip()
            )

        html.append("""
    </div>
</div>
""".strip())

    html.append("""
        </div>
    </div>
</nav>
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


    /* --------------------------------------------------------------------------
       Course content navigation links
       -------------------------------------------------------------------------- */

    document.querySelectorAll(
        ".course-content-navigation a[data-content-page]"
    ).forEach(function (link) {

        const page = link.dataset.contentPage;
        const href = siteRoot + "content/" + page;

        link.href = href;

        const currentContentPage =
            pathname.replace(/^.*\/content\//, "").replace(/\/$/, "") || "index.html";

        if (currentContentPage === page) {

            if (link.classList.contains(
                "course-content-navigation-introduction"
            )) {
                link.classList.add(
                    "course-content-navigation-toggle-active"
                );
            } else {
                link.classList.add(
                    "course-content-navigation-link-active"
                );

                const dropdown = link.closest(
                    ".course-content-navigation-dropdown"
                );

                if (dropdown) {
                    const toggle = dropdown.querySelector(
                        ".course-content-navigation-toggle"
                    );

                    if (toggle) {
                        toggle.classList.add(
                            "course-content-navigation-toggle-active"
                        );
                    }
                }
            }
        }
    });


    /* --------------------------------------------------------------------------
       Main course navbar links
       -------------------------------------------------------------------------- */

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


    /* --------------------------------------------------------------------------
       Course assets
       -------------------------------------------------------------------------- */

    document.querySelectorAll("[data-course-asset]").forEach(function (image) {
        image.src = siteRoot + image.dataset.courseAsset;
    });


    /* --------------------------------------------------------------------------
       Move horizontal course content navigation below navbar
       -------------------------------------------------------------------------- */

    const contentNavigation =
        document.querySelector(".course-content-navigation");

    if (contentNavigation) {

        if (navbar) {
            navbar.parentNode.insertBefore(
                contentNavigation,
                navbar.nextSibling
            );
        } else {
            document.body.insertBefore(
                contentNavigation,
                document.body.firstChild
            );
        }
    }


    /* --------------------------------------------------------------------------
       Course content dropdowns
       -------------------------------------------------------------------------- */

    document.querySelectorAll(
        ".course-content-navigation-dropdown"
    ).forEach(function (dropdown) {

        const toggle = dropdown.querySelector(
            ".course-content-navigation-toggle"
        );

        if (!toggle) {
            return;
        }

        // Open on hover (desktop)
        dropdown.addEventListener("mouseenter", function () {
            dropdown.classList.add("is-open");
            toggle.setAttribute("aria-expanded", "true");
        });

        // Close when the pointer leaves
        dropdown.addEventListener("mouseleave", function () {
            dropdown.classList.remove("is-open");
            toggle.setAttribute("aria-expanded", "false");
        });

        // Preserve click-to-toggle behavior (touchscreens and keyboard)
        toggle.addEventListener("click", function (event) {
            event.stopPropagation();

            const isOpen = dropdown.classList.contains("is-open");

            document.querySelectorAll(
                ".course-content-navigation-dropdown.is-open"
            ).forEach(function (openDropdown) {

                openDropdown.classList.remove("is-open");

                const openToggle = openDropdown.querySelector(
                    ".course-content-navigation-toggle"
                );

                if (openToggle) {
                    openToggle.setAttribute("aria-expanded", "false");
                }
            });

            if (!isOpen) {
                dropdown.classList.add("is-open");
                toggle.setAttribute("aria-expanded", "true");
            }
        });
    });


    document.addEventListener("click", function () {

        document.querySelectorAll(
            ".course-content-navigation-dropdown.is-open"
        ).forEach(function (dropdown) {

            dropdown.classList.remove("is-open");

            const toggle = dropdown.querySelector(
                ".course-content-navigation-toggle"
            );

            if (toggle) {
                toggle.setAttribute("aria-expanded", "false");
            }
        });
    });

    /* --------------------------------------------------------------------------
       TOC link navigation and active state
       -------------------------------------------------------------------------- */

    function setActiveTocLink(selectedLink) {
        document.querySelectorAll("#TOC .nav-link").forEach(function (link) {
            link.classList.remove("active");
            link.removeAttribute("aria-current");
        });

        selectedLink.classList.add("active");
        selectedLink.setAttribute("aria-current", "location");
    }

    // Start with the first TOC item active when the page opens at the top.
    window.addEventListener("load", function () {
        const firstTocLink = document.querySelector("#TOC .nav-link");

        if (firstTocLink && window.scrollY < 10) {
            setActiveTocLink(firstTocLink);
        }
    });

    // Navigate to and activate the selected section when a TOC item is clicked.
    document.addEventListener("click", function (event) {
        const link = event.target.closest(
            '#TOC a[data-scroll-target]'
        );

        if (!link) {
            return;
        }

        const target = document.querySelector(link.dataset.scrollTarget);

        if (!target) {
            return;
        }

        event.preventDefault();

        history.pushState(null, "", link.href);

        target.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

        // Set it again after Quarto has processed the click.
        setActiveTocLink(link);

        window.setTimeout(function () {
            setActiveTocLink(link);
        }, 150);
    }, true);
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