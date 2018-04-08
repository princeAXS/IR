import sys

def getLexicon(lexiconFile):
# Reads lexicons and the position of that lexicon in invlist file from memory
    lexiconPositionMap = {}

    with open(lexiconFile, 'r') as f:
        for line in f:
            line = line.split(" ")
            lexiconPositionMap[line[0]] = line[1]

    return lexiconPositionMap

def getDocNum(mapFile):
# Reads docId and docNum from memory and make hash map of it
    docIDNumMap = []

    with open(mapFile, 'r') as f:
        for line in f:
            line = line.split(" ")
            docIDNumMap.append(line[1])

    return docIDNumMap

def getTermOccurance(term,lexiconFile = "lexicon",invertedListFile = "invlists",mapFile = "map"):
# Reads the invlist and prints out term, its frequency, doc containing that term and its frequency within that document
    lexiconPositionMap = getLexicon(lexiconFile )

    # if term not found then simply exits with showing a message
    if term not in lexiconPositionMap:
        print("Cannot find term:", term)
        return

    print(term)

    docIDNumMap = getDocNum(mapFile)

    offset = int(lexiconPositionMap[term])

    #opens the file in binary mode to read bytes
    f = open(invertedListFile, 'rb')

    #seeks to appropiate position of particular term in invlist file
    f.seek(offset, 0)

    #reads first number at the offset that is list length or frequency of term occured in all documents
    listLength = int.from_bytes(f.read(4), byteorder='big')

    print(listLength)

    #Loop through to get each docId in which term occured and its frequency
    while listLength>0:
        docID = int.from_bytes(f.read(4), byteorder='big')
        print(docIDNumMap[docID].rstrip(), end=" ")
        print(str(int.from_bytes(f.read(4), byteorder='big')))
        listLength -= 1
    print("------------------")

if __name__ == '__main__':
    termList = sys.argv[4:]

    for term in termList:
        getTermOccurance(term,sys.argv[1],sys.argv[2],sys.argv[3])