# This module is in charge of managing links
#
# There are two type of links:
# 1. *fundamental*: this are the ones created by the user manually connecting two elements
# 2. *derived*: which are created automatically by the tool aggregating fundamental links
# For instance, in this example, the link between A->B is fundamental, while the A->C is derived
# (sometimes you can be interested in showing the first or the second)
# ___________         ___________
# |         |---------|-->|B|   |
# |         |         |         |
# |    A    |········>|    C    |
#  ----------         -----------
# There shouldn't be fundamental links from/to non final elements (i.e. elements with descendants)
#

class linkInfo():

     def __init__(self, link_id, link_name, link_type, start_element_id, end_element_id):
        self.id = link_id
        self.name = link_name
        self.type = link_type #fundamental or #derived
        self.start_element_id = start_element_id
        self.end_element_id = end_element_id


def computeLinks(msql, listElements):
    listComputedLinks = list()

    # 1. get descentants of all ellents and store them
    dictDescendants = {}
    for element in listElements:
        listElement_descendants = list()
        msql.getDescendantsPerId(element[0], listElement_descendants)
        dictDescendants[element[0]] = listElement_descendants

    # 2. for each start_element in listOfElements
    for start_element in listElements:
        # 3. for each end_element in listOfElements (there could be the case that start_element and end_element are the same)
        for end_element in listElements:

            # 4. Look for fundamental links
            listFundamentalLinks = msql.getLink(start_element[0], end_element[0]) #element[0] is the id
            for link in listFundamentalLinks:
                objLink = linkInfo(link[0], link[1], "fundamental", start_element[0], end_element[0])
                listComputedLinks.append(objLink)

            # 5.1 Look for derived links (start element pointing to end element descendants)
            for end_descendant in dictDescendants[end_element[0]]:
                listDerivedLinks = msql.getLink(start_element[0], end_descendant[0]) #element[0] is the id
                for link in listDerivedLinks:
                    objLink = linkInfo(link[0], link[1], "derived", start_element[0], end_element[0])
                    listComputedLinks.append(objLink)

            # 5.2 Look for derived links (end element pointing to start element descendants)
            for start_descendant in dictDescendants[start_element[0]]:
                listDerivedLinks = msql.getLink(start_descendant[0], end_element[0]) #element[0] is the id
                for link in listDerivedLinks:
                    objLink = linkInfo(link[0], link[1], "derived", start_element[0], end_element[0])
                    listComputedLinks.append(objLink)
            
            # 5. Look for derived links
            for start_descendant in dictDescendants[start_element[0]]:
                for end_descendant in dictDescendants[end_element[0]]:
                    listDerivedLinks = msql.getLink(start_descendant[0], end_descendant[0]) #element[0] is the id
                    for link in listDerivedLinks:
                        if (start_element[0] != end_element[0]):
                            objLink = linkInfo(link[0], link[1], "derived", start_element[0], end_element[0])
                            listComputedLinks.append(objLink)

    # 6. return listLinks
    return listComputedLinks

def groupLinks(listComputedLinks):
    listGroupedLinks = list()

    for link in listComputedLinks:
        bFound = False
        for index, grouppedLink in enumerate(listGroupedLinks):
            if ((link.start_element_id == grouppedLink.start_element_id) & (link.end_element_id == grouppedLink.end_element_id)):
                listGroupedLinks[index].name += ", " + link.name
                listGroupedLinks[index].type = "derived"
                bFound = True
        if bFound == False:
            listGroupedLinks.append(link)

    return listGroupedLinks

def extendElements (msql, listElements):
    listExtendedElements = list(listElements)

    for element in listElements:
        listLinks = msql.getAllLinksPerId(element[0])
        for link in listLinks:

            startElement = msql.getElementPerId(link[7])
            listAscendantsStartElement = list()
            msql.getAscendatsPerId(startElement[0], listAscendantsStartElement)
            if not any(item in listAscendantsStartElement for item in listElements):
                if (startElement not in listExtendedElements):
                    listExtendedElements.append(startElement)

            endElement = msql.getElementPerId(link[8])
            listAscendantsEndElement = list()
            msql.getAscendatsPerId(endElement[0], listAscendantsEndElement)
            if not any(item in listAscendantsEndElement for item in listElements):            
                if (endElement not in listExtendedElements):
                    listExtendedElements.append(endElement)

    return listExtendedElements