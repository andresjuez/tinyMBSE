import src.definitions as md
import src.links as ml
import webbrowser
import codecs
import os

def initPlot(filename):
    fd = codecs.open("./" + filename + ".puml","w", encoding='utf8')
    fd.write("@startuml\n")
    fd.write("skinparam roundCorner 15\n")
    fd.write("skinparam rectangle {\n BackgroundColor #C6CBD3\n BorderColor Black\n roundCorner<<Concept>> 25\n}\n")
    fd.write("skinparam actor {\n BackgroundColor #C6CBD3\n BorderColor Black\n}\n")
    fd.write("skinparam node {\n BackgroundColor #FFFFFF\n BorderColor Black\n}\n")
    fd.write("skinparam ArrowColor black\n")
    fd.write("skinparam ActorBorderColor black\n")
    fd.write("skinparam defaultTextAlignment center\n")    
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
    listSons = msql.getSonsPerId(intId)
    filename = element[1]
    
    fd = initPlot(filename)
    plotTreeLeaf (fd, msql, element, dictTypesPlots)
    closePlot(fd)
    
    launchPlantUML(filename, config)

    return;

def plotTreeLeaf (fd, msql, element, dictTypesPlots):
    fd.write(dictTypesPlots[element[5]] + " " + element[1] + " as " + str(element[0]) + "\n")        
    listSons = msql.getSonsPerId(element[0]) #element[0] is the id
    for son in listSons:
        plotTreeLeaf (fd, msql, son, dictTypesPlots)
        fd.write(str(element[0]) + " o-- " + str(son[0]) + "\n")
    return;


def plotDFD(msql, listElements, config, bGroup, bFundamental):
    dictTypesPlots = dict(zip(md.listElementTypes, md.listElementTypesPlot))
    filename = "dfd"
    listLinks = ml.computeLinks(msql, listElements)
    if (bGroup):
        listLinks = ml.groupLinks(listLinks)
    
    fd = initPlot(filename)
    for element in listElements:
        fd.write(dictTypesPlots[element[5]] + " " + element[1] + " as " + str(element[0]) + "\n")        
    for link in listLinks:
        if ((bFundamental == True) and (link.type == "fundamental") or (bFundamental == False)):
            fd.write(str(link.start_element_id) + " --> " + str(link.end_element_id) + " : " + str(link.name) + "\n")
    closePlot(fd)
    
    launchPlantUML(filename, config)

    return;