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

def getCurrentNumber(f):
    # Reads bytes until reaches to end byte
    byte = f.read(1)

    #convert byte to binary, chopping off 0b from the beginning
    curBin = bin(byte[0])[2:]

    #makes it 8 bits binary
    curBin = curBin.zfill(8)

    #Chops off the first bit which is flag of continuation
    integratedBin = curBin[1:]

    #loops through the bytes until get to the end byte
    while curBin[0] == "1":
        byte = f.read(1)
        curBin = bin(byte[0])[2:]
        curBin = curBin.zfill(8)
        integratedBin = curBin[1:] + "" + integratedBin

    #returns actual binary string of number
    return integratedBin

def getTermOccurance(term, invertedListFile, lexiconPositionMap, docIDNumMap):
    # if term not found then simply exits without any output
    if term not in lexiconPositionMap:
        return

    print(term)


    offset = int(lexiconPositionMap[term])

    # opens the file in binary mode to read bytes
    f = open(invertedListFile, 'rb')

    # seeks to appropiate position of particular term in invlist file
    f.seek(offset, 0)

    # reads first number at the offset that is list length or frequency of term occured in all documents
    listLength = int(getCurrentNumber(f), 2)

    print(listLength)

    gap_sum = 0

    # Loop through to get each docId in which term occured and its frequency
    while listLength > 0:
        #reads docId and termCount alternatively
        docID = int(getCurrentNumber(f), 2)
        termCount = int(getCurrentNumber(f), 2)

        # docID, gap_sum = (gap_sum + docID), docID
        docID += gap_sum
        gap_sum = docID

        print(docIDNumMap[docID], end=" ")
        print(termCount)
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
