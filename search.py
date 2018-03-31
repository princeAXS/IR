import sys
from normalise import normalise

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
    while curBin[0] is "1":
        byte = f.read(1)
        curBin = bin(byte[0])[2:]
        curBin = curBin.zfill(8)
        integratedBin = curBin[1:] + "" + integratedBin

    #returns actual binary string of number
    return integratedBin

def getTermOccurance(term, lexiconFile="lexicon", invertedListFile="invlists", mapFile="map"):
# Reads docId and docNum from memory and make hash map of it
    lexiconPositionMap = getLexicon(lexiconFile)

    # if term not found then simply exits with showing a message
    if term not in lexiconPositionMap:
        print("Cannot find term:", term)
        return

    print(term)

    docIDNumMap = getDocNum(mapFile)

    offset = int(lexiconPositionMap[term])

    # opens the file in binary mode to read bytes
    f = open(invertedListFile, 'rb')

    #seeks to appropiate position of particular term in invlist file
    f.seek(offset, 0)

    #reads first number at the offset that is list length or frequency of term occured in all documents
    listLength = int(getCurrentNumber(f), 2)

    print(listLength)

    #Loop through to get each docId in which term occured and its frequency
    while listLength > 0:
        #reads docId and termCount alternatively
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