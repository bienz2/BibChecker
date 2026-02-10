# BibChecker
Analyzes IEEE, SIAM, ACM, and Springer format bibliographies for correctness.  The tool parses an input PDF and checks the correctness of DOI links, ArXiv IDs, titles, and authors against online metadata.  Currently, the tool searches OpenAlex, Citeseer, Arxiv, Googlebooks, DBLP, and OSTI's openly available APIs.  This citation checker performs python string comparisons to check for correctness.  No generative AI tools are used when running this tool, allowing for it to be run during the paper review process. **This tool is only intended to be used as a first pass, not to replace human reviews.  Please verify all output for false positives.**

Note: the arXiv API does not allow for checking against previous versions of papers.  **If either the titles or authors fail to match against an arXiv paper, make sure to manually check previous versions.**

## Installing BibChecker
The bibcheck package can be installed with pip.  To install, run the following from the outermost directory:

`pip install .`

## Checking Citations in a PDF
After installing, you can check the accuracy of citations in a PDF through `bibcheck filename.pdf`

## Available Command Line Arguments
`-ieee` : Assume IEEE-formatted bibliography (default)
`-siam` : Assume SIAM-formatted bibliography
`-acm` : Assume ACM-formatted bibliophgray
`-springer` : Assume Springer-formatted bibliography
`-write_out` : Saves output to a word .docx file instead of printing to stdout.

*Acknowledgement: ChatGPT was used to generate string comparison patterns and API search URLs.*
