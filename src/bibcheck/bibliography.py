from PyPDF2 import PdfReader
from pathlib import Path
from docx import Document
import re

from .citation import Citation 

class Bibliography:
    def __init__(self):
        self.entries = []

    def parse(self, args):
        pdf_path = Path(args.pdf_path).expanduser().resolve()

        pdf_filename = pdf_path.name # e.g.filename.pdf
        pdf_stem = pdf_path.stem     # e.g. filename
        parent_dir = pdf_path.parent

        bibcheck_dir = parent_dir / "bibcheck"
        bibcheck_dir.mkdir(exist_ok=True)
        self.doc_path = bibcheck_dir / f"{pdf_stem}.docx"

        #Convert PDF to text
        if args.siam:
            import fitz
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            text = re.sub(r'^\s*\d+\s*$\n?', '', text, flags=re.MULTILINE)
        else:
            reader = PdfReader(pdf_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            
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
        
        for entry in self.entries:
            entry.validate(doc)
        #self.entries[16].validate(doc)

        if doc:
            print("Saving to ", self.doc_path)
            doc.save(self.doc_path)
