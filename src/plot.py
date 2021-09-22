import src.definitions as md
import src.links as ml
import webbrowser
import codecs
import os

def initPlot(filename, bLeftToRight=False, bOrthogonal=False):
    fd = codecs.open("./" + filename + ".puml","w", encoding='utf8')
    fd.write("@startuml\n")
    fd.write("skinparam roundCorner 15\n")
    fd.write("skinparam rectangle {\n BackgroundColor #C6CBD3\n BorderColor Black\n roundCorner<<Concept>> 25\n}\n")
    fd.write("skinparam actor {\n BackgroundColor #C6CBD3\n BorderColor Black\n}\n")
    fd.write("skinparam node {\n BackgroundColor #FFFFFF\n BorderColor Black\n}\n")
    fd.write("skinparam folder {\n BackgroundColor #FFFFFF\n BorderColor Black\n}\n")
    fd.write("skinparam ArrowColor black\n")
    fd.write("skinparam ActorBorderColor black\n")
    fd.write("skinparam defaultTextAlignment center\n")
    if (bLeftToRight):
        fd.write("left to right direction\n")
    if (bOrthogonal):
        fd.write("skinparam linetype ortho\n")
    return fd

def closePlot(fd):
    fd.write("@enduml\n")
    fd.close()

def launchPlantUML(filename, config):
    # run plant uml and display
    os.system("java -jar " + os.path.relpath(config["plantUML"]["path"], os.getcwd()) + " " + filename + ".puml")
    webbrowser.open(filename + ".png")


def plotTree(msql, intId, config):
    dictTypesPlots = dict(zip(md.listElementTypes, md.listElementTypesPlot))
    element = msql.getElementPerId(intId)
    filename = "." + element[md.ELEMENT_NAME]
    
    fd = initPlot(filename)
    plotTreeLeaf (fd, msql, element, dictTypesPlots)
    closePlot(fd)
    
    launchPlantUML(filename, config)

    return;

def plotTreeLeaf (fd, msql, element, dictTypesPlots):
    fd.write(dictTypesPlots[element[md.ELEMENT_TYPE]] + " " + element[md.ELEMENT_NAME] + " as " + str(element[md.ELEMENT_ID]) + "\n")
    listSons = msql.getSonsPerId(element[md.ELEMENT_ID]) 
    for son in listSons:
        plotTreeLeaf (fd, msql, son, dictTypesPlots)
        fd.write(str(element[md.ELEMENT_ID]) + " o-- " + str(son[md.ELEMENT_ID]) + "\n")
    return;


def plotDFD(msql, listElements, config, bGroup, bFundamental):
    dictTypesPlots = dict(zip(md.listElementTypes, md.listElementTypesPlot))
    filename = ".dfd"
    listLinks = ml.computeLinks(msql, listElements)
    if (bGroup):
        listLinks = ml.groupLinks(listLinks)
    
    fd = initPlot(filename)
    for element in listElements:
        fd.write(dictTypesPlots[element[md.ELEMENT_TYPE]] + " " + element[md.ELEMENT_NAME] + " as " + str(element[md.ELEMENT_ID]) + "\n")
    for link in listLinks:
        if ((bFundamental == True) and (link.type == "fundamental") or (bFundamental == False)):
            fd.write(str(link.start_element_id) + " --> " + str(link.end_element_id) + " : " + str(link.name) + "\n")
    closePlot(fd)
    
    launchPlantUML(filename, config)

    return;

def plotRecursiveDFD(msql, listElements, config):
    dictTypesPlots = dict(zip(md.listElementTypes, md.listElementTypesPlot))
    filename = ".dfd"
    listElementsPlusDescendants = list(listElements)

    fd = initPlot(filename)
    for element in listElements:
        plotHierarchy(fd, msql, element, dictTypesPlots)
        listElement_descendants = list()
        msql.getDescendantsPerId(element[md.ELEMENT_ID], listElement_descendants)
        if (listElement_descendants):
            listElementsPlusDescendants = listElementsPlusDescendants + listElement_descendants
    
    # compute links
    listLinks = ml.computeLinks(msql, listElementsPlusDescendants)

    for link in listLinks:
        if (link.type == "fundamental"):
            fd.write(str(link.start_element_id) + " --> " + str(link.end_element_id) + " : " + str(link.name) + "\n")

    closePlot(fd)
    
    launchPlantUML(filename, config)

    return;

def plotHierarchy(fd, msql, element, dictTypesPlots):
    sons = msql.getSonsPerId(element[md.ELEMENT_ID])
    if (sons):
        fd.write(dictTypesPlots[element[md.ELEMENT_TYPE]] + " " + element[md.ELEMENT_NAME] + " as " + str(element[md.ELEMENT_ID]) + " {\n")
        for son in sons:
            plotHierarchy(fd, msql, son, dictTypesPlots)
        fd.write("}\n")
    else:
        fd.write(dictTypesPlots[element[md.ELEMENT_TYPE]] + " " + element[md.ELEMENT_NAME] + " as " + str(element[md.ELEMENT_ID]) + "\n")
    return;


