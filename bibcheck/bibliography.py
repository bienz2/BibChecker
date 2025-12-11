from PyPDF2 import PdfReader
import re

from .citation import Citation 

class Bibliography:
    def __init__(self):
        self.entries = []

    def parse(self, args):
        #Convert PDF to text
        reader = PdfReader(args.pdf_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

        # Find the last instance of 'bibliography' or 'references'
        pattern = re.compile(
            r"(R\s*e\s*f\s*e\s*r\s*e\s*n\s*c\s*e\s*s|B\s*i\s*b\s*l\s*i\s*g\s*r\s*a\s*p\s*h\s*y)"
            r"(?:(?!\1).)*?(?=\[\s*1\s*\])",
            re.IGNORECASE | re.DOTALL,
        )
        matches = list(pattern.finditer(text))
        if not matches:
            print("No Bibliography Found")
            return 0

        m = matches[-1]
        start = m.end()

        # If "Appendix", stop before it
        m2 = re.search(r"\bAppendix\b", text[start:], re.IGNORECASE)
        if m2:
            end = start + m2.start()
            bib_text = text[start:end]
        else:
            bib_text = text[start:]

        # Find each entry (beginning with [#]) and add to entries
        pattern = r"\[(\d+)\]\s*(.+?)(?=\[\d+\]|\Z)"
        matches = re.findall(pattern, bib_text, re.DOTALL)
        for number, entry_text in matches:
            clean = " ".join(entry_text.split()).strip()
            if clean:
                self.entries.append(Citation(number, clean, args))  

        return 1

    def validate(self, args):
        for entry in self.entries:
            entry.validate()
        #self.entries[44].validate()
        #print(self.entries[16].entry)
