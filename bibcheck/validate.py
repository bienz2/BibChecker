import time
import feedparser
import requests
from urllib.parse import quote_plus
import Levenshtein

from datacite import DataCiteRESTClient
from habanero import Crossref
import arxiv
import re

cr = Crossref(timeout=30)
arxiv_client = arxiv.Client()

from .utils import normalize_authors, normalize_title, remove_special_chars

class Validate:
    def __init__(self, citation):
        self.title = ""
        self.authors = ""
        self.score_title = 0
        self.score_authors = 0


        if citation.excluded:
            self.match_percent = 1.0
            return

        if citation.doi:
            return self.search_doi(citation)

        if citation.arxiv_id:
            return self.search_arxiv_id(citation)

        if not citation.title:
            return self.search_no_title(citation)

        ## No or DOI Arxiv ID, parsed title and authors
        self.query_metadata(citation)

    def compare(self, citation, title, authors):
        if not title:
            return

        norm_title = normalize_title(title)
        score_title = Levenshtein.ratio(citation.norm_title, norm_title)
        if score_title < 1.0 and citation.norm_concat_title:
            score_title = max(score_title, Levenshtein.ratio(citation.norm_concat_title, norm_title))
        if score_title < 1.0 and citation.norm_hyphen_title:
            score_title = max(score_title, Levenshtein.ratio(citation.norm_hyphen_title, norm_title))

        if ":" in citation.title and score_title < 1.0:
            new_title = normalize_title(citation.title.split(':')[0])
            if (Levenshtein.ratio(new_title, norm_title) == 1.0):
                score_title = 1.0
        elif ":" in title and score_title < 1.0:
            new_title = normalize_title(title.split(':')[0])
            if (Levenshtein.ratio(citation.norm_title, new_title) == 1.0):
                score_title = 1.0

        if (score_title > self.score_title):
            self.score_title = score_title
            self.title = title
            self.authors = authors

        return score_title

    def compare_authors(self, citation):

        def extract_last_names(raw, from_list=False):
            names = []
            et_al_index = -1

            if from_list:
                iterable = raw
            else:
                cleaned = normalize_authors(raw)
                iterable = cleaned.split(',')

            idx = 0
            for entry in iterable:
                for name in entry.split('and'):
                    name = name.strip()
                    if not name:
                        continue

                    if "et al" in name.lower():
                        et_al_index = idx
                        return names, et_al_index

                    parts = name.split()
                    names.append(parts[-1].lower())
                    idx += 1

            return names, et_al_index


        list0, et_al0 = extract_last_names(citation.authors)
        list1, et_al1 = extract_last_names(self.authors, from_list=True)

        if et_al0 >= 0 and et_al1 < 0:
            list1 = list1[:et_al0]
        elif et_al1 >= 0 and et_al0 < 0:
            list0 = list0[:et_al1]

        auth_str0 = ", ".join(list0)
        auth_str0 = normalize_authors(auth_str0)
        auth_str1 = ", ".join(list1)
        auth_str1 = normalize_authors(auth_str1)

        self.score_authors = Levenshtein.ratio(auth_str0,auth_str1)




    def search_doi(self, citation):
        try:
            result = cr.works(ids=citation.doi)
        except Exception as e:
            result = None

        if result:
            title = result["message"].get("title", [""])
            if title:
                title = title[0]
                authors = []
                for a in result["message"].get("author", []):
                    name = a.get("family") or a.get("name") or ""
                    if name:
                        authors.append(name)

                if citation.title:
                    self.compare(citation, title, authors)
                
                self.title = title
                self.authors = authors

                return
        


        url = f"https://api.datacite.org/dois/{citation.doi}"
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
        except Exception:
            result = None

        if result:
            data = r.json().get("data", {}).get("attributes", {})
            title = data.get("titles", [{}])[0].get("title", "")
            creators = data.get("creators", [])
            authors = []
            for c in creators:
                name = c.get("familyName") or c.get("name") or ""
                if name:
                    name = name.strip()
                    parts = name.split()
                    last_name = parts[-1] if parts else name
                    authors.append(last_name)
            if citation.title:
                self.compare(citation, title, authors)

            self.title = title
            self.authors = authors

            return

    def search_arxiv_id(self, citation):
        api_url = f"http://export.arxiv.org/api/query?id_list={citation.arxiv_id}"
        try:
            feed = feedparser.parse(api_url)
            if not feed.entries:
                return

            arxiv_entry = feed.entries[0]
            title = arxiv_entry.get("title", "").strip()
            authors = list()
            for a in arxiv_entry.get("authors", []):
                name = a.name.strip()
                parts = name.split()
                last_name = parts[-1] if parts else name
                authors.append(last_name)

            if citation.title:
                self.compare(citation, title, authors);

            self.title = title
            self.authors = authors
        except Exception as e:
            return


    def search_no_title(self, citation):
        query = quote_plus(citation.entry)
        url = f"https://api.openalex.org/works?search={query}&per-page=1"
        time.sleep(0.5)
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                for i, work in enumerate(results[:1], start=1):
                    title = work.get("title", "")
                    authors = [a["display_name"] for a in work.get("authorships", [])]
                    self.title = title
                    self.authors = authors
                    return
        except Exception as e:
            return


    def query_metadata(self, citation): 
        self.search_openalex(citation, citation.norm_title)
        if self.score_title == 1:
            return
        self.search_crossref(citation, citation.norm_title)
        if self.score_title == 1:
            return
        self.search_arxiv(citation, citation.norm_title)
        if self.score_title == 1:
            return
        self.search_googlebooks(citation, citation.norm_title)
        if self.score_title == 1:
            return
        self.search_dblp(citation, citation.norm_title)
        if self.score_title == 1:
            return
        self.search_osti(citation, citation.norm_title)
        if self.score_title == 1:
            return

        if (citation.norm_concat_title):
            self.search_openalex(citation, citation.norm_concat_title)
            if self.score_title == 1:
                return
            self.search_crossref(citation, citation.norm_concat_title)
            if self.score_title == 1:
                return
            self.search_arxiv(citation, citation.norm_concat_title)
            if self.score_title == 1:
                return
            self.search_googlebooks(citation, citation.norm_concat_title)
            if self.score_title == 1:
                return
            self.search_dblp(citation, citation.norm_concat_title)
            if self.score_title == 1:
                return
            self.search_osti(citation, citation.norm_concat_title)
            if self.score_title == 1:
                return

        if (citation.norm_hyphen_title):
            self.search_openalex(citation, citation.norm_hyphen_title)
            if self.score_title == 1:
                return
            self.search_crossref(citation, citation.norm_hyphen_title)
            if self.score_title == 1:
                return
            self.search_arxiv(citation, citation.norm_hyphen_title)
            if self.score_title == 1:
                return
            self.search_googlebooks(citation, citation.norm_hyphen_title)
            if self.score_title == 1:
                return
            self.search_dblp(citation, citation.norm_hyphen_title)
            if self.score_title == 1:
                return
            self.search_osti(citation, citation.norm_hyphen_title)
            if self.score_title == 1:
                return

        self.search_openalex(citation, citation.entry)
        if self.score_title == 1:
            return

    def search_openalex(self, citation, search):
        query = quote_plus(search)
        url = f"https://api.openalex.org/works?search={query}&per-page=5"
        time.sleep(0.5)
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                for i, work in enumerate(results[:5], start=1):
                    title = work.get("title", "")
                    authors = [a["display_name"] for a in work.get("authorships", [])]
                    self.compare(citation, title, authors)
                    if self.score_title == 1:
                        return
        except Exception as e:
           return 

    def search_crossref(self, citation, search):
        time.sleep(0.5)
        try:
            result = cr.works(query = search, limit = 5)
            items = result.get("message", {}).get("items", [])
            for item in items:
                title = item.get("title", [""])[0]
                authors = [a.get("family", "").lower() for a in item.get("author", [])]
                self.compare(citation, title, authors)
                if self.score_title == 1.0:
                   return 
        except Exception as e:
            return  

    def search_dblp(self, citation, search):
        query = quote_plus(search)
        url = f"https://dblp.org/search/publ/api?q={query}&format=json&h=5"
        time.sleep(0.5)

        try:
            headers = {"User-Agent": "bibcheck/1.0"}
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()

            data = r.json()
            hits = (
                data.get("result", {})
                    .get("hits", {})
                    .get("hit", [])
            )

            if isinstance(hits, dict):
                hits = [hits]

            for hit in hits:
                info = hit.get("info", {})
                title = info.get("title") or ""
                authors_raw = info.get("authors", {}) or {}
                author_objs = authors_raw.get("author", [])
                if isinstance(author_objs, dict):
                    author_objs = [author_objs]

                authors = []
                for a in author_objs:
                    if isinstance(a, dict):
                        name = a.get("text") or a.get("name") or ""
                    else:
                        name = str(a)

                    if name:
                        name = re.sub(r"\s+0{3,}\d+$", "", name.strip())
                        authors.append(name)

                self.compare(citation, title, authors)
                if self.score_title == 1.0:
                    return

        except Exception:
            return


    def search_osti(self, citation, search):
        query = quote_plus(search)
        url = f"https://www.osti.gov/api/v1/records?q={query}&rows=5&format=json"
        time.sleep(0.5)

        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()

            records = data.get("records", []) or []

            for rec in records[:5]:
                title = (rec.get("title") or "").strip()

                authors = rec.get("authors") or []

                if isinstance(authors, str):
                    authors = [a.strip() for a in authors.split(";") if a.strip()]

                self.compare(citation, title, authors)
                if self.score_title == 1:
                    return

        except Exception:
            return



    def search_arxiv(self, citation, search):
        query = quote_plus(search)  
        url = f"http://export.arxiv.org/api/query?search_query=ti:%22{query}%22&max_results=5"
        time.sleep(0.5)
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            if r.status_code == 200:
                feed = feedparser.parse(r.text)
                entries = getattr(feed, "entries", [])
                for i, entry in enumerate(entries[:5], start=1):
                    title = (entry.get("title", "") or "").strip().replace("\n", " ")
                    authors = []
                    for a in entry.get("authors", []):
                        name = getattr(a, "name", None)
                        if name:
                            authors.append(name)

                    self.compare(citation, title, authors)
                    if self.score_title == 1:
                        return
        except Exception as e:
            return


    def search_googlebooks(self, citation, search):
        url = f"https://www.googleapis.com/books/v1/volumes?q={search}"
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                data = r.json()
                for item in data.get("items", []):
                    info = item.get("volumeInfo", {})
                    title = info.get("title") or ""
                    authors = info.get("authors", [])
                    self.compare(citation, title, authors)
        except Exception as e:
            return

