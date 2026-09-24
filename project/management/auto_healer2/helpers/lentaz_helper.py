from management.auto_healer.candidates import Candidate

def extract_lentaz_date(soup) -> str | None:
    """.news_img daxilindəki span teqindən tarixi götürür."""
    date_node = soup.select_one('.news_img span')
    if date_node:
        return date_node.get_text(strip=True)
    return None

def get_lentaz_date_candidate(soup) -> Candidate | None:
    """AutoHealer kandidat obyektini qaytarır."""
    node = soup.select_one('.news_img span')
    if not node:
        return None

    return Candidate(
        field="shared_date",
        resolution_type="css_selector",
        rule=".news_img span",
        source="lentaz_helper",
        node=node,
        value=node.get_text(strip=True),
        prior_confidence=0.95
    )