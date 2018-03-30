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
# Regexes

r_doc       = r'doc'
r_doc_num   = r'docno>\s*(.*?)\s*<\/docno'

r_head      = r'headline'
r_body      = r'text'

r_tag       = r'[\/\w]+'

# ===================
# State enums, such that they are

 # Exclude 0 for comparison purposes (i.e. NO_DOC != False)
NO_DOC, PARSING, HEAD, TEXT = range(1, 5)

# ===================
# Working variables

#stoplist    = None  # To be fetched
doc_map     = {}    # Map between document ids and <DOCNO>s
last_match  = None  # global - gets bounced between indexify() and regex check funcs
lexicon     = {}
hexDict = {
    '0':'0000', '1':'0001', '2':'0010', '3':'0011', '4':'0100', '5':'0101',
    '6':'0110', '7':'0111', '8':'1000', '9':'1001', 'a':'1010', 'b':'1011',
    'c':'1100', 'd':'1101', 'e':'1110', 'f':'1111', 'L':''}

# ===================


def indexify(a_fn, stoplist, a_print):
    global last_match

    current_id  = -1 # Will start at 0 due to being incremented every new document
    doc_terms = None # New dict every time we start on a new document
    state = NO_DOC   # Where in the document file we're up to (used for tracking closing tags)

    with open(a_fn, 'r') as f:
        for line in f:
            # Make the line comparible to our (lower case) regexes
            # Could use the re.ignore_case flag, but why bother?
            line = line.strip().lower()

            # ========== Opening Tags ==========
            # Start of new document
            if check_tag(r_doc, line):
                doc_terms = {}
                current_id += 1
                state = PARSING

            elif state == NO_DOC:
                continue # We're outside a <DOC> tag - do nothing. This probably never occurs

            # Document UID
            elif check_tag(r_doc_num, line):
                # Add entry to the map
                doc_map[current_id] = last_match.group(1)

            # Headline
            elif check_tag(r_head, line):
                state = HEAD # Start adding terms to the document terms list
            # Document body
            elif check_tag(r_body, line):
                state = TEXT # Start adding terms to the document terms list


            # ========== Closing Tags ==========
            # Assume TEXT and HEADLINE tags never intersect
            # Close of body
            elif check_close(r_body, line):
                state = PARSING
            # Close of headline
            elif check_close(r_head, line):
                state = PARSING

            # Finished with this document
            elif check_close(r_doc, line):
                # Done with this doc - can finalise frequencies
                # Store the doc id/term frequencies in the lexicon dict
                for w, ft in doc_terms.items():
                    lexicon[w].append((current_id, ft))

                doc_terms = None
                state = NO_DOC

            # ========== Term text ==========
            # It's a line to term-ify (term-inate, even :P)
            elif (state == TEXT or state == HEAD):
                if check_tag(r_tag, line):
                    # It's a markup tag - we don't want to index these
                    continue

                # Munch anything but numbers, letters, and spaces
                # We already case folded earlier - no need to do it again
                t = normalise(line, punctuation=r'[^\w\d\ ]', case=False, stops=stoplist)
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
def dec2bin(n):
    """
    A foolishly simple look-up method of getting binary string from an integer
    This happens to be faster than all other ways!!!
    """
    # =========================================================
    # create hex of int, remove '0x'. now for each hex char,
    # look up binary string, append in list and join at the end.
    # =========================================================
    return ''.join([hexDict[hstr] for hstr in hex(n)[2:]])

def bitstring_to_bytes(s):
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])

def getVBEncoding(n):
    binary = dec2bin(n)

    final = ""

    while(len(binary) >=7):
        final += "1"+binary[-7:]
        binary = binary[0:-7]
    binary = binary.zfill(8)
    final += binary

    return bitstring_to_bytes(final)

"""
Checks if the string is an opening tag for the passed regex
"""
def check_tag(reg, line):
    global last_match
    # Python internally caches regexe objects, so no need to re.compile()
    last_match = re.match(r'<' + reg + r'>', line)
    return last_match

"""
Checks if the string is a closing tag for the passed regex
"""
def check_close(reg, line):
    # Lazy code deduplication
    return check_tag(r'/' + reg, line)

"""
Opens a stoplist stored on disk and returns it as a list of strings
"""
def open_stoplist(sfn):
    if sfn is None:
        # No stoplist to read - return a blank
        return []

    with open(sfn, 'r') as sf:
        # Read all words (strip them of whitespace) and return the list
        sl = [w.strip() for w in sf]
        return sl

"""
Writes the 'map' file to disk
Each line has two items
1. document id
2. <DOCNO> tag contents
"""
def write_map(omap, ofn):
    with open(ofn, 'w') as of:
        for (did, dno) in omap.items():
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
                b = getVBEncoding(n)
                vf.write(b)



if __name__ == '__main__':
    # Handle arg vars
    parser = argparse.ArgumentParser()
    parser.add_argument('sourcefile', help='The source document file')
    parser.add_argument('-p', '--print', action='store_true',
                        help='Print each new term as it\'s found')
    parser.add_argument('-s', '--stoplist', type=str,
                        help='A path to a file containing a list of stopwords')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Output run times')
    args = parser.parse_args()

    # Track how long it takes to index and write to disk
    v = args.verbose
    if v:
        from time import time
        t_s = time()

    # Actually do stuff
    indexify(args.sourcefile, open_stoplist(args.stoplist), args.print)

    if v:
        t_i = time()

    # Save the auxiliary files
    write_map(doc_map, 'map')
    write_lexicon_invs(lexicon, 'lexicon', 'invlists')

    if v:
        t_w = time()
        print('{}s to index\n{}s to write to disk'.format(t_i - t_s, t_w - t_s))
