from cmd2 import bg, fg, style, ansi
from prettytable import PrettyTable
from prettytable.prettytable import PLAIN_COLUMNS
import src.definitions as md
import src.links as ml

def printlinks(msql, mp, listElements, bGroup, bFundamental):    
    dictTypesSymbols = dict(zip(md.listLinkTypes, md.listLinkTypesSymbols))
    dictTypeColours = dict(zip(md.listElementTypes,md.listElementTypesColours))
    listLinks = ml.computeLinks(msql, listElements)
    if (bGroup):
        listLinks = ml.groupLinks(listLinks)
      
    #print table header
    t = PrettyTable(['Name', 'Source', 'Type', 'Destination'])
    t.align = "l"
    t.set_style(PLAIN_COLUMNS)
    t.header = False

    for linkinfo in listLinks:
        link = msql.getLinkPerId(linkinfo.id)

        if ((bFundamental == True) and (linkinfo.type == "fundamental") or (bFundamental == False)):
            startElement = msql.getElementPerId(linkinfo.start_element_id)
            endElement = msql.getElementPerId(linkinfo.end_element_id)

            t.add_row([ansi.style(mp.getRelativePath(startElement[md.ELEMENT_PATH]), fg=dictTypeColours[startElement[md.ELEMENT_TYPE]]),
                    dictTypesSymbols[link[md.LINK_TYPE]],
                    ansi.style(mp.getRelativePath(endElement[md.ELEMENT_PATH]), fg=dictTypeColours[endElement[md.ELEMENT_TYPE]]), 
                    linkinfo.name]) 
    
    if listLinks:
        print(t)

def printelements(msql, listElements):    
    dictTypeColours = dict(zip(md.listElementTypes,md.listElementTypesColours))
    strLine = ""
    for element in listElements:
        listDescendants = msql.getSonsPerId(element[md.ELEMENT_ID]) 
        if listDescendants: #if the element has descendants, plot a (+)
            strLine += ansi.style('(+)' + element[md.ELEMENT_NAME], fg=dictTypeColours[element[md.ELEMENT_TYPE]]) + "\t" 
        else:
            strLine += ansi.style(element[md.ELEMENT_NAME], fg=dictTypeColours[element[md.ELEMENT_TYPE]]) + "\t" 
    print(strLine)

def printTreeLeaf (msql, element, strIndent, dictTypeColours):
    listSons = msql.getSonsPerId(element[md.ELEMENT_ID]) 
    print(ansi.style(strIndent + '└── ' + element[md.ELEMENT_NAME], fg=dictTypeColours[element[md.ELEMENT_TYPE]])) 
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