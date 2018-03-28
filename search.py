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

    listLength = int.from_bytes(f.read(4), byteorder='big')

    print(listLength)

    while listLength > 0:
        docID = int.from_bytes(f.read(4), byteorder='big')
        print(docIDNumMap[docID].rstrip(), end=" ")
        print(str(int.from_bytes(f.read(4), byteorder='big')))
        listLength -= 1
    print("------------------")


if __name__ == '__main__':
    termList = sys.argv[4:]


    for term in termList:
        getTermOccurance(term,sys.argv[1],sys.argv[2],sys.argv[3])



