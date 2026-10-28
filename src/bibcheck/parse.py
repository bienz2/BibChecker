class patterns:
    acm_pattern_3 = r'''
        ^(?P<authors>
            (?:\b[A-Z]\.|[^.\d])*?     # No periods unless they follow 1 capital letter (initial)            
            ,\s*and\b\s*             # Must find `, and` before last author
            (?:\b[A-Z]\.|[^.\d]+)*?
        )
        [\.]\s*                         # period after authors
            (?P<year>(19|20)\d{2})\b
        [\.]\s*                         # period after year
        (?P<title>
            (?:[^.?]|\.(?!\s))+
        )
        .*$
        '''
    acm_pattern_2 = r'''
            ^
            (?P<authors>
                (?:
                    \b[A-Z]\.                 # allowed initial
                  | (?!\.) .                  # any char except a period
                )*
                \sand\s+(?=[A-Z])             # " and " must occur before first real period
                (?:
                    \b[A-Z]\.
                  | (?!\.) .
                )*
                \b[A-Za-z]{2,}                # final author word
            )
            \.\s*                             # FIRST real period — end of authors
            (?P<year>(19|20)\d{2})
            \.\s*
            (?P<title>[^.]+)                  # title has NO periods
            \.
            .*$
        '''
    acm_pattern_et_al = r'''
            ^(?P<authors>
                (?:\b[A-Z]\.|[^.\d])*?     # same looseness as other patterns
                \bet\s+al\s*\.?                 # literal "et al."
            )
            \s*
            (?P<year>(19|20)\d{2})\b
            [\.]\s*
            (?P<title>
                (?:[^.?]|\.(?!\s))+
            )
            .*$
            '''    

    acm_pattern_1 = r'''
            ^
            (?P<authors>
                (?:
                    \b[A-Z]\.            # single-letter initial
                  | [^.\d]               # anything else but period/digit
                )*
                \b[A-Za-z]{2,}           # final author word (≥2 letters)
            )
            \.\s*
            (?P<year>(19|20)\d{2})
            \.\s*
            (?P<title>[^.]+)
            \.
            .*$
        '''  

    siam_pattern_3 = r'''
            ^
            (?P<authors>
                (?:\s*[^\s,]+(?:\s+[^\s,]+){0,2}\s*,){2,}
                \s*and\s+
                [^\s,]+(?:\s+[^\s,]+){0,2}
            )
            \s*,\s*                    # comma after authors
            (?P<title>.+?)                   # title up to next comma
            \s*,\s*
            (?P<rest>.+?)                    # everything after title
            (?:                              # year may appear in two forms
                \(\s*(?P<year_paren>(19|20)\d{2})\s*\)   # (2015)
              |
                \b(?P<year_plain>(19|20)\d{2})\b         # 2011
            )
            .*$
        '''
    siam_pattern_2 = r'''
            ^
            (?P<authors>
                [^\s,]+(?:\s+[^\s,]+){0,2}
                \s+and\s+
                [^\s,]+(?:\s+[^\s,]+){0,2}
            )
            \s*,\s*                # comma after authors
            (?P<title>.+?)                   # title up to next comma
            \s*,\s*
            (?P<rest>.+?)                    # everything after title
            (?:                              # year may appear in two forms
                \(\s*(?P<year_paren>(19|20)\d{2})\s*\)   # (2015)
              |
                \b(?P<year_plain>(19|20)\d{2})\b         # 2011
            )
            .*$
        '''
    siam_pattern_et_al = r'''
            ^
            (?P<authors>
                [^\s,]+(?:\s+[^\s,]+){0,2}
                \s+et\s+al\.?
            )
            \s*,\s*
            (?P<title>.+?)                   # title up to next comma
            \s*,\s*
            (?P<rest>.+?)                    # everything after title
            (?:                              # year may appear in two forms
                \(\s*(?P<year_paren>(19|20)\d{2})\s*\)   # (2015)
              |
                \b(?P<year_plain>(19|20)\d{2})\b         # 2011
            )
            .*$
        '''
        
    siam_pattern_1 = r'''
            ^
            (?P<authors>
                [^,]+?
            )
            \s*,\s*
            (?P<title>.+?)                   # title up to next comma
            \s*,\s*
            (?P<rest>.+?)                    # everything after title
            (?:                              # year may appear in two forms
                \(\s*(?P<year_paren>(19|20)\d{2})\s*\)   # (2015)
              |
                \b(?P<year_plain>(19|20)\d{2})\b         # 2011
            )
            .*$
        '''

    springer_pattern = r'''
            ^
            (?P<authors>[^:\d]+?)          # authors cannot contain colon
            \s*:\s*
            (?P<title>.*?)
            (?=                          # stop title right before...
                \.\s*                    # 1) a period
              | \s*\(                    # 2) an opening parenthesis
              | \s+(?:19|20)\d{2}\b      # 3) a 4-digit year
            )
            .*$
        '''
    springer_pattern_3 = springer_pattern
    springer_pattern_2 = springer_pattern
    springer_pattern_et_al = springer_pattern
    springer_pattern_1 = springer_pattern

    ieee_pattern = r'^(?P<authors>.*?)\s*[\u201C\u201D"](?P<title>[^"\u201C\u201D]+)[\u201C\u201D"]'
    ieee_pattern_3 = ieee_pattern
    ieee_pattern_2 = ieee_pattern
    ieee_pattern_et_al = ieee_pattern
    ieee_pattern_1 = ieee_pattern


    # Shared tail: comma after authors, title, venue, year.
    _ams_tail = r'''
        ,\s*                                    # comma after authors
        (?P<title>
            (?:[^.]|\.(?!\s))+?                 # no ". " inside the title
        )
        ,\s+                                    # comma after title, then venue starts:
        (?=[A-Z0-9]|in\s|preprint|arXiv|available|to\s+appear|submitted|Ph\.\s*D)
        .*?                                     # venue, volume, publisher ...
        (?:
            \(\s*(?:[^()]*?[,\s])?              # "(1976)"  "(Berlin, 1986)"  "(Oct. 2019)"
          | ,\s+(?:[A-Z][a-z]+\.?\s+)?          # ", 1999."  ", July 2020."  (books, misc)
        )
        (?P<year>(?:19|20)\d{2})
        (?=\)|[.,;]?(?:\s|$))                   # year not followed by "–pages" etc.
        .*$
        '''

    # One author: starts with a capital; no commas or digits; periods only
    # after an initial (B.  Th.  J.-P.).
    _one = r'(?=[A-Z])(?:\b[A-Z][a-z]?\.|[^.\d,])+?'

    ams_pattern_3 = r'''
        ^(?P<authors>
            ''' + _one + r'''
            (?:,\s*''' + _one + r''')*?         # more authors
            ,\s*and\s+                          # must find `, and` before last author
            ''' + _one + r'''
        )
        ''' + _ams_tail

    ams_pattern_et_al = r'''
        ^(?P<authors>
            (?=[A-Z])(?:\b[A-Z][a-z]?\.|[^.\d])*?   # one or more authors, commas allowed
            \bet\s+al\.                             # literal "et al."
        )
        ''' + _ams_tail

    ams_pattern_2 = r'''
        ^(?P<authors>
            ''' + _one + r'''
            \s+and\s+                           # " and " before the first comma
            ''' + _one + r'''
        )
        ''' + _ams_tail

    ams_pattern_1 = r'''
        ^(?!                                    # not a plain/ACM list "A, B, and C." ending in a period
            ''' + _one + r'''(?:,\s*''' + _one + r''')*,?\s*(?:and\s+''' + _one + r''')?(?<!\b[A-Z])(?<!\b[A-Z][a-z])\.\s
        )
        (?P<authors>
            ''' + _one + r'''
          | [—–\-_]{2,}                         # \bysame dash for a repeated author
        )
        ''' + _ams_tail   



    
    plain_pattern_3 = r'''
        ^(?P<authors>
            (?:\b[A-Z]\.|[^.\d])*?          # No periods unless they follow 1 capital letter (initial)
            ,\s*and\s+                      # Must find `, and` before last author
            (?:\b[A-Z]\.|[^.\d,])+?         # last author: no commas
        )
        (?<![^A-Za-z][A-Z])                 # authors don't end on an initial ("H." is not the end)
        \.\s+                               # period after authors
        (?P<title>
            (?!(?:19|20)\d{2}\.)            # title is not a bare year (rejects ACM)
            (?:[^.?!]|[.?!](?!\s))+?        # no ". " inside the title
        )
        (?:
            [.?!]\s+ .*? [,\s]\s*           # end of title, then venue/volume/pages...
          | ,\s* (?:[A-Z][a-z]+\.?\s+)?     # ...or @misc: "Title, 2021." / "Title, May 2021."
        )
        (?P<year>(?:19|20)\d{2})
        \.(?:\s|$)                          # period after year
        .*$
        '''

    plain_pattern_et_al = r'''
        ^(?P<authors>
            (?:\b[A-Z]\.|[^.\d])*?          # same looseness as other patterns
            \bet\s+al\.                     # literal "et al."
        )
        \s+
        (?P<title>
            (?!(?:19|20)\d{2}\.)
            (?:[^.?!]|[.?!](?!\s))+?
        )
        (?:
            [.?!]\s+ .*? [,\s]\s*
          | ,\s* (?:[A-Z][a-z]+\.?\s+)?
        )
        (?P<year>(?:19|20)\d{2})
        \.(?:\s|$)
        .*$
        '''

    plain_pattern_2 = r'''
        ^(?P<authors>
            (?:\b[A-Z]\.|[^.\d,])+?         # first author: no commas
            \s+and\s+                       # " and " before first real period
            (?:\b[A-Z]\.|[^.\d,])+?         # second author: no commas
        )
        (?<![^A-Za-z][A-Z])
        \.\s+                               # period after authors
        (?P<title>
            (?!(?:19|20)\d{2}\.)
            (?:[^.?!]|[.?!](?!\s))+?
        )
        (?:
            [.?!]\s+ .*? [,\s]\s*
          | ,\s* (?:[A-Z][a-z]+\.?\s+)?
        )
        (?P<year>(?:19|20)\d{2})
        \.(?:\s|$)
        .*$
        '''

    plain_pattern_1 = r'''
        ^(?P<authors>
            (?:\b[A-Z]\.|[^.\d,])+?         # single author: no commas
        )
        (?<![^A-Za-z][A-Z])
        \.\s+                               # period after authors
        (?P<title>
            (?!(?:19|20)\d{2}\.)
            (?:[^.?!]|[.?!](?!\s))+?
        )
        (?:
            [.?!]\s+ .*? [,\s]\s*
          | ,\s* (?:[A-Z][a-z]+\.?\s+)?
        )
        (?P<year>(?:19|20)\d{2})
        \.(?:\s|$)
        .*$
        '''


    gen_pattern_3 = r'''
        ^(?P<authors>
            .*?,\s*and\s+.*?[A-Za-z]{2,}\.
            )
            \s+
            (?P<title>
                [^.,]+
            )
            [\.,]
            .*$
            '''
    gen_pattern_2 = r'''
            ^(?P<authors>
                (?:
                    \b[A-Z]\.                 # allowed initial
                  | (?![.]) .                # any char except period or comma
                )*
                \sand\s+(?=[A-Z])             # " and " must occur before first real delimiter
                (?:
                    \b[A-Z]\.
                  | (?![.]) .
                )*
                \b[A-Za-z]{2,}                # final author word
            )
            [\.,]\s*                          # author–title separator: period OR comma
            (?P<title>[^.,]+)                 # title has NO periods or commas
            [\.,]
            .*$
        '''
    gen_pattern_et_al = r'''
            ^
            (?P<authors>
                .*?\bet\s+al\s*\.?
            )
            \s+
            (?P<title>
                [^.,]+
            )
            [\.,]
            .*$
        '''
    gen_pattern_1 = r'''
            ^
            (?P<authors>
                (?:                             # consume chars that are NOT the boundary start
                    (?!\b[A-Za-z]{2,}[\.])     # don't step over a WORD{2,} + . or , boundary
                    .                           # consume one char
                )*
                \b[A-Za-z]{2,}                  # final word before separator: >= 2 letters
            )
            (?=[\.,])                           # next char must be . or ,
            [\.,]\s*                            # consume the punctuation
            (?P<title>[^.]+)
            .*$
        '''  

