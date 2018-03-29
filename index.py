#!/usr/bin/env python3
# pylint: disable=C0111,C0326,W0603
# pylint: disable=E1135,E1137
# pylint: disable=C0103,R0912

######################################
#                                    #
# s3550167 - Cary Symes              #
# Information Retrieval Assignment 1 #
# Created 2018-03-26                 #
#                                    #
######################################

import re
import argparse
from normalise import normalise

INT_SIZE = 32 # -bits in an integer when saving the inverted lists

# ===================
# Tag names for comparison/regexing

r_doc       = 'doc'
r_doc_num   = r'docno>\s*(.*?)\s*<\/docno'

r_head      = 'headline'
r_body      = 'text'

# ===================
# State enums, such that they are

 # Exclude 0 for comparison purposes (i.e. NO_DOC != False)
NO_DOC, PARSING, HEAD, TEXT = range(1, 5)

# ===================
# Working variables

doc_map     = []    # 'Map' between document ids and <DOCNO>s
last_match  = None  # global - gets bounced between indexify() and regex check funcs
lexicon     = {}

# ===================


def indexify(a_fn, stoplist, a_print, punc):
    global last_match

    current_id  = -1 # Will start at 0 due to being incremented every new document
    doc_terms = None # New dict every time we start on a new document
    state = NO_DOC   # Where in the document file we're up to (used for tracking closing tags)

    with open(a_fn, 'r') as f:
        for line in f:
            # Make the line comparible to our (lower case) regexes
            # Could use the re.ignore_case flag, but why bother?
            line = line.strip().lower()

            # ========== Closing Tags ==========
            # Assume TEXT and HEADLINE tags never intersect
            # Close of body
            if state == TEXT and check_close(r_body, line):
                state = PARSING
            # Close of headline
            elif state == HEAD and check_close(r_head, line):
                state = PARSING

            # Finished with this document
            elif state == PARSING and check_close(r_doc, line):
                # Done with this doc - can finalise frequencies
                # Store the doc id/term frequencies in the lexicon dict
                for w, ft in doc_terms.items():
                    lexicon[w].append( (current_id, ft) )

                doc_terms = None
                state = NO_DOC

            # ========== Term text ==========
            # It's a line to term-ify (term-inate, even :P)
            elif ((state == TEXT) or (state == HEAD)):
                if line.startswith('<') and line.endswith('>'):
                    # It's a markup tag - we don't want to index these
                    continue

                # Munch anything but numbers, letters, and spaces
                # We already case folded earlier - no need to do it again
                t = normalise(line, punctuation=punc, case=False, stops=stoplist)

                for w in t:
                    # Increase (or add) in-doc frequency for this term
                    if w in doc_terms:
                        doc_terms[w] += 1
                    else:
                        doc_terms[w] = 1

                    if w not in lexicon:
                        # It's a fresh term - we need to do stuff with this!
                        lexicon[w] = [] # Empty list to be populated once entire doc is scanned
                        # Print it if that flag's flagged
                        if a_print:
                            print(w)

            # ========== Opening Tags ==========
            # Start of new document
            elif state == NO_DOC and check_tag(r_doc, line):
                doc_terms = {}
                current_id += 1
                state = PARSING

            # Document UID
            elif state == PARSING and check_tag(r_doc_num, line, is_regex=True):
                # Check we don't break the id->doc_map index relationship
                assert len(doc_map) == current_id
                # Add entry to the map
                doc_map.append(last_match.group(1))

            # Both these mean start adding terms to the document terms list
            # Headline
            elif state == PARSING and check_tag(r_head, line):
                state = HEAD
            # Document body
            elif state == PARSING and check_tag(r_body, line):
                state = TEXT

"""
Checks if the string is an opening tag for the passed tag
"""
def check_tag(comparitor, line, is_regex=False):
    global last_match

    comparitor = '<' + comparitor + '>'

    if is_regex:
        # Python internally caches regex objects, so no need to re.compile()
        last_match = re.match(comparitor, line)
    else:
        # Simple string comparison
        last_match = (comparitor == line)

    return last_match

"""
Checks if the string is a closing tag for the passed regex
"""
def check_close(reg, line, is_regex=False):
    # Lazy code deduplication
    return check_tag(r'/' + reg, line, is_regex=is_regex)

"""
Opens a stoplist stored on disk and returns it as a list of strings
"""
def open_stoplist(sfn):
    if sfn is None:
        # No stoplist to read - return a blank
        return set()

    with open(sfn, 'r') as sf:
        # Read all words (strip them of whitespace) and return the set
        # Set because order and identity don't matter, and there are good time gains to be had
        sl = {w.strip() for w in sf}
        return sl

"""
Writes the 'map' file to disk
Each line has two items
1. document id
2. <DOCNO> tag contents
"""
def write_map(omap, ofn):
    with open(ofn, 'w') as of:
        for (did, dno) in enumerate(omap):
            of.write('{} {}\n'.format(did, dno))


"""
Writes the 'lexicon' and 'invlists' files to disk in paratandemllel
lexicon: each line has two items
    1. the term this line is for
    2. the position in invlists for this entry (can be navigated to using file.seek())
invlists: binary file
    1. document frequency
    2. document id
    3. in-document frequency
    4. Repeat 2-3 as per the doc freq for each term
"""
def write_lexicon_invs(lss, lfn, ifn):
    with open(lfn, 'w') as lf, open(ifn, 'wb') as vf:
        for term, refs in lss.items(): # list of tuples
            # Write the term and the current index to the lexicon
            # I believe python well give the seek position as a number of bytes from the start
            # for binary-type files. This index can be passed to file.seek()
            lf.write('{} {}\n'.format(term, vf.tell() ))

            # List containing the document-frequency followed by the document ids and in-doc freqs
            tosav = [len(refs)] + [a[i] for a in refs for i in (0, 1)]
            for n in tosav:
                # Convert to a bytes array (4 large for 32 bit integers)
                b = n.to_bytes(INT_SIZE // 8, byteorder='big')
                vf.write(b)



if __name__ == '__main__':
    # Handle arg vars
    parser = argparse.ArgumentParser()
    parser.add_argument('sourcefile', help='The source document file')
    parser.add_argument('-p', '--print', action='store_true',
                        help='Print each new term as it\'s found')
    parser.add_argument('-s', '--stoplist', type=str,
                        help='A path to a file containing a list of stopwords')
    args = parser.parse_args()



    # Actually do stuff
    indexify(args.sourcefile, open_stoplist(args.stoplist), args.print, r'[^\w\d\ ]')

    # Save the auxiliary files
    write_map(doc_map, 'map')
    write_lexicon_invs(lexicon, 'lexicon', 'invlists')
