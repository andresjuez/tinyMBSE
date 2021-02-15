import modeldef as md
import codecs

def plot(mcmd, msql, mp, intId, bLinks, bLocalDirectoryInfo, bLocalDirectoryInfoOnly, bTree):
    dictTypesPlots = dict(zip(md.listElementTypes, md.listElementTypesPlot))
    element = msql.getElementPerId(intId)
    listSons = msql.getSonsPerId(intId)
    filename = element[1]
    fd = codecs.open("./" + filename + ".puml","w", encoding='utf8')

    fd.write("@startuml\n")
    
    #########
    # links #
    #########
    if (bLinks):
        print ("TODO")

    ############
    # elements #
    ############
    else:
        if (bTree == False):
            for son in listSons:
                fd.write(dictTypesPlots[son[5]] + " " + son[1] + " as " + str(son[0]) + "\n")        
        if (bTree == True):
            plotTreeLeaf (fd, msql, element, dictTypesPlots)

    fd.write("@enduml\n")
    
    return;

def plotTreeLeaf (fd, msql, element, dictTypesPlots):
    fd.write(dictTypesPlots[element[5]] + " " + element[1] + " as " + str(element[0]) + "\n")        
    listSons = msql.getSonsPerId(element[0]) #element[0] is the id
    for son in listSons:
        plotTreeLeaf (fd, msql, son, dictTypesPlots)
        fd.write(str(element[0]) + " o-- " + str(son[0]) + "\n")
    return;



