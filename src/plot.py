import src.definitions as md
import webbrowser
import codecs
import os

def plot(msql, mp, intId, bTree, config):
    dictTypesPlots = dict(zip(md.listElementTypes, md.listElementTypesPlot))
    element = msql.getElementPerId(intId)
    listSons = msql.getSonsPerId(intId)
    filename = element[1]
    fd = codecs.open("./" + filename + ".puml","w", encoding='utf8')

    fd.write("@startuml\n")
    fd.write("skinparam roundCorner 15\n")
    fd.write("skinparam storage {\n BackgroundColor #F7E286\n BorderColor Black\n}\n")
    fd.write("skinparam rectangle {\n BackgroundColor #C6CBD3\n BorderColor Black\n}\n")
    fd.write("skinparam actor {\n BackgroundColor #E87D6D\n BorderColor Black\n}\n")
    fd.write("skinparam node {\n BackgroundColor #FFFFFF\n BorderColor Black\n}\n")
    fd.write("skinparam ArrowColor black\n")
    fd.write("skinparam ActorBorderColor black\n")
    fd.write("skinparam defaultTextAlignment center\n")    
    
    if (bTree == False):
        for son in listSons:
            fd.write(dictTypesPlots[son[5]] + " " + son[1] + " as " + str(son[0]) + "\n")        
    if (bTree == True):
        plotTreeLeaf (fd, msql, element, dictTypesPlots)

    fd.write("@enduml\n")
    fd.close()

    # run plant uml and display
    os.system("java -jar " + os.path.relpath(config["plantUML"]["path"], os.getcwd()) + " " + filename + ".puml")
    webbrowser.open(filename + ".png")
    
    return;

def plotTreeLeaf (fd, msql, element, dictTypesPlots):
    fd.write(dictTypesPlots[element[5]] + " " + element[1] + " as " + str(element[0]) + "\n")        
    listSons = msql.getSonsPerId(element[0]) #element[0] is the id
    for son in listSons:
        plotTreeLeaf (fd, msql, son, dictTypesPlots)
        fd.write(str(element[0]) + " o-- " + str(son[0]) + "\n")
    return;



