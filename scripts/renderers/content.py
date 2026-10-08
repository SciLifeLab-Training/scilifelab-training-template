from pathlib import Path

from renderers.navbar import (
    render_navbar_meta,
    render_navbar_brand,
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
        <button
            class="course-content-navigation-arrow course-content-navigation-arrow-left"
            type="button"
            tabindex="-1"
            aria-hidden="true">
            <i class="bi bi-chevron-left"></i>
        </button>
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
            href = (
                page["path"]
                .relative_to(CONTENT_DIR)
                .with_suffix(".html")
            )

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
        <button
            class="course-content-navigation-arrow course-content-navigation-arrow-right"
            type="button"
            tabindex="-1"
            aria-hidden="true">
            <i class="bi bi-chevron-right"></i>
        </button>
    </div>
</nav>
""".strip())

    return "\n".join(html)


def render_content_next_navigation(sections):
    # Introduction is the first page in the navigation sequence.
    pages = [{
        "path": Path("index.qmd"),
        "title": "Introduction",
    }]

    # Add topic pages in their existing section/page order.
    for section in sections:
        for page in section["pages"]:
            if page["path"].name != "index.qmd":
                pages.append(page)

    def page_href(page):
        path = page["path"]

        if path.is_absolute():
            return path.relative_to(CONTENT_DIR).with_suffix(".html")

        return path.with_suffix(".html")

    html = []

    for index, page in enumerate(pages):
        current_page = page_href(page)
        links = []

        # Previous page
        if index > 0:
            previous_page = pages[index - 1]
            previous_href = page_href(previous_page)

            links.append(
                f"""
<a class="course-content-prev-link"
   href=""
   data-content-navigation-page="{previous_href}">
    <span class="course-content-next-label">Previous</span>
    <span class="course-content-next-title">
        ← {previous_page["title"]}
    </span>
</a>
""".strip()
            )

        # Next page
        if index < len(pages) - 1:
            next_page = pages[index + 1]
            next_href = page_href(next_page)

            links.append(
                f"""
<a class="course-content-next-link"
   href=""
   data-content-navigation-page="{next_href}">
    <span class="course-content-next-label">Next</span>
    <span class="course-content-next-title">
        {next_page["title"]} →
    </span>
</a>
""".strip()
            )

        html.append(
            f"""
<div class="course-content-next-navigation" hidden
     data-content-next-from="{current_page}">
    {"".join(links)}
</div>
""".strip()
        )

    return "\n".join(html)


def render_content_navbar(
    course,
    website,
    available_pages,
    content_navigation,
):
    meta = render_navbar_meta(course)
    brand = render_navbar_brand(website, content_page=True)
    links = render_navbar_links(website, available_pages)

    return """
<div class="course-content-page-shell">

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

""" + brand + """

            </div>

        </div>

    </div>

""" + content_navigation + """

</div>

<script>

document.documentElement.classList.add("course-content-page");

document.addEventListener("DOMContentLoaded", function () {

    const pageShell = document.querySelector(
        ".course-content-page-shell"
    );

    const footer = document.querySelector(".landing-footer");


    /*
     * Move the generated content-page site chrome
     * outside Quarto's main-content / TOC grid.
     */

    if (pageShell) {
        const quartoContent =
            document.querySelector("#quarto-content");

        if (quartoContent) {
            document.body.insertBefore(
                pageShell,
                quartoContent
            );
        } else {
            document.body.insertBefore(
                pageShell,
                document.body.firstChild
            );
        }
    }

    if (footer) {
        document.body.appendChild(footer);
    }

    const pathname = window.location.pathname;
    const contentMarker = "/content/";

    const siteRoot = pathname.includes(contentMarker)
        ? pathname.split(contentMarker)[0] + "/"
        : "/";

    const contentPath = pathname.includes(contentMarker)
        ? pathname.split(contentMarker)[1].replace(/^\/+|\/+$/g, "")
        : "";

    const currentContentPage =
        !contentPath || contentPath === "index"
            ? "index.html"
            : contentPath;

    /*
     * --------------------------------------------------------------------------
     * Course content navigation links
     * --------------------------------------------------------------------------
     */
    document.querySelectorAll(
        ".course-content-navigation a[data-content-page]"
    ).forEach(function (link) {
        const page = link.dataset.contentPage;
        const href = siteRoot + "content/" + page;

        link.href = href;

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

    /*
     * --------------------------------------------------------------------------
     * Previous / next page navigation
     * Show only the navigation for the current content page.
     * --------------------------------------------------------------------------
     */
    document.querySelectorAll(
        ".course-content-next-navigation[data-content-next-from]"
    ).forEach(function (navigation) {
        const isCurrentPage =
            navigation.dataset.contentNextFrom === currentContentPage;

        navigation.hidden = !isCurrentPage;

        if (isCurrentPage) {
            navigation.querySelectorAll(
                "a[data-content-navigation-page]"
            ).forEach(function (link) {
                link.href =
                    siteRoot + "content/" +
                    link.dataset.contentNavigationPage;
            });
        }
    });

    /*
     * Move the active navigation outside Quarto's content grid,
     * directly before the footer.
     */
    const activePageNavigation = document.querySelector(
        ".course-content-next-navigation:not([hidden])"
    );

    if (activePageNavigation) {
        const pageFooter = document.querySelector(".landing-footer");

        if (pageFooter && pageFooter.parentNode === document.body) {
            document.body.insertBefore(activePageNavigation, pageFooter);
        } else {
            document.body.appendChild(activePageNavigation);
        }
    }

    /*
     * --------------------------------------------------------------------------
     * Main course navbar links
     * --------------------------------------------------------------------------
     */
    const isContentPage = pathname.includes("/content/");
    const currentPage = pathname.split("/").pop() || "index.html";

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

    /*
     * --------------------------------------------------------------------------
     * Course assets
     * --------------------------------------------------------------------------
     */
    document.querySelectorAll("[data-course-asset]").forEach(function (image) {
        image.src = siteRoot + image.dataset.courseAsset;
    });

    /*
     * --------------------------------------------------------------------------
     * Course content dropdowns
     *
     * The navigation bar scrolls sideways, which would clip normally
     * positioned menus, so open menus use position: fixed and are
     * placed under their toggle here.
     * --------------------------------------------------------------------------
     */
    const contentNavScroll = document.querySelector(
        ".course-content-navigation-scroll"
    );

    const contentDropdowns = document.querySelectorAll(
        ".course-content-navigation-dropdown"
    );

    function positionContentMenu(dropdown) {
        const toggle = dropdown.querySelector(
            ".course-content-navigation-toggle"
        );
        const menu = dropdown.querySelector(
            ".course-content-navigation-menu"
        );

        if (!toggle || !menu) {
            return;
        }

        const rect = toggle.getBoundingClientRect();
        const maxLeft = window.innerWidth - menu.offsetWidth - 8;

        menu.style.top = (rect.bottom + 4) + "px";
        menu.style.left = Math.max(8, Math.min(rect.left, maxLeft)) + "px";
    }

    function closeContentDropdown(dropdown) {
        dropdown.classList.remove("is-open");

        const toggle = dropdown.querySelector(
            ".course-content-navigation-toggle"
        );

        if (toggle) {
            toggle.setAttribute("aria-expanded", "false");
        }
    }

    function closeAllContentDropdowns(except) {
        document.querySelectorAll(
            ".course-content-navigation-dropdown.is-open"
        ).forEach(function (openDropdown) {
            if (openDropdown !== except) {
                closeContentDropdown(openDropdown);
            }
        });
    }

    function openContentDropdown(dropdown) {
        closeAllContentDropdowns(dropdown);

        dropdown.classList.add("is-open");

        const toggle = dropdown.querySelector(
            ".course-content-navigation-toggle"
        );

        if (toggle) {
            toggle.setAttribute("aria-expanded", "true");
        }

        positionContentMenu(dropdown);
    }

    contentDropdowns.forEach(function (dropdown) {
        const toggle = dropdown.querySelector(
            ".course-content-navigation-toggle"
        );

        if (!toggle) {
            return;
        }

        let closeTimer = null;

        // Open on hover, for mouse users only.
        dropdown.addEventListener("pointerenter", function (event) {
            if (event.pointerType !== "mouse") {
                return;
            }

            window.clearTimeout(closeTimer);
            openContentDropdown(dropdown);
        });

        // Close shortly after the mouse leaves, so it can cross
        // the small gap between the toggle and the menu.
        dropdown.addEventListener("pointerleave", function (event) {
            if (event.pointerType !== "mouse") {
                return;
            }

            closeTimer = window.setTimeout(function () {
                closeContentDropdown(dropdown);
            }, 150);
        });

        // Toggle on click or tap (touchscreens and keyboard).
        toggle.addEventListener("click", function (event) {
            event.stopPropagation();

            if (dropdown.classList.contains("is-open")) {
                closeContentDropdown(dropdown);
            } else {
                openContentDropdown(dropdown);
            }
        });
    });

    // Close menus when clicking elsewhere or pressing Escape.
    document.addEventListener("click", function () {
        closeAllContentDropdowns(null);
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeAllContentDropdowns(null);
        }
    });

    // Keep open menus under their toggle while scrolling or resizing.
    function repositionOpenContentMenus() {
        document.querySelectorAll(
            ".course-content-navigation-dropdown.is-open"
        ).forEach(positionContentMenu);
    }

    window.addEventListener("resize", repositionOpenContentMenus);
    window.addEventListener(
        "scroll", repositionOpenContentMenus, { passive: true }
    );

    if (contentNavScroll) {
        contentNavScroll.addEventListener(
            "scroll", repositionOpenContentMenus, { passive: true }
        );

        // Scroll the current module into view, so it is visible
        // when the bar is wider than the screen.
        const activeToggle = contentNavScroll.querySelector(
            ".course-content-navigation-toggle-active"
        );

        if (activeToggle) {
            const activeItem =
                activeToggle.closest(".course-content-navigation-dropdown")
                || activeToggle;

            contentNavScroll.scrollLeft =
                activeItem.offsetLeft
                - (contentNavScroll.clientWidth - activeItem.offsetWidth) / 2;
        }
    }

    /*
     * --------------------------------------------------------------------------
     * Content navigation scroll indicators
     * Show the fade and arrow on each side that has more modules.
     * --------------------------------------------------------------------------
     */
    const contentNav = document.querySelector(".course-content-navigation");

    function updateContentNavArrows() {
        if (!contentNav || !contentNavScroll) {
            return;
        }

        const maxScroll =
            contentNavScroll.scrollWidth - contentNavScroll.clientWidth;

        contentNav.classList.toggle(
            "can-scroll-left",
            contentNavScroll.scrollLeft > 1
        );

        contentNav.classList.toggle(
            "can-scroll-right",
            contentNavScroll.scrollLeft < maxScroll - 1
        );
    }

    if (contentNav && contentNavScroll) {
        contentNav.querySelectorAll(
            ".course-content-navigation-arrow"
        ).forEach(function (arrow) {
            const direction = arrow.classList.contains(
                "course-content-navigation-arrow-left"
            ) ? -1 : 1;

            arrow.addEventListener("click", function () {
                contentNavScroll.scrollBy({
                    left: direction * contentNavScroll.clientWidth * 0.7,
                    behavior: "smooth"
                });
            });
        });

        contentNavScroll.addEventListener(
            "scroll", updateContentNavArrows, { passive: true }
        );
        window.addEventListener("resize", updateContentNavArrows);

        // Check again once fonts and images have loaded,
        // since they can change the width of the modules.
        window.addEventListener("load", updateContentNavArrows);

        updateContentNavArrows();
    }
    
    /*
     * --------------------------------------------------------------------------
     * TOC link navigation and active state
     * --------------------------------------------------------------------------
     */
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