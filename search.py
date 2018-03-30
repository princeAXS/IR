import sys
from normalise import normalise

def getLexicon(lexiconFile):

    lexiconPositionMap = {}

    with open(lexiconFile, 'r') as f:
        for line in f:
            line = line.split(" ")
            lexiconPositionMap[line[0]] = line[1]

    return lexiconPositionMap

def getDocNum(mapFile):

    docIDNumMap = []

    with open(mapFile, 'r') as f:
        for line in f:
            line = line.split(" ")
            docIDNumMap.append(line[1])

    return docIDNumMap


def getCurrentNumber(f):
    byte = f.read(1)
    curBin = bin(byte[0])[2:]
    curBin = curBin.zfill(8)
    integratedBin = curBin[1:]

    while curBin[0] is "1":
        byte = f.read(1)
        curBin = bin(byte[0])[2:]
        curBin = curBin.zfill(8)
        integratedBin = curBin[1:] + "" + integratedBin

    return integratedBin

def getTermOccurance(term, lexiconFile="lexicon", invertedListFile="invlists", mapFile="map"):
    lexiconPositionMap = getLexicon(lexiconFile)

    if term not in lexiconPositionMap:
        print("Cannot find term:", term)
        return

    print(term)

    docIDNumMap = getDocNum(mapFile)

    offset = int(lexiconPositionMap[term])

    f = open(invertedListFile, 'rb')

    f.seek(offset, 0)

    listLength = int(getCurrentNumber(f), 2)

    print(listLength)

    invList = []

    while listLength > 0:
        docID = int(getCurrentNumber(f), 2)
        termCount = int(getCurrentNumber(f), 2)

        print(docIDNumMap[docID].rstrip(), end=" ")
        print(termCount)
        listLength -= 1
    print("------------------")


if __name__ == '__main__':
    termList = sys.argv[4:]


    for term in termList:
        getTermOccurance(term,sys.argv[1],sys.argv[2],sys.argv[3])



