#!/usr/bin/env python3
# pylint: disable=C0111,C0103,C0301,C0326,R1705,W0603

import argparse
import time
import sys
from math import log
from normalise import normalise
from minHeap import Heap

# HashMap to store Doc ID and its BM25 score for each query term
docScoreMap = {}

# Constants for BM25 function
N, k1, b = 0, 0, 0

def calculateBM25(ft, K, fdt):
    # Calculates BM25 function score
    return (log((N-ft+0.5)/(ft+0.5)))*(((k1+1)*fdt)/(K+fdt))

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
    # Reads docId, [docNum and docWeight] from storage and return a list of them
    docIDNumMap = []

    with open(mapFile, 'r') as f:
        for line in f:
            line = line.rstrip().split(" ")
            docIDNumMap.append([line[1], float(line[2])])

    return docIDNumMap

def getTermOccurance(term, invertedListFile, lexiconPositionMap, docIDNumMap, BM25):
    # If term not found then simply exits without any output
    if term not in lexiconPositionMap:
        return None

    offset = int(lexiconPositionMap[term])

    #opens the file in binary mode to read bytes
    with open(invertedListFile, 'rb') as f:
        #seeks to appropiate position of particular term in invlist file
        f.seek(offset, 0)

        # lambda to read a number in
        read = lambda: int.from_bytes(f.read(4), byteorder='big')

        #reads first number at the offset that is list length or frequency of term occured in all documents
        listLength = read()
        ft = listLength

        if not BM25:
            # Store all occurance positions for each doc if we're phrase searching
            doc_occs = {}

        #Loop through to get each docId in which term occured and its frequency
        while listLength > 0:
            docNum = read()
            docRow = docIDNumMap[docNum]
            docId = docRow[0]

            fdt = read()

            if BM25:
                K = docRow[1]
                score = float(str(round(calculateBM25(ft, K, fdt), 4)))

                if docId in docScoreMap:
                    docScoreMap[docId] += score
                else:
                    docScoreMap[docId] = score

                # Discard position data
                for _ in range(fdt):
                    read()
            else: # Assume phrase search
                locations = []
                for _ in range(fdt):
                    locations.append(read())
                doc_occs[docNum] = locations


            listLength -= 1

        if BM25:
            return None # No return required for BM25 - all results stored in docStoreMap
        else: # phrase search
            # Return dict of occurances (doc id -> [term position])
            return doc_occs



# Usage: ./search.py <ranker> <label> <#results> <lexicon> <invlists> <map> <stoplist> <queryterms*>
def main(s_args):
    try:
        parser = argparse.ArgumentParser()
        ranker = parser.add_mutually_exclusive_group(required=True)
        ranker.add_argument('-BM25', '--BM25', action='store_true', default=False,
                            help='Uses BM25 similiarity function (default)')
        ranker.add_argument('--phrase-search', action='store_true', default=False,
                            help='Shows results that match the exact phrase searched')

        parser.add_argument('-q', '--querylabel', type=int, required=True,
                            help='An integer that identiﬁes the current query')
        parser.add_argument('-n', '--numresults', type=int,
                            help='An integer number specifying the number of documents that should be returned')
        parser.add_argument('-l', '--lexicon', type=str, required=True,
                            help='A path to a file containing a list of lexicons')
        parser.add_argument('-i', '--invlists', type=str, required=True,
                            help='A path to an inverted list file')
        parser.add_argument('-m', '--map', type=str, required=True,
                            help='A path to a file containing a mapping table')
        parser.add_argument('-s', '--stoplist', type=str,
                            help='A path to a file containing a list of stopwords')
        parser.add_argument('query', help='List of query terms', nargs='+')
        args = parser.parse_args(s_args)

        # Abort if we're missing mutually inclusive parameters
        if (args.BM25 and args.numresults is None):
            parser.error('BM25 queries require a number of results to output. Specify with -n / --numresults')
        elif (args.phrase_search and args.numresults is not None):
            parser.error('Phrase queries do not require a limit on output results. Remove the -n / --numresults argument')

        # Reading appropriate files into memory
        lexicons = getLexicon(args.lexicon)
        docMap = getDocNum(args.map)
        stoplist = open_stoplist(args.stoplist)

        # Normalizing query terms (assuming probable paramaters when indexing)
        termList = normalise(' '.join(args.query), punctuation=r'[^a-z0-9\ ]+', case=True, stops=stoplist)



        # Operate differently depending on which ranking method is being used

        if args.BM25: # BM25
            main_bm25(args, termList, lexicons, docMap)
        elif args.phrase_search: # phrase search
            main_phrase(args, termList, lexicons, docMap)

    except OSError as e:
        print('{}\nProgram Exiting'.format(e))
    except IndexError:
        print('Insufficient paramaters for meaningful response') # - Asimov, heh



def main_phrase(args, terms, lexicons, docMap):
    query_label = args.querylabel

    big_list = [] # [term_num -> {doc_id: [location]}]
    chicken_dinners = [] # Winning documents (and their in-doc phrase frequency)

    for inputTerm in terms:
        oc = getTermOccurance(inputTerm, args.invlists, lexicons, docMap, BM25=False)
        big_list.append(oc)

    # Checks for having some non-empty terms to peruse
    if big_list and big_list[0] and None not in big_list:

        # Set intersection of the keys - finds only the documents that contain all terms
        matches = big_list[0].keys()
        for d in big_list:
            matches = matches & d.keys()

        for d in matches: # Calculate validity on a per-document basis
            for i in range(1, len(terms)): # Check each term (starting at the second one)
                c_locs = big_list[i][d]     # Compare the location of each term to the locations
                p_locs = big_list[i - 1][d] # of the previous term - they should be offset by 1

                new_locs = list(c_locs) # Store the location of terms which are valid
                # (that is, occur directly in front of a chain of the previous terms)

                for j in c_locs:
                    if (j - 1) not in p_locs: # Does not occur after an instance of the previous term
                        new_locs.remove(j) # Remove from the list to compare against for the next term

                big_list[i][d] = new_locs # Store the new list for the next term's comparisons

            if big_list[-1][d]: # This document is validated - store for output
                chicken_dinners.append( (d, len(big_list[-1][d])) )
    else:
        # No documents matched at all
        pass

    if chicken_dinners:
        chicken_dinners.sort(key=lambda a: a[1], reverse=True) # sort on num occurances because why not

        # Following output guidelines for the ranked retrieval section
        for doc in chicken_dinners:
            print('{} {} {}'.format(query_label, docMap[doc[0]][0], doc[1])) # Documents and num occurances
    else:
        pass

def main_bm25(args, terms, lexicons, docMap):
    # Initializing constants
    global N, k1, b
    N = len(docMap)
    k1 = 1.2
    b = 0.75


    numOfResult = args.numresults
    querylabel = args.querylabel

    # Processing each query at a time
    for inputTerm in terms:
        getTermOccurance(inputTerm, args.invlists, lexicons, docMap, BM25=True)

    # Initializing Min Heap to keep the record of top N results
    minHeap = Heap()

    # Scanning through HashMap containing documents in which query terms occured and its score for that query
    # and storing in MinHeap to get top N results
    for key in docScoreMap:
        if len(minHeap) == numOfResult:
            minHeap.push(docScoreMap[key], key, replace=True)
        else:
            minHeap.push(docScoreMap[key], key)

    finalResult = []

    while True:
        try:
            item = minHeap.next()
            finalResult.append((item, docScoreMap[item]))
        except StopIteration:
            break

    # Displaying the content of Min Heap sorted by BM25 score in descending order
    for i, item in enumerate(reversed(finalResult)):
        print(querylabel, item[0], i + 1, item[1])



if __name__ == '__main__':
    start_time = time.time()

    main(sys.argv[1:])

    print("Running time: %d ms" % ((time.time() - start_time) * 1000))
