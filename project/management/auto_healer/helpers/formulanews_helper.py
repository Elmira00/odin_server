import re
from datetime import datetime
from management.auto_healer.candidates import Candidate

GEORGIAN_MONTHS = {
    "იან": "01", "თებ": "02", "მარ": "03", "აპრ": "04",
    "მაის": "05", "ივნ": "06", "ივლ": "07", "აგვ": "08",
    "სექ": "09", "ოქტ": "10", "ნოე": "11", "დეკ": "12"
}

def extract_formulanews_date(soup) -> str | None:
    """DOM-dan gürcü dilindəki tarixi götürüb ISO formatına salır."""
    date_node = soup.select_one('.news___inner___images_created')
    if not date_node:
        return None

    raw_text = date_node.get_text(strip=True, separator=" ")
    match = re.search(r'(\d{1,2})\s+([\u10D0-\u10FA]+)\s+(\d{2}:\d{2})', raw_text)
    
    if match:
        day, month_geo, time_str = match.groups()
        month = GEORGIAN_MONTHS.get(month_geo, "01")
        current_year = datetime.now().year
        return f"{current_year}-{month}-{int(day):02d} {time_str}"
        
    return raw_text

def get_formulanews_date_candidate(soup) -> Candidate | None:
    """AutoHealer sisteminin tanıması üçün Candidate obyekti qaytarır."""
    node = soup.select_one('.news___inner___images_created')
    if not node:
        return None

    extracted_value = extract_formulanews_date(soup)

    return Candidate(
        field="shared_date",
        resolution_type="css_selector",
        rule=".news___inner___images_created",
        source="formulanews_helper",
        node=node,
        value=extracted_value,
        prior_confidence=0.9
    )