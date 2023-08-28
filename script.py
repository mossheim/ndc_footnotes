#!/bin/env python3

from parsy import regex, seq, string, alt
import re

def parsy_match(m):
    start = regex(r'\[\^\d+\]:\s*')
    dot = string(".")
    comma = string(',')
    squote = string("'")
    dquote = string("\"")
    ws = regex(r'\s*')
    star = string("*")
    optstar = star.optional()
    authors = regex(r'(( [A-Z]\. )|([a-z]\.[a-z])|[a-zA-Z\-, ])+') << dot << ws
    authors = authors.tag('authors')
    title_base = regex(r'([^\'"*]|([\'"][^., ]))+') 
    squote_title_base = regex(r'([^\']|(\'[a-z]))+')
    title1 = squote >> squote_title_base << squote
    title2 = dquote >> title_base << dquote
    title3 = star >> title_base << star
    title = alt(title1, title2, title3) << alt(dot, comma).optional() << ws
    title = title.tag('title')

    
    date_base1 = regex(r'(?:Accessed )?\d+ \w+ \d+')
    date_base2 = regex(r'\d+ \w+, \d+')
    date_base3 = regex(r'\w+ (1|2)\d\d\d')
    date_base4 = regex(r'(1|2)\d\d\d')
    date = alt(date_base1, date_base2, date_base3, date_base4) << alt(dot, comma) << ws
    date = date.tag('date')

    link1 = string("<") >> regex(r'[^>]+') << string(">") << dot << ws
    link2 = regex("https://[^ ]*") << ws
    link3 = regex(r"\[[^\]]*\]\([^)]*\)") << dot << ws
    link = alt(link1, link2, link3).tag('link')

    other_field = regex(r'([^,.]|(\.[A-Z]))+[,.] +')
    starred_other_field = regex(r'\*[^,.]+[,.]\* +')
    more_fields = alt(date, link, other_field, starred_other_field).many()

    start = start.tag('start')
    more_fields = more_fields.tag('other')
    basic_citation = seq(start, authors.optional(('authors', None)), title, more_fields).map(dict)
    basic_note = seq(start, regex(r'[a-zA-Z\'",* .\-]+')).map(tuple)
    try:
        cite = basic_citation.parse(m)
        ct = cite['start']

        link = [l for l in cite['other'] if l[0] == 'link']
        if link:
            ct += '[' + cite['title'] + '](' + link[0][1] + ')'
        else:
            ct += '*' + cite['title'] + '*'
        author_line = cite['authors'] + ', ' if cite['authors'] else ''
        author_line += ''.join([l for l in cite['other'] if type(l) is str]).strip()

        ct += '  \n' + author_line[:-1] + '.' if len(author_line) > 0 else ''

        date = [l for l in cite['other'] if l[0] == 'date']
        if date:
            ct += '  \n' + date[0][1] + '.'

        print(ct)
    except Exception as e:
        raise e

def process_footnotes(text):
    first_footnote = text.find('[^1]:')
    pretext = text[:first_footnote]
    posttext = text[first_footnote:]

    # process inline footnotes
    pretext = re.sub(r'\[\^(\d+)\]([^:]|$)', r'[](#fn\1)[^\1]\2', pretext)
    pretext = re.sub('([^\n])\n[ \t]*([^\n])', '\\1 \\2', pretext)
    pretext = re.sub(r'#([^{\n]*).*', '##\\1', pretext)
    print(pretext)

    # ending footnotes
    matches = re.findall(r'\[\^\d+\]:(?:.*\n)(?:[ \t].*\n)*', posttext)
    errs = []
    for i, m in enumerate(matches):
        m = re.sub(r'  +', ' ', m.replace('\\\n', '\n').replace('\n', ' '))

        try:
            parsy_match(m)
        except Exception as e:
            print(m)
            #print('*** ERROR: ' + str(e))
            #print('')
            errs.append(i + 1)
        print('')

    #print(errs)
    #print(len(errs), '/', len(matches))

if __name__ == "__main__":
    import sys
    process_footnotes(open(sys.argv[1]).read())
