from PyPDF2 import PdfReader
from pathlib import Path
from docx import Document
import re

from .citation import Citation 

class Bibliography:
    def __init__(self):
        self.entries = []

    def parse(self, path, args):
        pdf_filename = path.name # e.g.filename.pdf
        pdf_stem = path.stem     # e.g. filename
        parent_dir = path.parent

        self.doc_path = parent_dir / "bibcheck" / f"{pdf_stem}.docx"
        print("Writing output to ", self.doc_path)

        #Convert PDF to text
        import fitz
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        text = re.sub(r'^\s*\d+\s*$\n?', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s+\.', '.', text)

        # Find the last instance of 'bibliography' or 'references'
        pattern = re.compile(
            r"(R\s*e\s*f\s*e\s*r\s*e\s*n\s*c\s*e\s*s|B\s*i\s*b\s*l\s*i\s*g\s*r\s*a\s*p\s*h\s*y)"
            r"(?:(?!\1).)*?(?=\[\s*1\s*\])",
            re.IGNORECASE | re.DOTALL,
        )
        if args.springer:
            pattern = re.compile(
                r"(R\s*e\s*f\s*e\s*r\s*e\s*n\s*c\s*e\s*s|B\s*i\s*b\s*l\s*i\s*g\s*r\s*a\s*p\s*h\s*y)"
                r"(?:(?!\1).)*?(?=(\[\s*1\s*\]|^\s*1\.))",
                re.IGNORECASE | re.DOTALL | re.MULTILINE,
            )
        matches = list(pattern.finditer(text))
        if not matches:
            print("No Bibliography Found")
            return 0

        m = matches[-1]
        start = m.end()

        # If "Appendix", stop before it
        if args.springer:
            m2 = re.search(r"\bOpen Access This chapter is licensed under the terms of\b", text[start:], re.IGNORECASE)
        else:
            m2 = re.search(r"\bAppendix\b", text[start:], re.IGNORECASE)
        if m2:
            end = start + m2.start()
            bib_text = text[start:end]
        else:
            bib_text = text[start:]

        LIGATURES = {
            "\ufb00": "ff",
            "\ufb01": "fi",
            "\ufb02": "fl",
            "\ufb03": "ffi",
            "\ufb04": "ffl",
        }

        for lig, repl in LIGATURES.items():
            bib_text = bib_text.replace(lig, repl)

        # Find each entry (beginning with [#]) and add to entries
        if args.springer:
            matches = []
            ctr = 1
            pos = 0
            lb = r"(?:^|[\n\r\f\u2028\u2029])"

            while True:
                m_cur = re.search(rf"{lb}\s*{ctr}\.\s+", bib_text[pos:])
                if not m_cur:
                    break
                start = pos + m_cur.end()

                m_next = re.search(rf"{lb}\s*{ctr+1}\.\s+", bib_text[start:])
                end = start + m_next.start() if m_next else len(bib_text)

                matches.append((ctr, bib_text[start:end]))
                ctr += 1
                pos = end
            
        else:
            pattern = r"\[(\d+)\]\s*(.+?)(?=\[\d+\]|\Z)"
            matches = re.findall(pattern, bib_text, re.DOTALL)
        for number, entry_text in matches:
            clean = " ".join(entry_text.split()).strip()
            if clean:
                if len(self.entries):
                    self.entries.append(Citation(number, clean, self.entries[-1], args))  
                else:
                    self.entries.append(Citation(number, clean, None, args))  

        return 1

    def validate(self, args):
        doc = None
        if args.write_out:
            doc = Document()
        
        incorrect_author_n= 0
        incorrect_title_n = 0
        incorrect_doi_n = 0
        correct_doi_n = 0
        num_excluded = 0
        matches = 0
        wrong_format = 0
        for entry in self.entries:
            correctness = entry.validate(doc)
            for key in correctness:
                if key == -1:
                    num_excluded += 1
                elif key == -2:
                    wrong_format += 1
                elif key == -3:
                    correct_doi_n += 1
                elif key == 0:
                    matches += 1
                elif key == 1:
                    incorrect_title_n += 1
                elif key == 2:
                    incorrect_author_n += 1
                elif key == 3:
                    incorrect_doi_n += 1

        if doc:
            print("Saving to ", self.doc_path)
            doc.save(self.doc_path)

        return [matches, num_excluded, wrong_format, incorrect_title_n, incorrect_author_n, correct_doi_n, incorrect_doi_n]
