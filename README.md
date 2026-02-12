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

## Limitations
- Currently, this only validates against metadata stored in publicly available APIs (e.g. OpenAlex, arXiv, and similar).  It cannot currently validate codebases and websites.  Github and common HPC websites are listed in an exclusions file, and if these URLs are found within a citation, the given citation is not validated.  When this happens, you will see `# excluded from search (exclusions.json match)`.
- Parsing citations with `PdfReader` and manual string comparisons is an error prone approach.  You may see parsings, particularly author names, that do not match the original citation.  When this happens, you can compare FOUND AUTHORS directly against the original citation, in the format should below.  If something looks odd, you may have run into a PDF that cannot be accurately parsed with PdfReader.  I have run this across a few hundred papers, and found one in which PdfReader output text with 0 spaces.
```
<Original Citation, e.g. author0, author1. "Title". etc>

Authors do not match metadata for FOUND TITLE!
GIVEN AUTHORS:  author0, author1, ...

FOUND AUTHORS: author0, author1, ...
```
- Authors do not also follow the expected citation format.  When this happens, this checker parses for a general match, likely introducing errors into the parsed author list and titles.  If a citation does not match the expected format, you will see `2 does not match expected <ieee|acm|siam|springer> format`.

## Exclusions file
The file `exclusions.json` includes keywords/phrases that indicates a citation should be excluded from the search.  For instance, if a reference contains a Github link, it is excluded from the search, as publicly available APIs will not be able to find codebases.  You can add additional exclusions by creating your own JSON file and passing it to the bibliography checker with `--exclude-file <exclusionfile.json>`.

## Output
The codebase will output citation validation information, including the following.  If titles or author lists to not match searched metadata exactly, the closest match is output, and differences between the two are highlighted in red or orange.

- \# found exact title/author match

- \# does not match expected \<\> format

- \# excluded from search (exclusions.json match)

- \<Parsed citation\> (unless matched exactly or excluded)

- Title does not match searched metadata!
    GIVEN TITLE: ...
    FOUND TITLE: ...
    
- Authors do not match metadata for FOUND TITLE!
    GIVEN AUTHORS: ...
    FOUND AUTHORS: ...

## Please Provide Feedback
Please reach out if you have any issues!  I am also happy to parse additional bibliography formats.

## 
*ChatGPT was used to generate string comparison patterns and API search URLs.*
