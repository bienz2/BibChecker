import time
import requests
from urllib.parse import quote_plus
import Levenshtein

from habanero import Crossref
import arxiv
import re

HEADERS = { "User-Agent": "BibChecker"}

from time import sleep
from .utils import *
from .validation import *

HYPHENS = r"[\u2010\u2011\u2012\u2013\u2014\u2212-]"
HYPHEN_SPACE = rf"{HYPHENS}\s+"

class Validate:
    def __init__(self, citation):
        self.title = ""
        self.authors = ""
        self.score_title = 0
        self.score_authors = 0
        self.arxiv_version_count = 0
        self.wrong_doi = 0
        self.doi_title = ""
        self.doi_authors = ""

        if citation.excluded:
            self.match_percent = 1.0
            return

        if citation.doi:
            search_crossref_doi(citation, self)
            if self.score_title == 1.0 and self.authors:
                return
            search_datacite_doi(citation, self)
            if self.score_title == 1.0:
                return
            self.wrong_doi = 1
            self.doi_title = self.title
            self.doi_authors = self.authors

        if citation.arxiv_id:
            search_arxiv_id(citation, self)
            if self.score_title == 1.0:
                return
            self.wrong_doi = 1
            self.doi_title = self.title
            self.doi_authors = self.authors


        if not citation.norm_title:
            return search_no_title(citation, self)

        ## No or DOI Arxiv ID, parsed title and authors
        # 1. Search OpenAlex
        search_openalex(citation, self)
        if self.score_title == 1.0 and self.authors:
            return

        #2. Search Crossref
        search_crossref(citation, self)
        if self.score_title == 1.0 and self.authors:
            return
        self.query_metadata(citation)

    def query_metadata(self, citation): 
        search_openalex(citation, self)
        if self.score_title == 1 and self.authors:
            return
        search_dblp(citation, self)
        if self.score_title == 1 and self.authors:
            return
        search_crossref(citation, self)
        if self.score_title == 1 and self.authors:
            return
        search_arxiv(citation, self)
        if self.score_title == 1 and self.authors:
            return
        search_googlebooks(citation, self)
        if self.score_title == 1 and self.authors:
            return
        search_osti(citation, self)
        if self.score_title == 1 and self.authors:
            return

    # Compare Cited and Found Titles, using Levenshtein ratio 
    def compare(self, citation, title, authors):
        if not title:
            return

        # Compare normalized cited and found titles
        norm_title = normalize_title(title)
        score_title = Levenshtein.ratio(citation.norm_title, norm_title)
        best = norm_title
        cit_best = citation.norm_title
        best_score = score_title

        # If no perfect match, try removing symbols in both titles
        if score_title < 1.0 and citation.norm_title:
            condensed_title = re.sub(r"[-,.\s'`:]+", "", citation.norm_title)
            condensed_title_found = re.sub(r"[-,.\s'`:]+", "", norm_title)
            score_condensed = Levenshtein.ratio(condensed_title, condensed_title_found)
            if score_condensed > score_title:
                best = condensed_title_found
                cit_best = condensed_title
                best_score = score_condensed

        # If better match than current best
        # Or already have a perfect match, but found authors
        if (best_score > self.score_title or (self.score_title  == 1.0 and authors)):
            self.score_title = best_score
            self.title = title
            self.authors = authors 
            self.best_match = best
            citation.best_match = cit_best

        return score_title


    # Compare Cited and Found Authors, using Levenstein ratio
    def compare_authors(self, citation, last_first = False):
        if (citation.authors):
            citation.authors = re.sub(HYPHEN_SPACE, "", citation.authors)        
            citation.authors = re.sub(HYPHENS, " ", citation.authors)

        if self.authors:
            self.authors = [re.sub(HYPHENS, " ", a) for a in self.authors]


        list0, list1 = replace_et_al(citation.authors, self.authors, last_first)

        list2 = None
        if self.doi_authors:
            self.doi_authors = [re.sub(HYPHENS, " ", a) for a in self.doi_authors]
            _, list2 = replace_et_al(citation.authors, self.doi_authors, last_first)

        if not list0 or not list1:
            self.score_authors = 0
            return list0, list1, list2

        auth_str0 = ", ".join(list0)
        auth_str0 = normalize_authors(auth_str0)
        auth_str1 = ", ".join(list1)
        auth_str1 = normalize_authors(auth_str1)

        self.score_authors = Levenshtein.ratio(auth_str0,auth_str1)
        return list0, list1, list2


    # Search a given URL for params
    # Include header stating BibChecker is sending request
    def search_request(self, url, params=None):
        sleep(0.5)
        try:
            r = requests.get(url, params = params, headers=HEADERS, timeout=20)
            r.raise_for_status()
            return r
        except Exception as e:
            return None




















