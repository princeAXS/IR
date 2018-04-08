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
hexDict = {
    '0':'0000', '1':'0001', '2':'0010', '3':'0011', '4':'0100', '5':'0101',
    '6':'0110', '7':'0111', '8':'1000', '9':'1001', 'a':'1010', 'b':'1011',
    'c':'1100', 'd':'1101', 'e':'1110', 'f':'1111', 'L':''}

# ===================


def indexify(a_fn, stoplist, a_print, punc):
    global last_match

    current_id  = -1 # Will start at 0 due to being incremented every new document
    doc_terms = None # New dict every time we start on a new document
    state = NO_DOC   # Where in the document file we're up to (used for tracking closing tags)
                     # Also cuts back on string comparisons

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
                    # Append a tuple of the document id and the in-document term
                    # frequency in the lexicon entry for this term
                    lexicon[w].append( (current_id, ft) )

                # Reset, ready for next doc
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
                # Create new terms map, increment document id and set state
                doc_terms = {}
                current_id += 1
                state = PARSING

            # Document UID
            elif state == PARSING and check_tag(r_doc_num, line, is_regex=True):
                # Check we don't break the id->doc_map index relationship
                # Unnecessary really, there's no way for these to get out of sync hopefully
                # assert len(doc_map) == current_id

                # Add entry to the map (the key is the item's index)
                doc_map.append(last_match.group(1))

            # Both these mean start adding terms to the document terms list
            # Headline
            elif state == PARSING and check_tag(r_head, line):
                state = HEAD
            # Document body
            elif state == PARSING and check_tag(r_body, line):
                state = TEXT

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

    # Edge case of document id #0
    if not v:
        b.append(0x00)

    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])

def getVBEncoding(n):
    binary = dec2bin(n)

    final = ""

    while len(binary) >= 7:
        final += "1" + binary[-7:]
        binary = binary[0:-7]
    binary = binary.zfill(8)
    final += binary

    return bitstring_to_bytes(final)

"""
Checks if the string (@line) is an opening tag for the passed tag name (@comparitor)
"""
def check_tag(comparitor, line, is_regex=False):
    global last_match

    # Add tag braces
    comparitor = '<' + comparitor + '>'

    if is_regex:
        # Python internally caches regex objects, so no need to re.compile()
        last_match = re.match(comparitor, line)
    else:
        # Simple string comparison - much faster than regexes
        last_match = (comparitor == line)

    # Return the match object/match results - will eval to True if there's a match
    return last_match

"""
Checks if the string is a closing tag for the passed regex
"""
def check_close(reg, line, is_regex=False):
    # Lazy code deduplication
    return check_tag(r'/' + reg, line, is_regex)

"""
Opens a stoplist stored on disk and returns it as a set of strings
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
invlists: binary file - each number takes 4 bytes
     - For each term
    1. document frequency
    2. document id
    3. in-document frequency
    4. Repeat 2-3 as per the doc freq
"""
def write_lexicon_invs(lss, lfn, ifn):
    with open(lfn, 'w') as lf, open(ifn, 'wb') as vf:
        for term, refs in lss.items(): # dict of list of tuples

            # Write the term and the current index to the lexicon
            # Python will tell() the seek position as a number of bytes from the start
            # for binary-type files. This index can be passed to file.seek()
            lf.write('{} {}\n'.format(term, vf.tell() ))

            # List containing the document-frequency followed by the document ids and in-doc freqs
            tosav = [len(refs)] + [a[i] for a in refs for i in (0, 1)]
            for n in tosav:
                # Get the encoded bytes to output
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
    args = parser.parse_args()



    # Gracefully catch errors on file access/write
    try:
        # Actually do stuff
        indexify(args.sourcefile, open_stoplist(args.stoplist), args.print, r'[^a-z0-9\ ]+')

        # Save the auxiliary files
        write_map(doc_map, 'map')
        write_lexicon_invs(lexicon, 'lexicon', 'invlists')
    except OSError as e:
        print('{}\nProgram Exiting'.format(e))
