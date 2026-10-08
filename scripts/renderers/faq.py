def render_faq(faq):

    if not faq:
        return ""

    questions = faq.get("questions") or []

    if not questions:
        return ""

    html = []

    html.append('<div class="course-faq-page">')

    # ---------------------------------------------------------
    # Page header
    # ---------------------------------------------------------

    html.append('<header class="course-faq-header">')

    html.append(
        '<div class="course-page-label">FAQ</div>'
    )

    html.append(
        '<h1 class="course-page-title">Frequently asked questions</h1>'
    )

    if faq.get("intro"):

        html.append(
            '<p class="course-page-intro">'
            f'{faq["intro"]}'
            '</p>'
        )

    html.append('</header>')

    # ---------------------------------------------------------
    # FAQ accordion
    # ---------------------------------------------------------

    html.append('<div class="course-faq-list">')

    for index, item in enumerate(questions, start=1):

        question = item.get("question")
        answer = item.get("answer")

        if not question or not answer:
            continue

        html.append('<details class="course-faq-item">')

        html.append(
            '<summary>'
            f'<span class="course-faq-number">{index}.</span>'
            f'<span class="course-faq-question">{question}</span>'
            '<i class="bi bi-chevron-down" aria-hidden="true"></i>'
            '</summary>'
        )

        html.append(
            '<div class="course-faq-answer">'
            f'<p>{answer}</p>'
            '</div>'
        )

        html.append('</details>')

    html.append('</div>')
    html.append('</div>')

    return "\n".join(html).strip()