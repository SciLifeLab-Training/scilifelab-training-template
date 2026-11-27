"""
The browser tab title of every page of a training instance.

Quarto names each tab after the title in the page's front matter, which
says nothing about the training. This script sets it to
"<page> – <training title>", and to only the training title on the
overview page, for example:

    Introduction to R                  (overview)
    Schedule – Introduction to R
    Reading data – Introduction to R   (a content page)

The page name comes from the navigation bar, so it matches what
visitors see there. Content pages use their own title.
"""

import json


def render_page_title_script(course):

    title = str(course.get("title") or "").strip()

    if not title:
        return ""

    training = json.dumps(title, ensure_ascii=False)

    return f"""<script>
(function () {{
  var training = {training};

  function apply() {{
    var path = window.location.pathname;
    if (path.slice(-1) === "/") {{
      path += "index.html";
    }}

    // The navigation link whose page this is. The longest match wins,
    // so content/index.html is not taken for the overview page.
    var best = null;
    document.querySelectorAll("[data-page]").forEach(function (link) {{
      var target = "/" + link.dataset.page.replace(/\\.qmd$/, ".html");
      if (path.slice(-target.length) === target &&
          (!best || target.length > best.target.length)) {{
        best = {{ target: target, label: link.textContent.trim() }};
      }}
    }});

    var page;
    if (best && best.target === "/index.html") {{
      page = "";
    }} else if (best) {{
      page = best.label;
    }} else {{
      page = document.title.split(" \\u2013 ")[0].trim();
    }}

    document.title = page && page !== training
      ? page + " \\u2013 " + training
      : training;
  }}

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", apply);
  }} else {{
    apply();
  }}
}})();
</script>
"""
