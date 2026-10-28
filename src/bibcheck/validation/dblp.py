__all__ = ["parse_dblp", "search_dblp"]

import re
import requests

def parse_dblp(citation, validation, results):
    if results is None or not results.ok:
        return

    data = ""
    try:
        data = results.json().get("result", {}).get("hits", {}).get("hit", [])
    except requests.exceptions.JSONDecodeError:
        return

    if isinstance(data, dict):
        data = [data]
    for item in data:
        info = item.get("info", {})
        title = info.get("title") or ""
        author_list = info.get("authors", {}).get("author", [])
        if isinstance(author_list, dict):
            author_list = [author_list]
        authors = []
        for a in author_list:
            if isinstance(a, dict):
                name = a.get("text") or a.get("name") or ""
            else:
                name = str(a)

            if name:
                name = re.sub(r"\s+\d{4}$", "", name)
                authors.append(name)

        validation.compare(citation, title, authors)
        if validation.score_title == 1.0 and validation.authors:
            return

def search_dblp(citation, validation):
    url = "https://dblp.org/search/publ/api"
    params = {
        "q": citation.norm_title,
        "format": "json",
        "h": 5
    }
    parse_dblp(citation, validation, validation.search_request(url, params))
    if validation.score_title == 1.0 and validation.authors:
        return

    if citation.norm_concat_title:
        params = {
            "q": citation.norm_concat_title,
            "format": "json",
            "h": 5
        }
        parse_dblp(citation, validation, validation.search_request(url, params))
