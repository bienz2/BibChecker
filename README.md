# BibChecker
Analyzes IEEE, SIAM, ACM, and Springer format bibliographies for correctness.  The tool parses an input PDF and checks the correctness of DOI links, ArXiv IDs, titles, and authors against online metadata.  Currently, the tool searches OpenAlex, Citeseer, Arxiv, Googlebooks, DBLP, and OSTI's openly available APIs.  This citation checker performs python string comparisons to check for correctness.  No generative AI tools are used when running this tool, allowing for it to be run during the paper review process. **This tool is only intended to be used as a first pass, not to replace human reviews.  Please manually verify all citations for which the tool is unable to find a match.**

Note: the arXiv API does not allow for checking against previous versions of papers.  **If either the title or authors fail to match against an arXiv paper, make sure to manually check previous versions.**

## Installing BibChecker
The bibcheck package can be installed with pip.  To install, run the following from the outermost directory:

`pip install .`

## Checking Citations in a PDF
After installing, you can check the accuracy of citations in a PDF through `bibcheck filename.pdf`

## Available Command Line Arguments
- `-ieee` : Assume IEEE-formatted bibliography (default)
- `-siam` : Assume SIAM-formatted bibliography
- `-acm` : Assume ACM-formatted bibliophgray
- `-springer` : Assume Springer-formatted bibliography
- `-write_out` : Saves output to a word .docx file instead of printing to stdout.

## Output
The codebase will output citation validation information, including the following.  If titles or author lists to not match searched metadata exactly, the closest match is output, and differences between the two are highlighted in red or orange.

- `# found exact title/author match`

- `# does not match expected <> format`

- `# excluded from search (exclusions.json match)`

- `<Parsed citation>` (unless matched exactly or excluded)

- 
    ```
    Title does not match searched metadata!
    GIVEN TITLE: ...
    FOUND TITLE: ...
    ```
    
- 
    ```
    Authors do not match metadata for FOUND TITLE!
    GIVEN AUTHORS: ...
    FOUND AUTHORS: ...
    ```

## Limitations
- Only validates against metadata stored in publicly available APIs (e.g. OpenAlex, arXiv, and similar).  Citations containing Github and common HPC websites are excluded from validation; will output `# excluded from search (exclusions.json match)`.
- Parsing PDFs is an error prone process.  When a citation cannot be validated, the original citation is output so that you can check it against the closest found match.
- Authors do not always conform to the expected citation format.  When this happens, this checker searches for a general match, potentially parsing incorrectly.  If a citation does not match the expected format, you will see `# does not match expected <ieee|acm|siam|springer> format`.
- Some PDFs are formatted in a way that they cannot be parsed with PdfParser.  In the few hundred papers I have tested, I did find one paper in which PdfParser returned text with 0 spaces.

## Exclusions file
The file `exclusions.json` includes keywords/phrases that indicates a citation should be excluded from the search.  For instance, if a reference contains a Github link, it is excluded from the search, as publicly available APIs will not be able to find codebases.  You can add additional exclusions by creating your own JSON file and passing it to the bibliography checker with `--exclude-file <exclusionfile.json>`.

## Please Provide Feedback
Please reach out if you have any issues!  I am also happy to parse additional bibliography formats.

## 
*ChatGPT was used to generate string comparison patterns and API search URLs.*
