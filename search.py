#!/usr/bin/env python3
# pylint: disable=C0111,C0103,C0301

import sys,argparse,time
from math import exp
from normalise import normalise
from minHeap import Heap

# HashMap to store Doc ID and its BM25 score for each query term
docScoreMap = {}

# Constants for BM25 function
AL,N,k1,b = 0,0,0,0

def calculateK(Ld):
    # Calculates K, a component of BM25 function
    return k1*((1-b)+((b*Ld)/AL))

def calculateBM25(ft, K, fdt):
    # Calculates BM25 function score
    return (exp((N-ft+0.5)/(ft+0.5)))*(((k1+1)*fdt)/(K+fdt))

def getNAndAL(docMap):
    # Iterate through each row in map file to calculate average doc length i.e AL
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
    # Reads docId, docNum and docLength from memory and make hash map of it
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

    offset = int(lexiconPositionMap[term])

    #opens the file in binary mode to read bytes
    f = open(invertedListFile, 'rb')

    #seeks to appropiate position of particular term in invlist file
    f.seek(offset, 0)

    #reads first number at the offset that is list length or frequency of term occured in all documents
    listLength = int.from_bytes(f.read(4), byteorder='big')
    ft = listLength

    #Loop through to get each docId in which term occured and its frequency
    while listLength > 0:
        docRow = docIDNumMap[int.from_bytes(f.read(4), byteorder='big')]
        fdt = int.from_bytes(f.read(4), byteorder='big')
        docId = docRow[0]

        K = calculateK(int(docRow[1]))
        score = calculateBM25(ft, K, fdt)

        if docId in docScoreMap:
            docScoreMap[docId] += score
        else:
            docScoreMap[docId] = score

        listLength -= 1


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

        # Reading appropriate files into memory
        lexicons = getLexicon(args.lexicon)
        docMap = getDocNum(args.map)
        stoplist = open_stoplist(args.stoplist)

        # Initializing constants
        N,AL = getNAndAL(docMap)
        k1 = 1.2
        b = 0.75
        numOfResult = args.numresults
        querylabel = args.querylabel

        # Normalizing query terms
        termList = normalise(' '.join(args.queryterms), punctuation=r'[^a-z0-9\ ]+', case=False, stops=stoplist)

        # Processing each query at a time
        for inputTerm in termList:
            getTermOccurance(inputTerm, args.invlists, lexicons, docMap)

        # Initializing Min Heap to keep the record of top N results
        minHeap = Heap()

        # Scaning through HashMap containing documents in which query terms occured and its score for that query
        # and storing in MinHeap to get top N results
        for key in docScoreMap:
            minHeap.add((docScoreMap[key], key))
            if len(minHeap.heap) > numOfResult:
                minHeap.del_min()

        # Displaying the content of Min Heap sorted by BM25 score in descending order
        i = 1
        for item in reversed(minHeap.heap):
            print(querylabel, item[1], i, item[0])
            i += 1

        print("Running time: %d ms" % ((time.time() - start_time) * 1000))
    except OSError as e:
        print('{}\nProgram Exiting'.format(e))
    except IndexError:
        print('Insufficient paramaters for meaningfull response') # - Asimov, heh
