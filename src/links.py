import src.definitions as md

# This module is in charge of managing links
class linkInfo():

     def __init__(self, link_id, link_name, link_type, start_element_id, end_element_id):
        self.id = link_id
        self.name = link_name
        self.type = link_type #fundamental or #derived
        self.start_element_id = start_element_id
        self.end_element_id = end_element_id


def computeLinks(msql, listElements):
    '''
    Given a list of elements, it computes the links among them.
    There are two type of links:
    1. *fundamental*: this are the ones created by the user manually connecting two elements
    2. *derived*: which are created automatically by the tool aggregating fundamental links
    For instance, in the example below, where A is B's parent and D is C's parent, 
    the link between B->C is "fundamental", while the A->D is derived
    ___________         ___________
    |   |B|---|---------|-->|C|   |
    |         |         |         |
    |    A    |········>|    D    |
    ----------          -----------
    There shouldn't be fundamental links from/to non final elements (i.e. elements with descendants)
    '''
    listComputedLinks = list()

    # 1. get descentants for each of the ellents given as input
    dictDescendants = {}
    for element in listElements:
        listElement_descendants = list()
        msql.getDescendantsPerId(element[md.ELEMENT_ID], listElement_descendants)
        dictDescendants[element[md.ELEMENT_ID]] = listElement_descendants

    # 2. for each start_element in listOfElements
    for start_element in listElements:
        # 3. for each end_element in listOfElements (there could be the case that start_element and end_element are the same)
        for end_element in listElements:

            # 3.1 Look for fundamental links
            listFundamentalLinks = msql.getLink(start_element[md.ELEMENT_ID], end_element[md.ELEMENT_ID])
            for link in listFundamentalLinks:
                objLink = linkInfo(link[md.LINK_ID], link[md.LINK_NAME], "fundamental", start_element[md.ELEMENT_ID], end_element[md.ELEMENT_ID])
                listComputedLinks.append(objLink)

            # 3.2 Look for derived links (start element pointing to end element descendants)
            for end_descendant in dictDescendants[end_element[md.ELEMENT_ID]]:
                listDerivedLinks = msql.getLink(start_element[md.ELEMENT_ID], end_descendant[md.ELEMENT_ID]) 
                for link in listDerivedLinks:
                    objLink = linkInfo(link[md.LINK_ID], link[md.LINK_NAME], "derived", start_element[md.ELEMENT_ID], end_element[md.ELEMENT_ID])
                    listComputedLinks.append(objLink)

            # 3.3 Look for derived links (end element pointing to start element descendants)
            for start_descendant in dictDescendants[start_element[md.ELEMENT_ID]]:
                listDerivedLinks = msql.getLink(start_descendant[md.ELEMENT_ID], end_element[md.ELEMENT_ID]) #element[0] is the id
                for link in listDerivedLinks:
                    objLink = linkInfo(link[md.LINK_ID], link[md.LINK_NAME], "derived", start_element[md.ELEMENT_ID], end_element[md.ELEMENT_ID])
                    listComputedLinks.append(objLink)
            
            # 3.4 Look for derived links
            for start_descendant in dictDescendants[start_element[md.ELEMENT_ID]]:
                for end_descendant in dictDescendants[end_element[md.ELEMENT_ID]]:
                    listDerivedLinks = msql.getLink(start_descendant[md.ELEMENT_ID], end_descendant[md.ELEMENT_ID]) #element[0] is the id
                    for link in listDerivedLinks:
                        if (start_element[md.ELEMENT_ID] != end_element[md.ELEMENT_ID]):
                            objLink = linkInfo(link[md.LINK_ID], link[md.LINK_NAME], "derived", start_element[md.ELEMENT_ID], end_element[md.ELEMENT_ID])
                            listComputedLinks.append(objLink)

    # 4. return listLinks
    return listComputedLinks

def groupLinks(listComputedLinks):
    ''' 
    This function group the identified links. This means that if there are two links 
    that start and end in the same starting and end element these will be combined into
    a single "derived" link.
    '''
    listGroupedLinks = list() 

    #1. for each link provided at input
    for link in listComputedLinks:
        bFound = False
        
        #2. check if that link is already in the list of grouped links
        for index, grouppedLink in enumerate(listGroupedLinks):
            #2.1 if it is in the grouped list, add it up
            if ((link.start_element_id == grouppedLink.start_element_id) & (link.end_element_id == grouppedLink.end_element_id)):
                listGroupedLinks[index].name += ", " + link.name
                listGroupedLinks[index].type = "derived"
                bFound = True
        
        # 3. if it is not already included in the list of links, added it.
        if bFound == False:
            listGroupedLinks.append(link)

    #4. return grouped links
    return listGroupedLinks

def extendElements (msql, listElements):
    '''
    Given a list of elements, it extend that list with additional elements to which they have links
    |A|-->|B|-->|C|
    If A and B are given as input in the list of elements, the returned list will include A, B and C.

    There is one thing to be taken into account: if the ascendant of a given element is already 
    included in the input list of elements, it will not be added to the extended list, as otherwise
    the link will be duplicated. For instance:
    ___________         ___________
    |   |B|---|---------|-->|C|   |
    |         |         |         |
    |    A    |········>|    D    |
    ----------          -----------
    If D is already included in the list, but C is not, C will not be included in the extende list 
    (or otherwise the link will appear twice)

    '''
    # 0. Copy listElements in list extended elements
    listExtendedElements = list(listElements)

    # 1. For each element given as input.
    for element in listElements:
        listLinks = msql.getAllLinksPerId(element[md.ELEMENT_ID])

        #2. For each link of that given element.
        for link in listLinks:

            startElement = msql.getElementPerId(link[md.LINK_SOURCE_ID])
            listAscendantsStartElement = list()
            msql.getAscendatsPerId(startElement[md.ELEMENT_ID], listAscendantsStartElement)
            if not any(item in listAscendantsStartElement for item in listElements):
                if (startElement not in listExtendedElements):
                    listExtendedElements.append(startElement)

            endElement = msql.getElementPerId(link[md.LINK_DESTINATION_ID])
            listAscendantsEndElement = list()
            msql.getAscendatsPerId(endElement[md.ELEMENT_ID], listAscendantsEndElement)
            if not any(item in listAscendantsEndElement for item in listElements):            
                if (endElement not in listExtendedElements):
                    listExtendedElements.append(endElement)

    return listExtendedElements