from cmd2 import bg, fg, style, ansi
from prettytable import PrettyTable
import src.definitions as md
import src.links as ml

def printlinks(msql, mp, listElements):    
    dictTypesSymbols = dict(zip(md.listLinkTypes, md.listLinkTypesSymbols))
    dictTypeColours = dict(zip(md.listElementTypes,md.listElementTypesColours))
    listLinks = ml.computeLinks(msql, listElements)    
      
    #print table header
    t = PrettyTable(['Name', 'Source', 'Type', 'Destination'])
    t.align = "l"

    for linkinfo in listLinks:
        link = msql.getLinkPerId(linkinfo.link_id)
        startElement = msql.getElementPerId(linkinfo.start_element_id)
        endElement = msql.getElementPerId(linkinfo.end_element_id)

        t.add_row([link[1],#link[1] is the name
                ansi.style(mp.getRelativePath(startElement[7]), fg=dictTypeColours[startElement[5]]),
                dictTypesSymbols[link[5]],
                ansi.style(mp.getRelativePath(endElement[7]), fg=dictTypeColours[endElement[5]])]) #element[7] is path, element[5] is type
    print(t)

def printelements(msql, listElements):    
    dictTypeColours = dict(zip(md.listElementTypes,md.listElementTypesColours))
    strLine = ""
    for element in listElements:
        listDescendants = msql.getSonsPerId(element[0]) #element[0] is the id
        if listDescendants: #if the element has descendants, plot a (+)
            strLine += ansi.style('(+)' + element[1], fg=dictTypeColours[element[5]]) + "\t" #element[1] is the name, element[5] is the type
        else:
            strLine += ansi.style(element[1], fg=dictTypeColours[element[5]]) + "\t" #element[1] is the name, element[5] is the type
    print(strLine)

def printTreeLeaf (msql, element, strIndent, dictTypeColours):
    listSons = msql.getSonsPerId(element[0]) #element[0] is the id
    print(ansi.style(strIndent + '└── ' + element[1], fg=dictTypeColours[element[5]])) #element[1] is the name, element[5] is the type
    strIndentSons = strIndent + "    "
    for elementSon in listSons:
        printTreeLeaf (msql, elementSon, strIndentSons, dictTypeColours)
    return;

def printtree(msql, intId):
    dictTypeColours = dict(zip(md.listElementTypes,md.listElementTypesColours))
    listSons = msql.getSonsPerId(intId)
    print (".")
    strIndent = ""
    for element in listSons:
        printTreeLeaf (msql, element, strIndent, dictTypeColours)
    return;