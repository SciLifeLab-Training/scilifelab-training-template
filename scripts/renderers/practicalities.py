from urllib.parse import urlparse, parse_qs


def osm_embed_url(map_url):
    """
    Convert an OpenStreetMap share URL into an embeddable map URL.
    """

    if not map_url:
        return ""

    parsed = urlparse(map_url)

    # OpenStreetMap stores map=zoom/latitude/longitude in the URL fragment.
    fragment = parse_qs(parsed.fragment)

    map_value = fragment.get("map", [None])[0]

    if not map_value:
        return map_url

    try:
        zoom, latitude, longitude = map_value.split("/")
        zoom = int(float(zoom))
        latitude = float(latitude)
        longitude = float(longitude)
    except (ValueError, AttributeError):
        return map_url

    # Create a small bounding box around the marker.
    # The size is adjusted slightly based on the requested zoom.
    span = 0.01 / (2 ** max(zoom - 15, 0))

    bbox = (
        f"{longitude - span},{latitude - span},"
        f"{longitude + span},{latitude + span}"
    )

    return (
        "https://www.openstreetmap.org/export/embed.html"
        f"?bbox={bbox}"
        f"&layer=mapnik"
        f"&marker={latitude},{longitude}"
    )


def section_heading(icon, title):
    return (
        "<h2>"
        f'<i class="bi {icon}" aria-hidden="true"></i>'
        f"{title}"
        "</h2>"
    )


def render_practicalities(practicalities, course):

    if not practicalities:
        return ""

    html = []

    html.append('<div class="course-practicalities-page">')

    # ---------------------------------------------------------
    # Page header
    # ---------------------------------------------------------

    html.append('<header class="course-practicalities-header">')

    html.append(
        '<div class="course-practicalities-header-main">'
    )

    html.append(
        '<div class="course-page-label">'
        "Practicalities"
        "</div>"
    )

    html.append('<h1 class="course-page-title">Practical information</h1>')

    if practicalities.get("intro"):

        html.append(
            '<p class="course-page-intro course-page-intro-narrow">'
            f'{practicalities["intro"]}'
            '</p>'
        )   

    html.append("</div>")

    contact = course.get("contact", {})
    contact_email = contact.get("email")

    if contact_email:
        html.append(
            '<div class="course-page-contact">'
        )

        html.append(
            '<div class="course-page-contact-icon">'
            '<i class="bi bi-envelope"></i>'
            "</div>"
        )

        html.append(
            '<div class="course-page-contact-title">'
            "Questions about the training?"
            "</div>"
        )

        html.append(
            "<p>Get in touch with the training team.</p>"
        )

        html.append(
            f'<a class="course-text-link" href="mailto:{contact_email}">'
            f"{contact_email}"
            "</a>"
        )

        html.append("</div>")

    html.append("</header>")

    # ---------------------------------------------------------
    # Venue
    # ---------------------------------------------------------

    venue = practicalities.get("venue", {})
    venue_name = venue.get("name", "")
    venue_address = venue.get("address", "")

    # Extract city from the address.
    # Expected format:
    # Street address
    # Postal code City
    # Country

    venue_city = ""

    address_lines = [
        line.strip()
        for line in venue_address.splitlines()
        if line.strip()
    ]

    if len(address_lines) >= 2:
        city_line = address_lines[-2]

        # Swedish postal code format: 123 45 City
        parts = city_line.split(maxsplit=2)

        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            venue_city = parts[2]

    if any(
        venue.get(field)
        for field in [
            "name",
            "address",
            "room",
            "instructions",
            "map_url",
        ]
    ):

        html.append(
            '<section class="course-practicalities-section">'
        )

        html.append(
            section_heading(
                "bi-geo-alt-fill",
                "Venue",
            )
        )

        if venue_name:
            if venue_city:
                html.append(
                    f"<p>The training will take place at "
                    f"{venue_name} in {venue_city}.</p>"
                )
            else:
                html.append(
                    f"<p>The training will take place at "
                    f"{venue_name}.</p>"
                )

        html.append(
            '<div class="course-practicalities-venue">'
        )

        venue_details = []

        if venue.get("address"):
            venue_details.append(
                "<div>"
                "<strong>Address</strong>"
                '<div class="course-practicalities-address">'
                f'{venue["address"].replace(chr(10), "<br>")}'
                "</div>"
                "</div>"
            )

        if venue.get("room"):
            venue_details.append(
                "<div>"
                "<strong>Room</strong>"
                f'<div>{venue["room"]}</div>'
                "</div>"
            )

        if venue.get("instructions"):
            venue_details.append(
                "<div>"
                "<strong>Entrance</strong>"
                f'<div>{venue["instructions"]}</div>'
                "</div>"
            )

        if venue_details:
            html.append(
                '<div class="course-practicalities-venue-details">'
                + "\n".join(venue_details)
                + "</div>"
            )

        if venue.get("map_url"):
            map_embed_url = osm_embed_url(
                venue["map_url"]
            )

            html.append(
                '<div class="course-practicalities-map-column">'
                '<div class="course-practicalities-map">'
                f'<iframe '
                f'src="{map_embed_url}" '
                'title="Venue map" '
                'loading="lazy">'
                '</iframe>'
                '</div>'
                f'<a class="course-practicalities-map-link" '
                f'href="{venue["map_url"]}" '
                'target="_blank" rel="noopener">'
                '<i class="bi bi-box-arrow-up-right" aria-hidden="true"></i>'
                'Open map '
                '</a>'
                '</div>'
            )

        html.append("</div>")

        html.append("</section>")

    # ---------------------------------------------------------
    # Transport
    # ---------------------------------------------------------

    transport = practicalities.get("transport", {})

    if (
        transport.get("description")
        or transport.get("public_transport")
        or transport.get("parking")
        or transport.get("links")
    ):

        html.append(
            '<section class="course-practicalities-section">'
        )

        html.append(
            section_heading(
                "bi-bus-front-fill",
                "Transport",
            )
        )

        if transport.get("description"):
            html.append(
                f'<p>{transport["description"]}</p>'
            )

        if transport.get("public_transport"):
            html.append(
                f'<p>{transport["public_transport"]}</p>'
            )

        links = [
            link
            for link in transport.get("links", [])
            if link.get("title") and link.get("url")
        ]

        if links:
            html.append(
                '<ul class="course-practicalities-links">'
            )

            for link in links:
                html.append(
                    f'<li><a class="course-text-link" href="{link["url"]}" '
                    'target="_blank" rel="noopener">'
                    f'{link["title"]}</a></li>'
                )

            html.append("</ul>")

        if transport.get("parking"):
            html.append(
                f'<p>{transport["parking"]}</p>'
            )

        html.append("</section>")

    # ---------------------------------------------------------
    # Accommodation
    # ---------------------------------------------------------

    accommodation = practicalities.get(
        "accommodation",
        {},
    )

    hotels = [
        hotel
        for hotel in accommodation.get("hotels", [])
        if hotel.get("name")
    ]

    if accommodation.get("description") or hotels:

        html.append(
            '<section class="course-practicalities-section">'
        )

        html.append(
            section_heading(
                "bi-building",
                "Accommodation",
            )
        )

        if accommodation.get("description"):
            html.append(
                f'<p>{accommodation["description"]}</p>'
            )

        if hotels:
            html.append(
                '<div class="course-practicalities-table-wrapper">'
            )

            html.append(
                '<table class="course-practicalities-table">'
            )

            html.append(
                "<thead>"
                "<tr>"
                "<th>Hotel</th>"
                "<th>Distance</th>"
                "<th>Walking time</th>"
                "</tr>"
                "</thead>"
            )

            html.append("<tbody>")

            for hotel in hotels:

                name = hotel["name"]

                if hotel.get("url"):
                    name = (
                        f'<a class="course-text-link" href="{hotel["url"]}" '
                        'target="_blank" rel="noopener">'
                        f"{name}</a>"
                    )

                html.append(
                    "<tr>"
                    f"<td>{name}</td>"
                    f'<td>{hotel.get("distance", "")}</td>'
                    f'<td>{hotel.get("walking_time", "")}</td>'
                    "</tr>"
                )

            html.append("</tbody>")
            html.append("</table>")
            html.append("</div>")

        html.append("</section>")

    # ---------------------------------------------------------
    # Food
    # ---------------------------------------------------------

    food = practicalities.get("food", {})

    if (
        food.get("description")
        or food.get("dietary_information")
    ):

        html.append(
            '<section class="course-practicalities-section">'
        )

        html.append(
            section_heading(
                "bi-cup-hot-fill",
                "Food &amp; refreshments",
            )
        )

        if food.get("description"):
            html.append(
                f'<p>{food["description"]}</p>'
            )

        if food.get("dietary_information"):
            html.append(
                f'<p>{food["dietary_information"]}</p>'
            )

        html.append("</section>")

    # ---------------------------------------------------------
    # Additional information
    # ---------------------------------------------------------

    additional = [
        item
        for item in practicalities.get("additional", [])
        if item.get("title") and item.get("content")
    ]

    if additional:

        html.append(
            '<section class="course-practicalities-section">'
        )

        html.append(
            section_heading(
                "bi-file-earmark-text-fill",
                "Other information",
            )
        )

        html.append(
            '<div class="course-practicalities-additional">'
        )

        for item in additional:
            html.append(
                '<div class="course-practicalities-additional-item">'
                f'<h3>{item["title"]}</h3>'
                f'<p>{item["content"]}</p>'
                "</div>"
            )

        html.append("</div>")
        html.append("</section>")

    html.append("</div>")

    return "\n".join(html).strip()