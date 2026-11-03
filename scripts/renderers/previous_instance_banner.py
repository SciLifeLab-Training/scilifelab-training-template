"""
The "This is an older instance of this training" banner.

The banner is shown on every page of a training instance as soon as a
newer instance is marked as current on the landing page. Nothing needs
to change on this branch for that:

- When the landing page is published, it also publishes the list of
  instances (instances.json, next to the landing page).
- A small script in the visitor's browser reads that list. When this
  instance is listed with "status: previous", the banner appears, with a
  link to the current instance.

Without that list (for example in the preview on your own computer, or
before the landing page has been published), the banner stays hidden.

Set website.previous_instance_banner to false to never show the banner,
for example for a self-paced version that stays valid.
"""

from html import escape

from renderers.fair import instance_id


# Reads the list of instances published with the landing page, and shows
# the banner when this instance is no longer the current one.
#
# The list is at the root of the website: the part of the address before
# "/<this instance>/". For example, for
# https://org.github.io/repo/2505/content/module-1/introduction.html
# the list is https://org.github.io/repo/instances.json.
SCRIPT = """
<script>
(function () {
  var banner = document.currentScript.previousElementSibling;
  var slug = banner && banner.dataset.instance;
  if (!slug || !window.fetch) {
    return;
  }

  var path = window.location.pathname;
  var position = path.indexOf("/" + slug + "/");
  if (position < 0) {
    return;
  }

  var root = window.location.origin + path.slice(0, position + 1);

  fetch(root + "instances.json", { cache: "no-cache" })
    .then(function (response) {
      return response.ok ? response.json() : null;
    })
    .then(function (data) {
      var instances = (data && data.instances) || [];
      var self = instances.filter(function (item) {
        return item.slug === slug;
      })[0];
      var current = instances.filter(function (item) {
        return item.status === "current";
      })[0];

      if (!self || !current || self.status !== "previous") {
        return;
      }

      var link = banner.querySelector("a");
      link.href = new URL(current.url, root).href;
      banner.querySelector("[data-current-label]").textContent = current.label;
      banner.hidden = false;
    })
    .catch(function () {});
})();
</script>
""".strip()


def render_previous_instance_banner_html(website):
    """The hidden banner and its script, as HTML."""

    if website.get("previous_instance_banner", True) is False:
        return ""

    slug = instance_id()

    if not slug:
        return ""

    return (
        f'<div class="template-banner previous-instance-banner" '
        f'data-instance="{escape(slug, quote=True)}" hidden>\n'
        "<p><strong>This is an older instance of this training.</strong> "
        "For the latest information, visit the newest training instance: "
        '<a href="#"><span data-current-label></span> →</a></p>\n'
        "</div>\n"
        f"{SCRIPT}\n"
    )


def render_previous_instance_banner(website):
    """The banner for the pages written in Quarto Markdown."""

    html = render_previous_instance_banner_html(website)

    if not html:
        return ""

    return f"```{{=html}}\n{html}```\n"
