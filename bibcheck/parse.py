class patterns:
    acm_pattern_3 = r'''
            ^(?P<authors>
                .*?                  # anything up to the first ' and ' or ', and '
                (?:[,]and )         # space-or-comma, then 'and', then space
                [^,]+?                  # rest of the authors (can include periods for initials)
                \b[A-Za-z]{2,}       # final word before separator: >= 2 letters (e.g. 'Bienz')
            )
            [\.]\s*                 # punctuation right after title
            (?P<year>(19|20)\d{2})\b
            [\.]\s*                 # consume the punctuation right after authors
            (?P<title>
                [^.]+?               # title: any chars except '.' (no periods allowed in title)
            )
            .*$
        '''
    acm_pattern_2 = r'''
            ^(?P<authors>
                .*?                  # anything up to the first ' and ' or ', and '
                (?:and )         # space-or-comma, then 'and', then space
                [^,]+?                  # rest of the authors (can include periods for initials)
                \b[A-Za-z]{2,}       # final word before separator: >= 2 letters (e.g. 'Bienz')
            )
            [\.]\s*                 # punctuation right after title
            (?P<year>(19|20)\d{2})\b
            [\.]\s*                 # consume the punctuation right after authors
            (?P<title>
                [^.]+?               # title: any chars except '.' (no periods allowed in title)
            )
            .*$
        '''
    acm_pattern_1 = r'''
            ^
            (?P<authors>
                (?:                             # consume chars that are NOT the boundary start
                    (?!\b[A-Za-z]{2,}[\.,])     # don't step over a WORD{2,} + . or , boundary
                    .                           # consume one char
                )*
                \b[A-Za-z]{2,}                  # final word before separator: >= 2 letters
            )
            (?=[\.])                           # next char must be . or ,
            [\.,]\s*
            (?P<year>(19|20)\d{2})\b
            [\.]\s*                            # consume the punctuation
            (?P<title>\s*
                [^.]+?                          # title (no periods allowed)
            )
            .*$
        '''  

    siam_pattern_3 = r'''
            ^(?P<authors>
                .*?                  # anything up to the first ' and ' or ', and '
                (?:[,]and )         # space-or-comma, then 'and', then space
                [^,]+?                  # rest of the authors (can include periods for initials)
                \b[A-Za-z]{2,}       # final word before separator: >= 2 letters (e.g. 'Bienz')
            )
            [\.]\s*                 # consume the punctuation right after authors
            (?P<title>
                [^.]+?               # title: any chars except '.' (no periods allowed in title)
            )
            [\.]\s*                 # punctuation right after title
            (?P<year>(19|20)\d{2})\b
            .*$
        '''
    siam_pattern_2 = r'''
            ^(?P<authors>
                .*?                  # anything up to the first ' and ' or ', and '
                (?:and )         # space-or-comma, then 'and', then space
                [^,]+?                  # rest of the authors (can include periods for initials)
                \b[A-Za-z]{2,}       # final word before separator: >= 2 letters (e.g. 'Bienz')
            )
            [\.]\s*                 # consume the punctuation right after authors
            (?P<title>
                [^.]+?               # title: any chars except '.' (no periods allowed in title)
            )
            [\.]\s*                 # punctuation right after title
            (?P<year>(19|20)\d{2})\b
            .*$
        '''
    siam_pattern_1 = r'''
            ^
            (?P<authors>
                (?:                             # consume chars that are NOT the boundary start
                    (?!\b[A-Za-z]{2,}[\.,])     # don't step over a WORD{2,} + . or , boundary
                    .                           # consume one char
                )*
                \b[A-Za-z]{2,}                  # final word before separator: >= 2 letters
            )
            (?=[\.,])                           # next char must be . or ,
            [\.]\s*                            # consume the punctuation
            (?P<title>\s*
                [^.]+?                          # title (no periods allowed)
            )
            [\.]\s*
            (?P<year>(19|20)\d{2})\b
            .*$
        '''  

    ieee_pattern_3 = r'^(?P<authors>.*?)["“”](?P<title>.+?)["“”]'
    ieee_pattern_2 = r'^(?P<authors>.*?)["“”](?P<title>.+?)["“”]'
    ieee_pattern_1 = r'^(?P<authors>.*?)["“”](?P<title>.+?)["“”]'


    gen_pattern_3 = r'''
            ^(?P<authors>
                .*?                  # anything up to the first ' and ' or ', and '
                (?:[,]and )         # space-or-comma, then 'and', then space
                [^,]+?                  # rest of the authors (can include periods for initials)
                \b[A-Za-z]{2,}       # final word before separator: >= 2 letters (e.g. 'Bienz')
            )
            [\.,]\s*                 # consume the punctuation right after authors
            (?P<title>
                [^.]+?               # title: any chars except '.' (no periods allowed in title)
            )
            .*$
        '''
    gen_pattern_2 = r'''
            ^(?P<authors>
                .*?                  # anything up to the first ' and ' or ', and '
                (?:and )         # space-or-comma, then 'and', then space
                [^,]+?                  # rest of the authors (can include periods for initials)
                \b[A-Za-z]{2,}       # final word before separator: >= 2 letters (e.g. 'Bienz')
            )
            [\.,]\s*                 # consume the punctuation right after authors
            (?P<title>
                [^.]+?               # title: any chars except '.' (no periods allowed in title)
            )
            .*$
        '''
    gen_pattern1 = r'''
            ^
            (?P<authors>
                (?:                             # consume chars that are NOT the boundary start
                    (?!\b[A-Za-z]{2,}[\.,])     # don't step over a WORD{2,} + . or , boundary
                    .                           # consume one char
                )*
                \b[A-Za-z]{2,}                  # final word before separator: >= 2 letters
            )
            (?=[\.,])                           # next char must be . or ,
            [\.,]\s*                            # consume the punctuation
            (?P<title>\s*
                [^.]+?                          # title (no periods allowed)
            )
            .*$
        '''  

