from cmd2 import bg, fg, style, ansi
import modeldef as md
from prettytable import PrettyTable

def printterm(mcmd, msql, mp, intId, bLinks, bLocalDirectoryInfo, bLocalDirectoryInfoOnly, bTree):
    dictTypesSymbols = dict(zip(md.listLinkTypes, md.listLinkTypesSymbols))
    dictTypeColours = dict(zip(md.listElementTypes,md.listElementTypesColours))
    listSons = msql.getSonsPerId(intId)

    #########
    # links #
    #########
    if (bLinks):
        
        #getDescendants
        listDescendants = []
        msql.getDescendantsPerId(intId, listDescendants)

        #getLinks among descendants
        listLinks = []                
        for element in listDescendants:
            links = msql.getLinksPerId(element[0]) #element[0] is the id
            for link in links:
                if link not in listLinks:
                    listLinks.append(link)

        #print table header
        if (bLocalDirectoryInfo):
            t = PrettyTable(['Name', 'Source', 'Source(details)', 'Type', 'Destination(details)', 'Destination'])
        elif (bLocalDirectoryInfoOnly):
            t = PrettyTable(['Name', 'Source', 'Type', 'Destination(Local)'])
        else:
            t = PrettyTable(['Name', 'Source', 'Type', 'Destination'])
        t.align = "l"

        #print table rows (1 per link)
        for link in listLinks:
            sourceData = msql.getElementPerId(link[7]) #link[7] is the source Id
            destinationData = msql.getElementPerId(link[8]) #link[8] is the destination Id
            source_path = sourceData[7]
            destination_path = destinationData[7]               

            if (bLocalDirectoryInfo or bLocalDirectoryInfoOnly):
                # find local level
                bSourceLocalLevelFound = False
                bDestinationLocalLevelFound = False
                for element in listSons:
                    element_path = element[7]
                    if (element_path in source_path):
                        source_local = element[1]
                        bSourceLocalLevelFound = True
                    if (element_path in destination_path):
                        destination_local = element[1]
                        bDestinationLocalLevelFound = True
                                        
                # if local level found, include the row
                if (bSourceLocalLevelFound) and (bDestinationLocalLevelFound):
                    if (bLocalDirectoryInfo):
                        if (source_local != destination_local):
                            t.add_row([link[1],#link[1] is the name
                                       ansi.style(source_local, fg=dictTypeColours[sourceData[5]]),
                                       ansi.style(mp.getRelativePath(source_path), fg=dictTypeColours[sourceData[5]]),
                                       dictTypesSymbols[link[5]],
                                       ansi.style(mp.getRelativePath(destination_path), fg=dictTypeColours[destinationData[5]]),
                                       ansi.style(destination_local, fg=dictTypeColours[destinationData[5]])]) #element[7] is path, element[5] is type
                    if (bLocalDirectoryInfoOnly):
                        if (source_local != destination_local):
                            t.add_row([link[1],#link[1] is the name
                                       ansi.style(source_local, fg=dictTypeColours[sourceData[5]]),
                                       dictTypesSymbols[link[5]],
                                       ansi.style(destination_local, fg=dictTypeColours[destinationData[5]])]) #element[7] is path, element[5] is type                        
            else:
                t.add_row([link[1],#link[1] is the name
                           ansi.style(mp.getRelativePath(sourceData[7]), fg=dictTypeColours[sourceData[5]]),
                           dictTypesSymbols[link[5]],
                           ansi.style(mp.getRelativePath(destinationData[7]), fg=dictTypeColours[destinationData[5]])]) #element[7] is path, element[5] is type
        print(t)

    ############
    # elements #
    ############
    else:
        if (bTree == False):
            strLine = ""
            for element in listSons:
                listSonsOfSons = msql.getSonsPerId(element[0]) #element[0] is the id
                if listSonsOfSons: #if the element has descendants, plot a (+)
                    strLine += ansi.style('(+)' + element[1], fg=dictTypeColours[element[5]]) + "\t" #element[1] is the name, element[5] is the type
                else:
                    strLine += ansi.style(element[1], fg=dictTypeColours[element[5]]) + "\t" #element[1] is the name, element[5] is the type
            mcmd.ppaged(strLine, chop=True)
        else:
            print ("to be done")
    return;

