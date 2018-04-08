#!/usr/bin/env python3
# pylint: disable=C0111,C0103,C0301

import sys
from normalise import normalise

def getLexicon(lexiconFile):
    # Reads lexicons and the position of that lexicon in invlist file from memory
    lexiconPositionMap = {}

    with open(lexiconFile, 'r') as f:
        for line in f:
            line = line.rstrip().split(" ")
            lexiconPositionMap[line[0]] = line[1]

    return lexiconPositionMap

def getDocNum(mapFile):
    # Reads docId and docNum from memory and make hash map of it
    docIDNumMap = []

    with open(mapFile, 'r') as f:
        for line in f:
            line = line.rstrip().split(" ")
            docIDNumMap.append(line[1])

    return docIDNumMap

def getTermOccurance(term, invertedListFile, lexiconPositionMap, docIDNumMap):
    # If term not found then simply exits without any output
    if term not in lexiconPositionMap:
        return

    print(term)

    offset = int(lexiconPositionMap[term])

    #opens the file in binary mode to read bytes
    f = open(invertedListFile, 'rb')

    #seeks to appropiate position of particular term in invlist file
    f.seek(offset, 0)

    #reads first number at the offset that is list length or frequency of term occured in all documents
    listLength = int.from_bytes(f.read(4), byteorder='big')

    print(listLength)

    #Loop through to get each docId in which term occured and its frequency
    while listLength > 0:
        docID = int.from_bytes(f.read(4), byteorder='big')
        print(docIDNumMap[docID], end=" ")
        print(str(int.from_bytes(f.read(4), byteorder='big')))
        listLength -= 1
    print("------------------")



# Usage: ./search.py <lexicon> <invlists> <map> <queryterm 1> [... <queryterm N>]
if __name__ == '__main__':
    try:
        termList = normalise(' '.join(sys.argv[4:]))

        # Reads docId and docNum from memory and make hash map of it
        lex = getLexicon(sys.argv[1])
        dmap = getDocNum(sys.argv[3])

        if not termList:
            print('No search query provided - exiting')

        for inputTerm in termList:
            getTermOccurance(inputTerm, sys.argv[2], lex, dmap)
    except OSError as e:
        print('{}\nProgram Exiting'.format(e))
    except IndexError:
        print('Insufficient paramaters for meaningfull response') # - Asimov, heh
