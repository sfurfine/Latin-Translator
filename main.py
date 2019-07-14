# Sophia Furfine - Final Project: Latin Translator
# To run this program, open Python 2.7 and run as normal.
# Also need to install Pattern: https://www.clips.uantwerpen.be/pattern


from collections import namedtuple

Node = namedtuple('Node', 'name pos formInfo parent children defn')

def main():
    while True:
        words = raw_input("Enter a simple Latin sentence to translate: ").split()
        tree = makeSuccessfulTree(words)
        translate(tree)
        print

def makeSuccessfulTree(words):

    pileOfLeaves = breakSentenceIntoNodes(words)
    listOfAllLeavesVariations = []
    makeLeavesVariations(pileOfLeaves, [], listOfAllLeavesVariations)
    
    for leafVariation in listOfAllLeavesVariations:
        tree = assembleTree(leafVariation)
        if tree is not None:
            return tree
        disassemble(leafVariation)

def makeLeavesVariations(pileOfLeaves, curHandfulOfLeaves, basketOfLeaves):
    if len(pileOfLeaves) == 0:
        basketOfLeaves.append(list(curHandfulOfLeaves))
        return

    for leaf in pileOfLeaves[0]:
        curHandfulOfLeaves.append(leaf)
        makeLeavesVariations(pileOfLeaves[1:], curHandfulOfLeaves, basketOfLeaves)
        curHandfulOfLeaves.pop()


# Part I

def breakSentenceIntoNodes(words):
    toReturn = []
    for word in words:
        wordInfo = lookup(word)

        nodeChoiceList = []

        skip = False
        
        for i in range(len(wordInfo)):
            if len(wordInfo[i]) < 2:
                continue

            if skip:
                skip = False
            else:
                if wordInfo[i][-1][0] != '[':
                    nodeChoiceList.append(Node(word, wordInfo[i][1], wordInfo[i],
                                           [], [], getDefn(wordInfo, i)))
                else:
                    skip = True
        toReturn.append(nodeChoiceList)

    return toReturn


def getDefn(wordInfo, i):
    for j in range(i, len(wordInfo)):
        if wordInfo[j][-1][0] == '[':
            toReturn = wordInfo[j+1][0]
            if toReturn[-1] == ',' or toReturn[-1] == ';' or toReturn[-1] == ':':
                toReturn = toReturn[:-1]
            return toReturn
    return "uh oh"

# End of Part I







# Part II

def assembleTree(allLeaves):
    print(allLeaves)

    activeNodes = list(allLeaves)

    for word in allLeaves:
        if word.pos == 'N' or word.pos == 'ADJ':
            nounAdjMergeWithMatches(word, allLeaves, activeNodes)
    # NP phrases done

    for i in range(len(allLeaves)-1):

        if allLeaves[i].pos == 'PREP':
            
            merge(allLeaves[i], allLeaves[i+1], activeNodes)
    # Prep phrases done
    

    copyOfActiveNodes = list(activeNodes)
    for word in copyOfActiveNodes:
        if word.pos == 'V':
            cur = word
            objectFull = False
            for unit in copyOfActiveNodes:
                if unit.pos == 'PREP' or (
                        unit.pos == 'N' and unit.formInfo[4] == 'ACC' and not objectFull):
                    if unit.pos == 'N':
                        objectFull = True
                    merge(cur, unit, activeNodes)
                    cur = activeNodes[-1]
            break
    #VP done
    
    if len(activeNodes) == 1:
        return(activeNodes[0])
    
    if len(activeNodes) == 2:
        merge(activeNodes[0], activeNodes[1], activeNodes)
        return(activeNodes[0])

    # only get here if bad tree
    return None


def nounAdjMergeWithMatches(word, allLeaves, activeNodes): 

    if word not in activeNodes:
        return

    for unit in activeNodes:
        if unit is not word and not (unit.pos == 'N' and word.pos == 'N'):

            if caseNumGen(word.formInfo) == caseNumGen(unit.formInfo):
                merge(word, unit, activeNodes)
                return


def caseNumGen(nounOrAdjFormInfo):
    if nounOrAdjFormInfo[1] == 'N':
        return nounOrAdjFormInfo[-3:]
    #only get here if adjective
    return nounOrAdjFormInfo[-4:-1]


def merge(word1, word2, activeNodes):

    while word1.parent != []:
        word1 = word1.parent[0]
    while word2.parent != []:
        word2 = word2.parent[0]
    
    w1Priority = mergePrioritize(word1)
    w2Priority = mergePrioritize(word2)

    # make it so WOLOG w1Priority \ge w2Priority
    if w1Priority < w2Priority:
        word1, word2 = word2, word1

    toReturn = Node(None, word1.pos, word1.formInfo, [], [word1, word2], None)

    word1.parent.append(toReturn)
    word2.parent.append(toReturn)
    activeNodes.remove(word1)
    activeNodes.remove(word2)
    activeNodes.append(toReturn)
    return toReturn

def mergePrioritize(word):
    if word.pos == 'PREP':
        return 3
    if word.pos == 'N':
        return 2
    if word.pos == 'ADJ':
        return 1
    if word.pos == 'V':
        return 4
    
    return "yelp"

def disassemble(leafVariation):
    for leaf in leafVariation:
        while leaf.parent != []:
            leaf.parent.pop()




# End of Part II






# Part III

def translate(tree):

    # first time in a given noun phrase
    if tree.pos == 'N' and tree.parent[0].pos != 'N':
        print "the",
    
    if tree.name is None:
        # then it's not a leaf
        # so then we do recursive stuff to its kids that we know exist

        child1, child2 = tree.children

        priority1 = translatePriority(child1.formInfo)
        priority2 = translatePriority(child2.formInfo)

        # so that child1 will have priority before child2
        if priority2 < priority1:
            child1, child2 = child2, child1

        translate(child1)
        translate(child2)
        return

    # only gets here if tree is a leaf

    print prettify(tree.formInfo, tree.defn),


from pattern.en import *
def prettify(wordInformation, definition):
    
    # get word in the format that pattern can understand
    # previously have removed punctuation from definition, so just have word we want

    if wordInformation[1] == 'ADJ':
        if wordInformation[-1] == 'POS':
            return definition
        if wordInformation[-1] == 'COMP':
            return comparative(definition)
        if wordInformation[-1] == 'SUPER':
            return superlative(definition)
        
    if wordInformation[1] == 'N':
        if wordInformation[-2] == 'P':
            return pluralize(definition)
        return definition

    if wordInformation[1] == 'PREP':
        return definition

    if wordInformation[1] == 'V':
        t = verbInformationNaming[wordInformation[4]]
        p = verbInformationNaming[wordInformation[-2]]
        n = verbInformationNaming[wordInformation[-1]]
        m = verbInformationNaming[wordInformation[-3]]

        return conjugate(definition, tense = t, person = p,
                         number = n, mood = m) or definition


# converts notation for verb forms from how the dictionary does it to pattern format
verbInformationNaming = {
    # tense
    'PRES' : PRESENT,
    'PERF' : PAST,
    'FUT' : FUTURE,

    # person
    '1' : 1,
    '2' : 2,
    '3' : 3,

    # number
    'S' : SG,
    'P' : PL,
    
    # mood
    'IND' : INDICATIVE,
    'IMP' : IMPERATIVE,
    'SUB' : SUBJUNCTIVE
    }

def translatePriority(wordInformation):

    if wordInformation[1] == 'ADJ' and wordInformation[4] == 'NOM':
        return 1
    if wordInformation[1] == 'N' and wordInformation[4] == 'NOM':
        return 2
    if wordInformation[1] == 'V':
        return 3
    if wordInformation[1] == 'PREP':
        return 4
    if wordInformation[1] == 'ADJ':
        return 5
    if wordInformation[1] == 'N':
        return 6
    return "ahhhh"


# End of Part III






# The part between this comment and the next comment like this I got substantial
# help, so consider the next 5 lines as "starter" code.

import urllib

def lookup(word):
    url = "http://archives.nd.edu/cgi-bin/wordz.pl?keyword=" + word
    html = str(urllib.urlopen(url).read()).split("pre")[1][1:-2].strip()
    return [line.strip().split() for line in html.splitlines()]

# End of received help.
# The rest of the code is my own work.


if __name__ == "__main__": main()
