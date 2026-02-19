import regex
import re
import feedparser
from urllib.parse import quote_plus
from docx import Document
from docx.shared import RGBColor

from .validate import Validate
from .utils import exclusions, remove_special_chars, normalize_title, normalize_title_concat, format_for_url, normalize_authors, remove_line_numbers
from .parse import patterns
from .write_output import *

class Citation:
    authors = None

    def __init__(self, number, entry, prev_citation, args):
        self.match_percent = 0
        self.match_title = None
        self.number = number
        self.correct_format = 1
        self.format = 'ieee'
        self.last_first = False

        if args.acm:
            self.format = 'acm'
        elif args.siam: 
            self.format = 'siam'
        elif args.springer:
            self.format = 'springer'
            self.last_first = True

        entry = remove_special_chars(entry)
        if args.siam:
            entry = remove_line_numbers(entry)
        self.entry = entry

        self.excluded = False
        lower = format_for_url(self.entry)
        for pattern, label in exclusions.items():
            if pattern in lower:
                self.excluded = True
                return

        # Remove IEEE Watermark
        ieee_notice = re.compile(
            r"""
            Authorized\s+licensed\s+use\s+limited\s+to:.*?
            Downloaded\s+on\s+.*?
            from\s+IEEE\s+Xplore\.\s*
            Restrictions\s+apply\.?
            """,
            re.IGNORECASE | re.DOTALL | re.VERBOSE,
        )
        entry = ieee_notice.sub("", entry)
        entry = re.sub(
            r"\b97[89][-–]\d{1,5}[-–]\d{1,7}[-–]\d{1,7}[-–]\d\b.*?IEEE",
            "",
            entry,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Find DOI
        self.doi = None
        self.doi2 = None
        self.arxiv_id = None
        doi_entry = re.sub(
            r'((?:doi:\s*|https?://doi\.org/)10\.\d{4,9}/\S*?-)\s+(\S+)',
            r'\1\2',
            entry,
        )
        doi_entry = re.sub(
            r'((?:doi:\s*|https?://doi\.org/)10\.\d{4,9}/\S*?\.)\s+((?:\d+\.)*\d+)\b',
            r'\1\2',
            doi_entry,
        )
        doi_entry = re.sub(r'\.\s*\n\s*(\d)', r'.\1', doi_entry)
        doi_entry2 = re.sub(
            r'((?:doi:\s*|https?://doi\.org/)10\.\d{4,9}/\S+?)\s+(\d+)\b',
            r'\1_\2',
            doi_entry,
        )
        doi_entry2 = re.sub(r'\.\s*\n\s*(\d)', r'.\1', doi_entry2)

        try:
            doi_match = regex.search(r"(10\.\d{4,9}/[^\s\"<>]+)", doi_entry, timeout=0.1)
        except TimeoutError:
            doi_match = None

        if doi_match:
            self.doi = doi_match.group(1).rstrip('.,;)')
            try:
                doi_match = regex.search(r"(10\.\d{4,9}/[^\s\"<>]+)", doi_entry2, timeout = 0.1)
            except TimeoutError:
                doi_match = None
            if doi_match:
                self.doi2 = doi_match.group(1).rstrip('.,;)')

        else:
            # Find ArXiv 
            try:
                m = regex.search(
                    r"(?:arXiv\s*:\s*|https?://arxiv\.org/abs/)"
                    r"([0-9]{4}\.[0-9]{4,5}(?:v\d+)?|[a-z\-]+/\d{7}(?:v\d+)?)",
                    entry,
                    regex.I,
                    timeout=0.1
                )
            except TimeoutError:
                m = None
            if m:
                self.arxiv_id = m.group(1)


        # Split into title, author, venue
        m = None

        pattern_2 = None
        pattern_1 = None
        pattern_et_al = None
        if args.acm:
            pattern_3 = patterns.acm_pattern_3
            pattern_2 = patterns.acm_pattern_2
            pattern_1 = patterns.acm_pattern_1
            pattern_et_al = patterns.acm_pattern_et_al
        elif args.siam:
            pattern_3 = patterns.siam_pattern_3
            pattern_2 = patterns.siam_pattern_2
            pattern_1 = patterns.siam_pattern_1
            pattern_et_al = patterns.siam_pattern_et_al
        elif args.springer:
            pattern_3 = patterns.springer_pattern_3
            pattern_2 = patterns.springer_pattern_2
            pattern_1 = patterns.springer_pattern_1
            pattern_et_al = patterns.springer_pattern_et_al
        else:
            pattern_3 = patterns.ieee_pattern_3 
            pattern_2 = patterns.ieee_pattern_2
            pattern_1 = patterns.ieee_pattern_1
            pattern_et_al = patterns.ieee_pattern_et_al

        if "et al" in entry:
            try: 
                m = regex.search(pattern_et_al, entry, flags = re.DOTALL | re.VERBOSE, timeout = 0.1)
            except TimeoutError:
                m = None

        if not m and (args.springer or ", and " in entry): # 3+ authors
            try:
                m = regex.search(pattern_3, entry, flags = re.DOTALL | re.VERBOSE, timeout = 0.1)

            except TimeoutError:
                m = None
        
        if not m and (args.springer or " and " in entry): # 2 authors
            try:
                m = regex.search(pattern_2, entry, flags = re.DOTALL | re.VERBOSE, timeout = 0.1)

            except TimeoutError:
                m = None

        if not m:
            try:
                m = regex.search(pattern_1, entry, flags = re.DOTALL | re.VERBOSE, timeout = 0.1)
            except TimeoutError:
                m = None

        if not m:
            self.correct_format = 0

        # If title/authors/etc not found, try other patterns
        if not m:
            try:
                m = regex.search(patterns.ieee_pattern_3, entry, flags = re.DOTALL | re.VERBOSE, timeout = 0.1)
                if m and "Bruneo" in entry:
                    print("Matched ieee")
            except TimeoutError:
                m = None

        if not m and ", and " in entry:
            try:
                m = regex.search(patterns.gen_pattern_3, entry, flags = re.DOTALL | re.VERBOSE, timeout = 0.1)
            except TimeoutError:
                m = None

        if not m and " and " in entry:
            try:
                m = regex.search(patterns.gen_pattern_2, entry, flags = re.DOTALL | re.VERBOSE, timeout = 0.1)
                if m and "Bruneo" in entry:
                    print("Matched gen 2")
            except TimeoutError:
                m = None

        if not m and "et al" in entry:
            try:
                m = regex.search(patterns.gen_pattern_et_al, entry, flags = re.DOTALL | re.VERBOSE, timeout = 0.1)
            except TimeoutError:
                m = None

        if not m:
            try:
                m = regex.search(patterns.gen_pattern_1, entry, flags = re.DOTALL | re.VERBOSE, timeout = 0.1)
            except TimeoutError:
                m = None


        self.title = None
        self.authors = None
        self.best_match = None
        if m:
            self.title = m.group("title").strip(' ,')
            self.best_match = self.title
            self.authors = m.group("authors").strip(" ,")
            self.authors = remove_special_chars(self.authors)

            if self.authors == '--':
                self.authors = prev_citation.authors

        self.norm_title = None
        self.norm_concat_title = None
        if self.title:
            self.norm_title = normalize_title(self.title)
            self.norm_concat_title = normalize_title_concat(self.title)




    def color(self, list0, list1):

        seg0 = []
        for a in (list0 or []):
            if a in set1:
                seg0.append((a, None))
            else:
                seg0.append((a, RED))

        seg1 = []
        for a in (list1 or []):
            if a in set0:
                seg1.append((a, None))
            else:
                seg1.append((a, ORANGE))

        return seg0, seg1


    def add_runs(paragraph, segments):
        for text, color in segments:
            run = paragraph.add_run(text)
            if color is not None:
                run.font.color.rgb = color

    def color(self, list0, list1, RED, ORANGE):
        set0 = set(list0 or [])
        set1 = set(list1 or [])

        colored_0 = []
        if list0:
            for a in list0:
                if a in set1:
                    colored_0.append((a, None))
                else: 
                    colored_0.append((a, RED))

        colored_1 = []
        if list1:
            for a in list1:
                if a in set0:
                    colored_1.append((a, None))
                else:
                    colored_1.append((a, ORANGE))

        return colored_0, colored_1

    def validate(self, doc):
        [RED, ORANGE, BLUE, GREEN, DIM] = get_colors(doc)
        
        if self.excluded:
            write_output(f"{self.number} excluded from search (exclusions.json match)", doc, BLUE)
            return

        if self.correct_format == 0:
            write_output(f"{self.number} does not match expected {self.format} format", doc, BLUE)


        validation = Validate(self)
        list0, list1 = validation.compare_authors(self, self.last_first)

        if validation.score_title == 1.0 and validation.score_authors == 1.0:
            write_output(f"{self.number} found exact title/author match", doc, GREEN)
            return

        write_output(f"{self.number} {self.entry}", doc, ORANGE)

        if validation.wrong_doi:
            if self.doi:
                write_output(f"Title NOT found using DOI {self.doi} or {self.doi2}", doc, RED)
            elif self.arxiv_id:
                write_output(f"Title NOT found using ARXIV ID {self.arxiv_id}", doc, RED)
                if validation.arxiv_version_count:
                    write_output(f"ArXIV Version Count is {validation.arxiv_version_count}, Manually compare against older versions!", doc, BLUE)

        if validation.score_title != 1.0:
            title0 = self.norm_title.split(" ") if self.norm_title else []
            title1 = normalize_title(validation.title).split(" ") if validation.title else []
            colored_0, colored_1 = self.color(title0, title1, RED, ORANGE)

            write_output("Title does not match searched metadata!", doc, RED)

            write_multi_output("GIVEN TITLE: ", DIM, colored_0, doc)
            write_multi_output("FOUND TITLE: ", DIM, colored_1, doc)


        if validation.score_authors < 1.0:
            a0, a1 = self.color(list0, list1, RED, ORANGE)
            write_output("Authors do not match metadata for FOUND TITLE!", doc, RED)
            
            write_multi_output("GIVEN AUTHORS: ", DIM, a0, doc)
            write_multi_output("FOUND AUTHORS: ", DIM, a1, doc)
                

        else:
            write_output("Authors match!", doc, BLUE)

        write_output(" ", doc)
        write_output(" ", doc)

