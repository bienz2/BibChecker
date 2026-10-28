__all__ = ["parse_osti", "search_osti"]

import requests

def safe_json(results):
    """Return parsed JSON, or None if the request failed or the body isn't JSON."""
    if results is None or not results.ok:
        return None
    try:
        return results.json()
    except requests.exceptions.JSONDecodeError:
        return None

def parse_osti(citation, validation, results):
    if results is None:
        return

    data = safe_json(results)
    if not isinstance(data, list):
        return
    for rec in data:
        title = (rec.get("title") or "").strip()
        authors = []

        for c in rec.get("authors", []) or []:
            last = (c.split(',')[0]).lower()
            if last:
                authors.append(last)

        validation.compare(citation, title, authors)
        if validation.score_title == 1 and validation.authors:
            return

        
def search_osti(citation, validation):
    url = "https://www.osti.gov/api/v1/records"
    params = {
        "q": citation.norm_title,
        "rows": 5,
        "format": "json"
    }
    parse_osti(citation, validation, validation.search_request(url, params))
    if validation.score_title == 1.0 and validation.authors:
        return

    if citation.norm_concat_title:
        params = {
            "q": citation.norm_concat_title,
            "rows": 5,
            "format": "json"
        }
        parse_osti(citation, validation, validation.search_request(url, params))


