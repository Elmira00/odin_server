#project/management/auto_healer/services.py
import traceback
import requests
from bs4 import BeautifulSoup
import management.auto_healer.helpers  # noqa: F401
from management.auto_healer.discovery import discover_field
from management.auto_healer.resolvers_adapter import (
    TitleAutoHealer,
    DescriptionAutoHealer,
    ContentAutoHealer,
    ImageAutoHealer,
    SharedDateAutoHealer,
)

HEALER_CLASSES_BY_FIELD = {
    'title': TitleAutoHealer,
    'description': DescriptionAutoHealer,
    'content': ContentAutoHealer,
    'image': ImageAutoHealer,
    'news_shared_date': SharedDateAutoHealer,
}

DISPLAY_TO_FIELD = {
    'title': 'title',
    'description': 'description',
    'content': 'content',
    'image': 'image',
    'news_shared_date': 'shared_date',
}

def extract_sample_preview(category, result, sample_soup, sample_url):
    try:
        res_type = result.resolution_type
        rule = result.rule
        raw_text = None

        if res_type == 'meta':
            element = sample_soup.find(rule.get('tag'), attrs=rule.get('attrs'))
            if element:
                raw_text = element.get('content') or element.get('href')

        elif res_type == 'json_ld':
            healer_cls = HEALER_CLASSES_BY_FIELD.get(category)
            if healer_cls:
                healer = healer_cls(source_id=0, test_urls=[sample_url], shared_soups={sample_url: sample_soup})
                raw_text = healer.get_json_ld_value(sample_soup, rule.get('keys', []))

        elif res_type == 'api_json':
            raw_text = f"[value comes from {rule.get('source')} at extraction time]"

        elif res_type == 'css_selector':
            element = sample_soup.select_one(rule)
            if element:
                if category == 'image':
                    raw_text = element.get('src') or element.get('data-src') or element.get('poster')
                else:
                    text = element.get_text(separator=" ", strip=True)
                    raw_text = text[:150] + "..." if len(text) > 150 else text

        elif res_type == 'url_regex':
            import re
            match = re.search(rule, sample_url)
            if match:
                raw_text = match.group(1)

        if category == 'news_shared_date' and raw_text and res_type != 'api_json':
            try:
                from dateutil import parser
                from datetime import timedelta, timezone
                
                parsed_date = parser.parse(raw_text)
                
                if parsed_date.tzinfo is not None:
                    baku_tz = timezone(timedelta(hours=4))
                    parsed_date = parsed_date.astimezone(baku_tz)
                else:
                    parsed_date = parsed_date + timedelta(hours=4)
                    
                return f"{parsed_date.strftime('%Y-%m-%d %H:%M:%S')} (raw text: {raw_text})"
            except Exception:
                return raw_text

        return raw_text
    except Exception:
        pass
    return None

def run_discovery_diagnostics(test_urls):
    shared_soups = {}
    for url in test_urls:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if resp.status_code == 200:
                shared_soups[url] = BeautifulSoup(resp.text, 'html.parser')
        except Exception:
            pass

    sample_url = test_urls[0] if test_urls else None
    sample_soup = shared_soups.get(sample_url) if sample_url else None

    diagnostic_results = {}
    diagnostic_results = {}
    for display_name, internal_field in DISPLAY_TO_FIELD.items():
        try:
            HealerClass = HEALER_CLASSES_BY_FIELD.get(display_name)
            if not HealerClass:
                raise ValueError(f"Unknown healer class for {display_name}")
            
            # Instantiate the base healer adapter for this field
            healer = HealerClass(source_id=0, test_urls=test_urls, shared_soups=shared_soups)
            
            # Call discover_field with soups_by_url positionally
            result = discover_field(internal_field, healer, shared_soups)
            
            if result:
                preview = None
                if sample_soup and sample_url:
                    preview = extract_sample_preview(display_name, result, sample_soup, sample_url)

                diagnostic_results[display_name] = {
                    "status": "success",
                    "resolution_type": getattr(result, 'resolution_type', None),
                    "rule": getattr(result, 'rule', None),
                    "source": getattr(result, 'source', None),
                    "preview": preview
                }
            else:
                diagnostic_results[display_name] = {
                    "status": "not_found",
                    "resolution_type": None,
                    "rule": None,
                    "source": None,
                    "preview": None
                }
        except Exception as e:
            diagnostic_results[display_name] = {
                "status": "error",
                "detail": str(e),
                "traceback": traceback.format_exc()
            }

    return diagnostic_results