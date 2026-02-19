__all__=["parse_crossref", "search_crossref_doi", "search_crossref"]

def parse_crossref(citation, validation, results):
        if results is None:
            return

        items = results.json().get("message", {}).get("items", [])
        data = results.json()
        message = data.get("message", {})

        if "items" in message:
            items = message.get("items", [])
        else:
            items = [message]

        for item in items:
            title = item.get("title", [""])[0]
            authors = item.get("author")
            authors = [a.get("family", "").lower() for a in item.get("author", [])]
            validation.compare(citation, title, authors)
            if validation.score_title == 1.0 and validation.authors:
                return

            subtitle_list = item.get("subtitle", [])
            if subtitle_list:
                subtitle = subtitle_list[0].strip()
                title = f"{title}: {subtitle}"
                validation.compare(citation, title, authors)

def search_crossref_doi(citation, validation):
    url = f"https://api.crossref.org/works/{citation.doi}"
    parse_crossref(citation, validation, validation.search_request(url))
    if validation.score_title == 1.0 and validation.authors:
        return

    if citation.doi2:
        url = f"https://api.crossref.org/works/{citation.doi2}"
        parse_crossref(citation, validation, validation.search_request(url))


def search_crossref(citation, validation):
    url = "https://api.crossref.org/works"
    params = {
        "query": citation.norm_title,
        "rows": 5
    }
    parse_crossref(citation, validation, validation.search_request(url, params))
    if validation.score_title == 1.0 and validation.authors:
        return

    if citation.norm_concat_title:
        params = {
            "query": citation.norm_concat_title,
            "rows": 5
        }
        parse_crossref(citation, validation, validation.search_request(url, params))
