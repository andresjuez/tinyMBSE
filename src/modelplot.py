import src.modeldef as md
import codecs
import subprocess
import os

def plot(mcmd, msql, mp, intId, bLinks, bLocalDirectoryInfo, bLocalDirectoryInfoOnly, bTree):
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
    fd.close()

    # run plant uml and display
    os.system("java -jar " + os.path.relpath("/drives/C/Users/aajm/Desktop/PlantUML/plantuml.jar", os.getcwd()) + " " + filename + ".puml")
    subprocess.run(["display","./" + filename + ".png" ])
    
    return;

def plotTreeLeaf (fd, msql, element, dictTypesPlots):
    fd.write(dictTypesPlots[element[5]] + " " + element[1] + " as " + str(element[0]) + "\n")        
    listSons = msql.getSonsPerId(element[0]) #element[0] is the id
    for son in listSons:
        plotTreeLeaf (fd, msql, son, dictTypesPlots)
        fd.write(str(element[0]) + " o-- " + str(son[0]) + "\n")
    return;



