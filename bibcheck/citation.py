import re
import feedparser
from urllib.parse import quote_plus

from .validate import Validate
from .utils import exclusions, remove_special_chars, normalize_title, normalize_concat_title, normalize_hyphen_title, format_for_url, normalize_authors

from .parse import patterns


class Citation:
    def __init__(self, number, entry, args):
        self.match_percent = 0
        self.match_title = None
        self.number = number

        entry = remove_special_chars(entry)
        self.entry = entry

        self.excluded = False
        lower = format_for_url(self.entry)
        for pattern, label in exclusions.items():
            if pattern in lower:
                self.excluded = True
                return

        # Find DOI
        self.doi = None
        self.arxiv_id = None
        doi_entry = re.sub(
                r'(https?://doi\.org/10\.\d{4,9}/\S+)\s+(\d+)\b',
                r'\1_\2',
                entry,
            )
        doi_entry = re.sub(r'\.\s*\n\s*(\d)', r'.\1', doi_entry)
        doi_match = re.search(r"(10\.\d{4,9}/[^\s\"<>]+)", doi_entry)
        if doi_match:
            self.doi = doi_match.group(1).rstrip('.,;)')
        else:
            # Find ArXiv 
            m = re.search(
                r"(?:arXiv\s*:\s*|https?://arxiv\.org/abs/)"
                r"([0-9]{4}\.[0-9]{4,5}(?:v\d+)?|[a-z\-]+/\d{7}(?:v\d+)?)",
                entry,
                re.I,
            )
            if m:
                self.arxiv_id = m.group(1)


        # Split into title, author, venue
        m = None

        pattern_2 = None
        pattern_1 = None
        if args.acm:
            pattern_3 = patterns.acm_pattern_3
            pattern_2 = patterns.acm_pattern_2
            pattern_1 = patterns.acm_pattern_1
        elif args.siam:
            pattern_3 = patterns.siam_pattern_3
            pattern_2 = patterns.siam_pattern_2
            pattern_1 = patterns.siam_pattern_1
        else:
            pattern_3 = patterns.ieee_pattern_3 
            pattern_2 = patterns.ieee_pattern_2
            pattern_1 = patterns.ieee_pattern_1

        if ",and " in entry: # 3+ authors
            m = re.search(pattern_3, entry, re.DOTALL | re.VERBOSE)
        
        if not m and " and " in entry: # 2 authors
            m = re.search(pattern_2, entry, re.DOTALL | re.VERBOSE)
        
        if not m:
            m = re.search(pattern_1, entry, re.DOTALL | re.VERBOSE)


        # If title/authors/etc not found, try other patterns
        if not m:
            m = re.search(patterns.ieee_pattern_3, entry, re.DOTALL | re.VERBOSE)

        if not m and ",and " in entry:
            m = re.search(patterns.gen_pattern_3, entry, re.DOTALL | re.VERBOSE)

        if not m and " and " in entry:
            m = re.search(patterns.gen_pattern_2, entry, re.DOTALL | re.VERBOSE)

        if not m:
            m = re.search(patterns.gen_pattern_1, entry, re.DOTALL | re.VERBOSE)


        self.title = None
        self.authors = None
        if m:
            self.title = m.group("title").strip(' ,')
            self.authors = m.group("authors").strip(" ,")
            self.authors = remove_special_chars(self.authors)

            year_match = re.search(r'(?<![\d/])\b(19|20)\d{2}\b(?![\d/])', self.title)
            if year_match:
                year = year_match.group(0)
                self.title = self.title.replace(year, '')

                    
        self.norm_title = None
        self.norm_concat_title = None
        self.norm_hyphen_title = None
        if self.title:
            self.norm_title = normalize_title(self.title)

            if '- ' in self.title:
                self.norm_concat_title = normalize_concat_title(self.title)
                self.norm_hyphen_title = normalize_hyphen_title(self.title)

    def validate(self):
        if self.excluded:
            return

        validation = Validate(self)
        if validation.score_title != 1.0:
            print("\n")
            print("\n")
            print(self.number, self.entry)
            print("Titles do not match!")
            if self.doi:
                print("DOI NOT A MATCH! ", self.doi)
            elif self.arxiv_id:
                print("ARXIV ID NOT A MATCH! ", self.arxiv_id)
            print("GIVEN: ", self.title)
            print("FOUND: ", validation.title)
        else:
            validation.compare_authors(self)
            if validation.score_authors < 0.9:
                print("\n")
                print("\n")
                print(self.number, self.entry)
                print("Authors do not match!")
                print(self.authors)
                print(validation.authors)

