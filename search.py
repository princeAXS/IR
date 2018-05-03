#!/usr/bin/env python3
# pylint: disable=C0111,C0103,C0301

import sys,argparse,time
from math import exp
from normalise import normalise

docScoreMap = {}
AL,N,k1,b = 0,0,0,0

def calculateK(Ld):
    return k1*((1-b)+((b*Ld)/AL))

def calculateBM25(ft, K, fdt):
    return (exp((N-ft+0.5)/(ft+0.5)))*(((k1+1)*fdt)/(K+fdt))

def getNAndAL(docMap):
    sum = 0
    for item in docMap:
        sum += int(item[1])
    return len(docMap),int(sum/len(docMap))

def open_stoplist(sfn):
    # Opens a stoplist stored on disk and returns it as a set of strings
    if sfn is None:
        # No stoplist to read - return a blank
        return set()

    with open(sfn, 'r') as sf:
        # Read all words (strip them of whitespace) and return the set
        # Set because order and identity don't matter, and there are good time gains to be had
        sl = {w.strip() for w in sf}
        return sl

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
            docIDNumMap.append([line[1],line[2]])

    return docIDNumMap

def getTermOccurance(term, invertedListFile, lexiconPositionMap, docIDNumMap):
    # If term not found then simply exits without any output
    if term not in lexiconPositionMap:
        return

    # print(term)

    offset = int(lexiconPositionMap[term])

    #opens the file in binary mode to read bytes
    f = open(invertedListFile, 'rb')

    #seeks to appropiate position of particular term in invlist file
    f.seek(offset, 0)

    #reads first number at the offset that is list length or frequency of term occured in all documents
    listLength = int.from_bytes(f.read(4), byteorder='big')
    ft = listLength

    # print(listLength)

    #Loop through to get each docId in which term occured and its frequency
    while listLength > 0:
        docRow = docIDNumMap[int.from_bytes(f.read(4), byteorder='big')]
        fdt = int.from_bytes(f.read(4), byteorder='big')
        docId = docRow[0]

        K = calculateK(int(docRow[1]))
        # print(K,ft,fdt)
        score = calculateBM25(ft, K, fdt)

        if docId in docScoreMap:
            docScoreMap[docId] += score
        else:
            docScoreMap[docId] = score

        listLength -= 1
    # print("------------------")
    # print(docScoreMap)
    # print("------------------")
    # print("------------------")


# Usage: ./search.py <lexicon> <invlists> <map> <queryterm 1> [... <queryterm N>]
if __name__ == '__main__':
    start_time = time.time()
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-BM25', '--BM25', action='store_true',
                            help='Uses BM25 similiarity function')
        parser.add_argument('-q', '--querylabel', type=int,
                            help='An integer that identiﬁes the current query')
        parser.add_argument('-n', '--numresults', type=int,
                            help='An integer number specifying the number of top-ranked documents that should be returned as an answer')
        parser.add_argument('-l', '--lexicon', type=str,
                            help='A path to a file containing a list of lexicons')
        parser.add_argument('-i', '--invlists', type=str,
                            help='A path to a Inverted list file')
        parser.add_argument('-m', '--map', type=str,
                            help='A path to a file containing a mapping table from internal document numbers to actual document identiﬁers')
        parser.add_argument('-s', '--stoplist', type=str,
                            help='A path to a file containing a list of stopwords')
        parser.add_argument('queryterms', help='List of query terms', nargs='+')
        args = parser.parse_args()

        print(args.queryterms)

        # Reads docId and docNum from memory and make hash map of it
        lexicons = getLexicon(args.lexicon)
        docMap = getDocNum(args.map)
        stoplist = open_stoplist(args.stoplist)

        N,AL = getNAndAL(docMap)

        k1 = 1.2
        b = 0.75

        termList = normalise(' '.join(args.queryterms), punctuation=r'[^a-z0-9\ ]+', case=False, stops=stoplist)

        for inputTerm in termList:
            getTermOccurance(inputTerm, args.invlists, lexicons, docMap)

        numOfResult = args.numresults
        querylabel = args.querylabel

        i = 0
        for r in sorted(docScoreMap, key=docScoreMap.get, reverse=True):
            print(querylabel, r, i, docScoreMap[r])
            i += 1

        print("Running time: %d ms" % ((time.time() - start_time) * 1000))
    except OSError as e:
        print('{}\nProgram Exiting'.format(e))
    except IndexError:
        print('Insufficient paramaters for meaningfull response') # - Asimov, heh
