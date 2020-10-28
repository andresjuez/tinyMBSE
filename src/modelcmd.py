import argparse
import cmd2
from cmd2 import bg, fg, style, ansi
from typing import List
import modelsql
import modelpath
import logging

class modelcmd(cmd2.Cmd):
    """ This manages the model in the SQL database """
    # command categories
    strMODEL_COMMANDS = "Model Commands"
    strELEMENT_COMMANDS = "Element Commands"

    def __init__(self):

        # call parent
        super().__init__(multiline_commands=['echo'], persistent_history_file='.climb_history.dat', use_ipython=True)

        # intro
        self.intro = style('Welcome to Command Line Interface Modelling Blocks (climb)!', bold=True)

        # model sql management
        self.modelsql = modelsql.modelsql()

        # model path management
        self.modelpath = modelpath.modelpath()

        # Allow access to your application in py and ipy via self
        self.self_in_py = True

        # set prompt
        self._set_prompt()
       
    def _set_prompt(self):
        """Set prompt so it displays the current working directory."""
        if (self.modelsql.bConnected == False):
            self.prompt = ansi.style(f'Disconnected/> ', fg='bright_red')
            return
        self.prompt = ansi.style("[" + self.modelsql.strUser + "@" + self.modelsql.strHost + " " + \
                                 str(self.modelsql.intCWI) + "] " + self.modelpath.getCWD() + "/> ")

    def postcmd(self, stop: bool, line: str) -> bool:
        """Hook method executed just after a command dispatch is finished.

        :param stop: if True, the command has indicated the application should exit
        :param line: the command line text for this command
        :return: if this is True, the application will exit after this command and the postloop() will run
        """
        """Override this so prompt always displays cwd."""
        self._set_prompt()
        return stop

    # ANCILLIARY get model list 
    def get_db_list(self) -> List[str]:
        """list of available db options"""
        return self.modelsql.listDB()

    def mcmd_can_be_executed(self):
        if self.modelsql.bConnected:
            return True
        logging.info("Please connect first")
        return False

    def cmd_can_be_executed(self):
        if self.modelsql.bConnected:
            if self.modelsql.bSelected:
                return True
            else:
                logging.info("Please Select Model first")
        else:
            logging.info("Please connect first")
        return False

    # CMD: conect #
    parser = argparse.ArgumentParser(description='connect to DB', add_help=False)
    parser.add_argument('-h', '--host', required=True, help="host to connect to database")
    parser.add_argument('-u','--user', required=True, help="username to connect to database")
    parser.add_argument('-p','--password', required=True, help="password for username")
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strMODEL_COMMANDS)
    def do_connect(self, args):
        """Connects to mysql server""" 
        self.modelsql.connect(args.host, args.user, args.password)

    # CMD: mls #
    @cmd2.with_category(strMODEL_COMMANDS)
    def do_mls(self, args):
        """List of models""" 
        if self.mcmd_can_be_executed():            
            self.ppaged("\n".join(self.get_db_list()), chop=True)

    # CMD: msel #
    parser = argparse.ArgumentParser(description='select model to work with', add_help=False)
    parser.add_argument('model', nargs=1, help="model name", choices_method=get_db_list)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strMODEL_COMMANDS)
    def do_msel(self, args):
        if self.mcmd_can_be_executed():
            bSelected = self.modelsql.useDB(args.model[0])
            if (bSelected):
                # manage paths
                self.modelpath.cd(self.modelpath.CLIMB_PATH)
                self.modelpath.removeFolder(args.model[0])
                self.modelpath.initFolders(args.model[0], 1, self.modelsql)
                self.modelpath.cd(args.model[0])
                # manage DB
                self.modelsql.intCWI = 1
        return

    # CMD: mnew #
    parser = argparse.ArgumentParser(description='create model', add_help=False)
    parser.add_argument('model', nargs=1, help="name of the model to be created", choices_method=get_db_list)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strMODEL_COMMANDS)
    def do_mnew(self, args):
        if self.mcmd_can_be_executed():
            bCreated = self.modelsql.createDB(args.model[0])
            if (bCreated):
                # manage paths
                self.modelpath.cd(self.modelpath.CLIMB_PATH)
                self.modelpath.newFolder(args.model[0])
                self.modelpath.cd(args.model[0])
                # manage DB
                self.modelsql.intCWI = 0
                self.modelsql.insertElement(args.model[0], 'folder', self.modelpath.getCWD())
                self.modelsql.selectCWIperPath(self.modelpath.getCWD())

    # CMD: mdel #
    parser = argparse.ArgumentParser(description='delete model', add_help=False)
    parser.add_argument('model', nargs=1, help="name of the model to be deleted", choices_method=get_db_list)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strMODEL_COMMANDS)
    def do_mdel(self, args):
        if self.mcmd_can_be_executed():
            # manage Paths
            self.modelpath.removeFolder(self.modelpath.CLIMB_PATH + "/" + args.model[0])
            if (args.model[0] == self.modelsql.strSelectedDB):
                self.modelpath.cd(self.modelpath.CLIMB_PATH)
            # manage DB
            self.modelsql.dropDB(args.model[0])
        
    # CMD: insert #
    def insert_options(self) -> List[str]:
        """insert options"""
        return [item[2] for item in self.modelsql.getSonsPerId(self.modelsql.intCWI)] 

    parser = argparse.ArgumentParser(description='insert element')
    parser.add_argument('type', help="type of element to be created", choices=modelsql.listElementTypes)
    parser.add_argument('name', help="element name", choices_method=insert_options)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_insert(self, args):
        """Creates insert element""" 
        if self.cmd_can_be_executed():
            # manage Paths
            self.modelpath.newFolder(args.name)
            # manage DB
            self.modelsql.insertElement(args.name, args.type, self.modelpath.getCWD()+"/"+args.name)
            return;

    # CMD: ls #
    parser = argparse.ArgumentParser(description='list elements and links')
    parser.add_argument('-l', '--links', required=False, default=False, action='store_true', help="host to connect to database")
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_ls(self, args):
        """list elements""" 
        if self.cmd_can_be_executed():
            listSons = self.modelsql.getSonsPerId(self.modelsql.intCWI)
            if (args.links): 
                for id, parentId, name, type in listSons:
                    listLinks = self.modelsql.getLinksPerId(id)
                    for source, destination in listLinks:
                        print (str(source) + " -> " + str(destination))
            else:
                self.ppaged(" ".join([i[2] for i in listSons]), chop=True)
            return;

    # CMD: cd #
    @cmd2.with_argument_list
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_cd(self, args: List[str]):
        """Change working directory""" 
        if self.cmd_can_be_executed():
            strBasename = self.modelpath.cd(args[0])
            self.modelsql.selectCWIperPath(self.modelpath.getCWD())
            self.ppaged(args[0], chop=True)
            return;

    complete_cd = cmd2.Cmd.path_complete

    # CMD: ln #
    parser = argparse.ArgumentParser(description='link to elements')
    parser.add_argument('origin', help="origin", completer_method=cmd2.Cmd.path_complete)
    parser.add_argument('destination', help="destination", completer_method=cmd2.Cmd.path_complete)
    parser.add_argument('-t', '--type', help="type of element to be created", choices=modelsql.listLinkTypes)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_ln(self, args):
        """Creates a link between two elements""" 
        if self.cmd_can_be_executed():
            type = 'flow'
            if args.type:
                type = args.type
            self.modelsql.insertLink(self.modelpath.getAbsPath(args.origin), self.modelpath.getAbsPath(args.destination), type) 
            return;

# del - [NAME]
#  --help, deletes an element and all its sons, all the links where this element appears
#  --f, force the deletion without asking
#   OS for path_complete: remove a folder in the ancilliary directory tree, son of CWD

# msel - [NAME]
#  --help, Select dabatabase/model
#  reads the DB and creates the folder structure
 
# link [element_source] [element_destination]
#  --help, links two elements
#  --type, flow, realization, aggregation, etc
#  --parent indicate previous link, useful for sequence diagrams
 
# convey [linkname] [element]
#  --help, joins an element to a link 

    

# import datetime as dt
# import uuid
# import logging
       

# # define class design data
# class classItem: 
#     """ This is a design item """

#     def __init__(self, strRow, strLevel, strId, strName, strType, strInputs="", strOutputs="", strRealization="", strDescription="", strUuid=""):
#         self.siRow = int(strRow)
#         self.siLevel = int(float(strLevel))
#         self.strId = strId 
#         if (strUuid == ""):
#             self.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, strId)).replace("-","_")
#         else:
#             self.uuid = strUuid

#         self.strParentId = ""
#         self.strName = strName
#         self.strIdPlusName = "["+strId+"] " + strName
#         if strName == strId:
#             self.strIdPlusName = strName
#         self.bEnd = True
#         self.strType = strType
#         self.setInputs = set()
#         if (strInputs != "nan"): 
#             self.setInputs = set(strInputs.strip().split("\n"))
#         self.setOutputs = set()
#         if (strOutputs != "nan"): 
#             self.setOutputs = set(strOutputs.strip().split("\n"))
#         self.setRealization = ""
#         if (strRealization != "nan"): 
#             self.setRealization = set(strRealization.strip().split("\n"))
#         self.setDescendantId = set()
#         self.strDescription = ""
#         if (strDescription != "nan"): 
#             self.strDescription = strDescription
#         self.setPortsId = set()

#     def setParentId(self, strId):
#         self.strParentId = strId

#     def addDesdendant(self, strDescendant, strType):
#         if (strType == "Port"):
#             self.setPortsId.add(strDescendant)
#         else:
#             self.setDescendantId.add(strDescendant)
#         self.bEnd = False

#     def __str__(self):
#         print "siRow: " + str(self.siRow)
#         print "siLevel: " + str(self.siLevel)
#         print "strId: " + self.strId
#         print "strName: " + self.strName
#         print "bEnd: " + str(self.bEnd)
#         print "strType: " + self.strType
#         print "setInputs:",
#         print self.setInputs
#         print "setOutputs:",
#         print self.setOutputs
#         print "setRealization:",
#         print self.setRealization
#         print "setDescendentId:",
#         print self.setDescendantId
#         print "setPortsId:",
#         print self.setPortsId
#         print "strParentId: " + self.strParentId
#         print "uuid: " + self.uuid
#         print "strDescription: " + self.strDescription
#         return ""
    
# # define Association
# class classAssociation:
#     """ This is a link """

#     def __init__(self, strType, strSourceId, strTargetId, strUuid="", strSourceUuid="", strTargetUuid=""):
#         self.strId = strType+strSourceId+strTargetId
#         self.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.strId)).replace("-","_")
#         if (strUuid != ""):
#             self.uuid = strUuid
#             self.strId = strUuid

#         self.strSourceId = strSourceId
#         self.strSourceUuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, strSourceId)).replace("-","_")
#         if (strSourceUuid != ""): 
#             self.strSourceUuid = strSourceUuid

#         self.strTargetId = strTargetId
#         self.strTargetUuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, strTargetId)).replace("-","_")
#         if (strTargetUuid != ""): 
#             self.strTargetUuid = strTargetUuid

#         self.strType = strType #Aggregation, InformationFlow, Realisation
#         self.setDataflowsConveyed = set()
#         self.setUuidDataflowsConveyed = set()

#     def __str__(self):
#         print "strId: " + str(self.strId)
#         print "strSourceId: " + str(self.strSourceId)
#         print "strTargetId: " + str(self.strTargetId)
#         print "strType: " + str(self.strType)
#         print "uuid: " + self.uuid
#         print "setDataflowsConveyed: ",
#         for f in self.setDataflowsConveyed:
#             print f,
#         print
#         print "setUuidDataflowsConveyed: ",
#         for f in self.setUuidDataflowsConveyed:
#             print f,
#         print
#         return ""

# # define functional analysis data
# class classDiagram:
#     """ This is the diagram data """

#     def __init__(self, strType, strId, strName):
#         #metainfo
#         self.strType = strType
#         self.strId = strId
#         self.strName = strName
#         self.strIdPlusName = "["+strId+"] " + strName
#         self.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, strId)).replace("-","_")

#         self.strCentralId = ""
#         self.setSourcesId = set()
#         self.setTargetsId = set()
#         self.setBothSourceAndTargetIds = set()
#         self.setShownAssociationsId = set()
#         self.setHiddenAssociationsId = set()


# # define functional analysis data
# class classModel:
#     """ This is the complete data """

#     def __init__(self, strName):
#         #metainfo
#         self.strName = strName
#         self.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, strName)).replace("-","_")
#         self.strDate = str(dt.datetime.now())
#         self.listPkg = ["Items", "Dataflows", "Diagrams"]
#         self.dictUuidPkg = {}
#         for strPkg in self.listPkg:
#             self.dictUuidPkg[strPkg] = str(uuid.uuid5(uuid.NAMESPACE_DNS, strName+strPkg)).replace("-","_")

#         #info
#         self.dictDesignItem = {}
#         self.dictDataflowItem = {}
#         self.dictAssociation = {}
#         self.dictDfdDiagram = {}
#         self.dictTreeDiagram = {}
#         self.siDeepestLevel = 0

#     def addDesignItem(self, classItem):
#         self.dictDesignItem[classItem.strId] = classItem
#         if (classItem.siLevel > self.siDeepestLevel):
#             self.siDeepestLevel = classItem.siLevel

#     def getAllDescentants(self, strId, setAllDescendants):
#         setAllDescendants.add(strId)
#         for strDescId in self.dictDesignItem[strId].setDescendantId:
#             self.getAllDescentants(strDescId, setAllDescendants)

#     def getAllAncestors(self, strId, setAllAncestors):
#         setAllAncestors.add(strId)
#         if self.dictDesignItem[strId].siLevel > 0:
#             self.getAllAncestors(self.dictDesignItem[strId].strParentId, setAllAncestors)
    
#     def aggregateInfo(self):
#         ''' this function aggreages input and output data from lower to uper levels '''        

#         #from siDeepestLevel backwards to 0
#         for siLevel in range(self.siDeepestLevel,-1,-1): 

#             #for each function in that level
#             for strId, myDesignItem in self.dictDesignItem.items(): 
#                 # if the function has descendants
#                 if (myDesignItem.siLevel == siLevel) and (len(myDesignItem.setDescendantId)>0):
#                     #init
#                     setDescInputs = set()
#                     setDescOutputs = set()
#                     setDescReqs = set()
                    
#                     # for each descendant aggregate inputs and outpus
#                     for strDescId in myDesignItem.setDescendantId:
#                         myDesc = self.dictDesignItem[strDescId]
#                         setDescInputs = setDescInputs.union(myDesc.setInputs)
#                         setDescOutputs = setDescOutputs.union(myDesc.setOutputs)
#                         setDescReqs = setDescReqs.union(myDesc.setRealization)
                        
#                     # copy aggregated inputs and outputs to function
#                     myDesignItem.setRealization = setDescReqs.copy()
#                     myDesignItem.setInputs = setDescInputs.copy()
#                     myDesignItem.setOutputs = setDescOutputs.copy()

#             #for each function in that level
#             for strId, myDesignItem in self.dictDesignItem.items(): 
#                 # if the function has descendants
#                 if (myDesignItem.siLevel == siLevel) and (len(myDesignItem.setDescendantId)>0):
#                     #init
#                     setDescInputs = set()
#                     setDescOutputs = set()
#                     setDescReqs = set()
                    
#                     # for each descendant aggregate inputs and outpus
#                     for strDescId in myDesignItem.setDescendantId:
#                         myDesc = self.dictDesignItem[strDescId]
#                         setDescInputs = setDescInputs.union(myDesc.setInputs)
#                         setDescOutputs = setDescOutputs.union(myDesc.setOutputs)
#                         setDescReqs = setDescReqs.union(myDesc.setRealization)

#                     #clean internal inputs and outputs
#                     setItemAndDesc = set()
#                     self.getAllDescentants(strId, setItemAndDesc)
#                     setRestOfInputs = set()
#                     setRestOfOutputs = set()
#                     for strIdAux, myDesignItemAux in self.dictDesignItem.items():
#                         if strIdAux not in setItemAndDesc:
#                             setRestOfInputs = setRestOfInputs.union(myDesignItemAux.setInputs)
#                             setRestOfOutputs = setRestOfOutputs.union(myDesignItemAux.setOutputs)
#                     for dataflow in setDescInputs:
#                         if (dataflow in setDescOutputs) and (dataflow not in setRestOfOutputs):
#                             myDesignItem.setInputs.remove(dataflow)
#                     for dataflow in setDescOutputs:
#                         if (dataflow in setDescInputs) and (dataflow not in setRestOfInputs):
#                             myDesignItem.setOutputs.remove(dataflow)

#     def generateDataflowDict(self):
#         # run through functions
#         setDataflows = set()
#         for strId, myDesignItem in self.dictDesignItem.items(): 
#             setDataflows = setDataflows.union(myDesignItem.setInputs).union(myDesignItem.setOutputs)

#         for strDataflow in setDataflows:
#             strRow = "0"
#             strLevel = "0"
#             strId = strDataflow
#             strName = strDataflow
#             strType = "Class"
#             myDataflow = classItem(strRow, strLevel, strId, strName, strType)
#             self.dictDataflowItem[strId] = myDataflow

#     def addAssociation(self, strId, strType, strSourceId, strTargetId, strDataflowId=""):
#         if strId not in self.dictAssociation:
#             self.dictAssociation[strId] = classAssociation(strType, strSourceId, strTargetId)
#             if (strDataflowId):
#                 self.dictAssociation[strId].setDataflowsConveyed.add(strDataflowId)
#                 self.dictAssociation[strId].setUuidDataflowsConveyed.add(self.dictDataflowItem[strDataflowId].uuid)
#         else:
#             if (strDataflowId):
#                 self.dictAssociation[strId].setDataflowsConveyed.add(strDataflowId)
#                 self.dictAssociation[strId].setUuidDataflowsConveyed.add(self.dictDataflowItem[strDataflowId].uuid)
    
#     def addInformationFlowSets(self, setA, setB, strOrigId, strDestId):
#         for strDataflowId in setA:
#             if strDataflowId in setB:
#                 self.addAssociation("InformationFlow"+strOrigId + strDestId, "InformationFlow", strOrigId, strDestId, strDataflowId)

#     def generateRealizations(self):
#         # Realizations
#         for strId, myDesignItem in self.dictDesignItem.items():
#             for strReq in myDesignItem.setRealization:
#                 self.addAssociation("Realisation"+strId+strReq, "Realisation", strId, strReq)

#     def generateAggregations(self):
#         # Aggregations
#         for strId, myDesignItem in self.dictDesignItem.items(): 
#             for strDesc in myDesignItem.setDescendantId:
#                 myDesc = self.dictDesignItem[strDesc]
#                 # ports are special cases not to declare this kind of association
#                 if "Port" not in myDesc.strType:
#                     self.addAssociation("Aggregation"+myDesc.strId+myDesignItem.strId, "Aggregation", myDesc.strId, myDesignItem.strId)

#     def generateAssociations(self):
#         # Associations
#         for strId, myDesignItem in self.dictDesignItem.items():
#             for strInput in myDesignItem.setInputs:
#                 for strIdAux, myDesignItemAux in self.dictDesignItem.items():
#                     if strInput in myDesignItemAux.setOutputs:
#                         self.addAssociation("Association"+strId+strIdAux, "Association", strId, strIdAux)

#     def generateInclusions(self):
#         # Inclusions
#         for strId, myDesignItem in self.dictDesignItem.items(): 
#             for strDesc in myDesignItem.setDescendantId:
#                 myDesc = self.dictDesignItem[strDesc]
#                 # ports are special cases not to declare this kind of association
#                 if "Port" not in myDesc.strType:
#                     self.addAssociation("UseCase"+myDesignItem.strId+myDesc.strId, "UseCase", myDesignItem.strId, myDesc.strId)

#     def generateInformationFlows(self):
#         # Information flows
#         setLevel0ItemsId = set()
#         for strId, myDesignItem in self.dictDesignItem.items(): 

#             if (myDesignItem.siLevel == 0):
#                 setLevel0ItemsId.add(strId)

#             for strDescId in myDesignItem.setDescendantId:
#                 myDesc = self.dictDesignItem[strDescId]
#                 # intpus from parent to descendant
#                 self.addInformationFlowSets(myDesignItem.setInputs, myDesc.setInputs, strId, strDescId)
#                 # output from descentant to parent
#                 self.addInformationFlowSets(myDesignItem.setOutputs, myDesc.setOutputs, strDescId, strId)
#                 # input and output from brothers
#                 for strDescAuxId in myDesignItem.setDescendantId:
#                     myDescAux = self.dictDesignItem[strDescAuxId]
#                     # intpus comming from brothers
#                     self.addInformationFlowSets(myDesc.setInputs, myDescAux.setOutputs, strDescAuxId, strDescId)
#                     # outputs going to brothers
#                     self.addInformationFlowSets(myDesc.setOutputs, myDescAux.setInputs, strDescId, strDescAuxId)

#         # Information flows for level 0 items
#         for strId in setLevel0ItemsId:
#             myDesignItem = self.dictDesignItem[strId]
#             for strAuxId in setLevel0ItemsId:
#                 myDesignItemAux = self.dictDesignItem[strAuxId]
#                 # intpus comming from brothers
#                 self.addInformationFlowSets(myDesignItem.setInputs, myDesignItemAux.setOutputs, strAuxId, strId)
#                 # outputs going to brothers
#                 self.addInformationFlowSets(myDesignItem.setOutputs, myDesignItemAux.setInputs, strId, strAuxId)

#     def generateInformationFlows_option(self):
#         # Information flows
#         for strId, myItem in self.dictDesignItem.items(): 
#             setAllDescendants = set()
#             setAllAncestors = set()
#             self.getAllDescentants(strId, setAllDescendants)
#             setAllDescendants.remove(strId)
#             self.getAllAncestors(strId, setAllAncestors)
#             setAllAncestors.remove(strId)
#             for strIdAux, myItemAux in self.dictDesignItem.items(): 
#                 if strIdAux not in (setAllDescendants or setAllAncestors):
#                     self.addInformationFlowSets(myItemAux.setOutputs, myItem.setInputs, strIdAux, strId)
#                     self.addInformationFlowSets(myItem.setOutputs, myItemAux.setInputs, strId, strIdAux)
#                 if strIdAux in setAllDescendants:
#                     self.addInformationFlowSets(myItem.setInputs, myItemAux.setInputs, strId, strIdAux)
#                     self.addInformationFlowSets(myItemAux.setOutputs, myItem.setOutputs, strIdAux, strId)

#     def generateInformationFlowsOnlyPorts(self):
#         # Information flows
#         setLevel0ItemsId = set()
#         for strId, myDesignItem in self.dictDesignItem.items(): 

#             if (myDesignItem.siLevel == 0):
#                 setLevel0ItemsId.add(strId)

#             for strPortId in myDesignItem.setPortsId:
#                 myPort = self.dictDesignItem[strPortId]

#                 for strDescId in myDesignItem.setDescendantId:
#                     myDesc = self.dictDesignItem[strDescId]
                    
#                     for strPortDescId in myDesc.setPortsId:
#                         myPortDesc = self.dictDesignItem[strPortDescId]

#                         # from parent to descendant
#                         self.addInformationFlowSets(myPort.setInputs, myPortDesc.setInputs, strPortId, strPortDescId)
#                         # from descendant to parent
#                         self.addInformationFlowSets(myPort.setOutputs, myPortDesc.setOutputs, strPortDescId, strPortId)
                        
#                         # input and output from brothers
#                         for strDescAuxId in myDesignItem.setDescendantId:
#                             myDescAux = self.dictDesignItem[strDescAuxId]

#                             for strPortDescAuxId in myDescAux.setPortsId:
#                                 myPortDescAux = self.dictDesignItem[strPortDescAuxId]
#                                 # intpus comming from brothers
#                                 self.addInformationFlowSets(myPortDesc.setInputs, myPortDescAux.setOutputs, strPortDescAuxId, strPortDescId)
#                                 # outputs going to brothers
#                                 self.addInformationFlowSets(myPortDesc.setOutputs, myPortDescAux.setInputs, strPortDescId, strPortDescAuxId)
                                
#         # Information flows for level 0 items
#         for strId in setLevel0ItemsId:
#             myDesignItem = self.dictDesignItem[strId]

#             for strPortId in myDesignItem.setPortsId:
#                 myPort = self.dictDesignItem[strPortId]
            
#                 for strAuxId in setLevel0ItemsId:
#                     myDesignItemAux = self.dictDesignItem[strAuxId]

#                     for strPortAuxId in myDesignItemAux.setPortsId:
#                         myPortAux = self.dictDesignItem[strPortAuxId]
                        
#                         # intpus comming from brothers
#                         self.addInformationFlowSets(myPort.setInputs, myPortAux.setOutputs, strPortAuxId, strPortId)
#                         # outputs going to brothers
#                         self.addInformationFlowSets(myPort.setOutputs, myPortAux.setInputs, strPortId, strPortAuxId)

#     def compactInformationFlows(self, intMaxSize):
#         for strAssociationId, myAssociation in self.dictAssociation.items(): 
#             if len(myAssociation.setDataflowsConveyed) > intMaxSize:
#                 # Create New Dataflow
#                 strRow = "0"
#                 strLevel = "0"
#                 strId = myAssociation.strSourceId + ":" + myAssociation.strTargetId
#                 strName = myAssociation.strSourceId + ":" + myAssociation.strTargetId
#                 strType = "Class"
#                 myDataflow = classItem(strRow, strLevel, strId, strName, strType)
#                 self.dictDataflowItem[strId] = myDataflow
#                 # set Association
#                 for strDataFlowId in myAssociation.setDataflowsConveyed:
#                     self.addAssociation("Aggregation"+strDataFlowId+strId, "Aggregation", strDataFlowId, strId)
#                 # replace data items conveyed
#                 self.dictAssociation[strAssociationId].setDataflowsConveyed = set()
#                 self.dictAssociation[strAssociationId].setDataflowsConveyed.add(myDataflow.strId)
#                 self.dictAssociation[strAssociationId].setUuidDataflowsConveyed = set()
#                 self.dictAssociation[strAssociationId].setUuidDataflowsConveyed.add(myDataflow.uuid)
            
#     def detectOrphanFlows(self):
#         logger = logging.getLogger()
#         for strDataflowId, myDataflowItem in self.dictDataflowItem.items(): 
#             setDataflowInput = set()
#             setDataflowOutput = set()
#             for strId, myDesignItem in self.dictDesignItem.items(): 
#                 if strDataflowId in myDesignItem.setInputs: 
#                     setDataflowInput.add(strId)
#                 if strDataflowId in myDesignItem.setOutputs: 
#                     setDataflowOutput.add(strId)
#             if (len(setDataflowInput) == 0) or (len(setDataflowOutput) == 0):
#                 logging.error(" Orphan flow detected: " + strDataflowId)

#     def generateDfdDiagrams(self):
#         for strId, myItem in self.dictDesignItem.items():
#             if myItem.strType != "Port":
#                 setSourceIdTmp = set()
#                 setNonCentralId = set()
#                 self.dictDfdDiagram[strId] = classDiagram(myItem.strType, myItem.strId + " DFD", myItem.strName)
#                 self.dictDfdDiagram[strId].strCentralId = strId
#                 for strAssociationId, myAssociation in self.dictAssociation.items():
#                     if  (myAssociation.strType == "InformationFlow"):
#                         if (myAssociation.strTargetId == strId):
#                             if (myAssociation.strSourceId not in myItem.setDescendantId):
#                                 setSourceIdTmp.add(myAssociation.strSourceId)
#                                 setNonCentralId.add(myAssociation.strSourceId)
#                                 self.dictDfdDiagram[strId].setSourcesId.add(myAssociation.strSourceId)
#                                 self.dictDfdDiagram[strId].setShownAssociationsId.add(strAssociationId)
#                         if (myAssociation.strSourceId == strId):
#                             if (myAssociation.strTargetId not in myItem.setDescendantId):
#                                 setNonCentralId.add(myAssociation.strTargetId)
#                                 self.dictDfdDiagram[strId].setTargetsId.add(myAssociation.strTargetId)
#                                 self.dictDfdDiagram[strId].setShownAssociationsId.add(strAssociationId)
#                 self.dictDfdDiagram[strId].setBothSourceAndTargetIds = self.dictDfdDiagram[strId].setSourcesId.intersection(self.dictDfdDiagram[strId].setTargetsId)
#                 self.dictDfdDiagram[strId].setSourcesId = setSourceIdTmp.difference(self.dictDfdDiagram[strId].setBothSourceAndTargetIds)

#                 # hide links
#                 for strAssociationId, myAssociation in self.dictAssociation.items():
#                     if (myAssociation.strSourceId in setNonCentralId) and (myAssociation.strTargetId in setNonCentralId):
#                         self.dictDfdDiagram[strId].setHiddenAssociationsId.add(strAssociationId)

#     def generateDfdDiagrams_option(self):
#         for strId, myItem in self.dictDesignItem.items():
#             if myItem.strType != "Port":

#                 self.dictDfdDiagram[strId] = classDiagram(myItem.strType, myItem.strId + " DFD", myItem.strName)
#                 self.dictDfdDiagram[strId].strCentralId = strId

#                 #Ancestors
#                 setMyAncestors = set()
#                 self.getAllAncestors(strId, setMyAncestors)
#                 setMyAncestors.remove(strId)

#                 #Descendants
#                 setMyDescendants = set()
#                 self.getAllDescentants(strId, setMyDescendants)
#                 setMyDescendants.remove(strId)

#                 # identify sources
#                 setSourceIdTmp = set()
#                 for strInput in myItem.setInputs:
#                     for strIdAux, myItemAux in self.dictDesignItem.items():
#                         if strInput in myItemAux.setOutputs and strIdAux not in setMyAncestors.union(setMyDescendants):
#                             setSourceIdTmp.add(strIdAux)
#                 for strSourceId in setSourceIdTmp:
#                     setAncestors = set()
#                     self.getAllAncestors(strSourceId, setAncestors)
#                     setAncestors.remove(strSourceId)
#                     if not setAncestors.intersection(setSourceIdTmp):
#                         self.dictDfdDiagram[strId].setSourcesId.add(strSourceId)

#                 # identify target
#                 setTargetIdTmp = set()
#                 for strOutput in myItem.setOutputs:
#                     for strIdAux, myItemAux in self.dictDesignItem.items():
#                         if strOutput in myItemAux.setInputs and strIdAux not in setMyAncestors.union(setMyDescendants):
#                             setTargetIdTmp.add(strIdAux)
#                 for strTargetId in setTargetIdTmp:
#                     setAncestors = set()
#                     self.getAllAncestors(strTargetId, setAncestors)
#                     setAncestors.remove(strTargetId)
#                     if not setAncestors.intersection(setTargetIdTmp):
#                         self.dictDfdDiagram[strId].setTargetsId.add(strTargetId)

#                 # show associations
#                 for strAssociationId, myAssociation in self.dictAssociation.items():
#                     if (myAssociation.strSourceId == strId) and (myAssociation.strTargetId in self.dictDfdDiagram[strId].setTargetsId):
#                         self.dictDfdDiagram[strId].setShownAssociationsId.add(strAssociationId)
#                     if (myAssociation.strTargetId == strId) and (myAssociation.strSourceId in self.dictDfdDiagram[strId].setSourcesId):
#                         self.dictDfdDiagram[strId].setShownAssociationsId.add(strAssociationId)

#                 # check those that are simultaneouly sources and Targets
#                 self.dictDfdDiagram[strId].setBothSourceAndTargetIds = self.dictDfdDiagram[strId].setSourcesId.intersection(self.dictDfdDiagram[strId].setTargetsId).copy()
#                 self.dictDfdDiagram[strId].setSourcesId = self.dictDfdDiagram[strId].setSourcesId.difference(self.dictDfdDiagram[strId].setBothSourceAndTargetIds).copy()
#                 self.dictDfdDiagram[strId].setTargetsId = self.dictDfdDiagram[strId].setTargetsId.difference(self.dictDfdDiagram[strId].setBothSourceAndTargetIds).copy()
#                 setNonCentralIds = self.dictDfdDiagram[strId].setBothSourceAndTargetIds.union(self.dictDfdDiagram[strId].setSourcesId.union(self.dictDfdDiagram[strId].setTargetsId))

#                 # hide links
#                 for strAssociationId, myAssociation in self.dictAssociation.items():
#                     if (myAssociation.strSourceId in setNonCentralIds) and (myAssociation.strTargetId in setNonCentralIds):
#                         self.dictDfdDiagram[strId].setHiddenAssociationsId.add(strAssociationId)

#     def generateTreeDiagrams(self):
#         for strId, myItem in self.dictDesignItem.items():
#             if myItem.bEnd == False:
#                 self.dictTreeDiagram[strId] = classDiagram(myItem.strType, myItem.strId + " Tree", myItem.strName)
#                 self.dictTreeDiagram[strId].strCentralId = strId
#                 self.dictTreeDiagram[strId].setTargetsId = myItem.setDescendantId.copy()
#                 # show links
#                 for strAssociationId, myAssociation in self.dictAssociation.items():
#                     if (myAssociation.strType == "Aggregation"):
#                         if (myAssociation.strTargetId == self.dictTreeDiagram[strId].strCentralId) and (myAssociation.strSourceId in self.dictTreeDiagram[strId].setTargetsId):
#                             self.dictTreeDiagram[strId].setShownAssociationsId.add(strAssociationId)
#                 # hide links
#                 for strAssociationId, myAssociation in self.dictAssociation.items():
#                     if (myAssociation.strType == "InformationFlow"):
#                         if (myAssociation.strSourceId == self.dictTreeDiagram[strId].strCentralId) and (myAssociation.strTargetId in self.dictTreeDiagram[strId].setTargetsId):
#                             self.dictTreeDiagram[strId].setHiddenAssociationsId.add(strAssociationId)
#                         if ((myAssociation.strSourceId in self.dictTreeDiagram[strId].setTargetsId) and myAssociation.strTargetId == self.dictTreeDiagram[strId].strCentralId):
#                             self.dictTreeDiagram[strId].setHiddenAssociationsId.add(strAssociationId)
#                         if (myAssociation.strSourceId in self.dictTreeDiagram[strId].setTargetsId) and (myAssociation.strTargetId in self.dictTreeDiagram[strId].setTargetsId):
#                             self.dictTreeDiagram[strId].setHiddenAssociationsId.add(strAssociationId)

#         # composite Dataflows
#         for strId, myItem in self.dictDataflowItem.items():
#             if myItem.bEnd == False:
#                 self.dictTreeDiagram[strId] = classDiagram(myItem.strType, myItem.strId + " Tree", myItem.strName)
#                 self.dictTreeDiagram[strId].strCentralId = strId
#                 self.dictTreeDiagram[strId].setTargetsId = myItem.setDescendantId.copy()
#                 # show links
#                 for strAssociationId, myAssociation in self.dictAssociation.items():
#                     if (myAssociation.strType == "Aggregation"):
#                         if (myAssociation.strTargetId == self.dictTreeDiagram[strId].strCentralId) and (myAssociation.strSourceId in self.dictTreeDiagram[strId].setTargetsId):
#                             self.dictTreeDiagram[strId].setShownAssociationsId.add(strAssociationId)


#     def row2csv(self, fd, myItem):
#         fd.write(str(myItem.siLevel) + ";")
#         fd.write(myItem.strName + ";")
#         fd.write(myItem.strId + ";")
#         fd.write("\"\";") #Responsible
#         if (myItem.bEnd == True):
#             fd.write("\"" +"\n".join(sorted(list(myItem.setInputs))) + "\";")
#             fd.write("\"" +"\n".join(sorted(list(myItem.setOutputs))) + "\";")
#         else:
#             fd.write("\"\";")
#             fd.write("\"\";")         
#         fd.write("\"" + myItem.strDescription + "\";")
#         if (myItem.bEnd == True):
#             fd.write("\"" +"\n".join(sorted(list(myItem.setRealization))) + "\";")
#         else:
#             fd.write("\"\";")
#         fd.write("\n")
#         for strDescId in sorted(list(myItem.setDescendantId)):
#             self.row2csv(fd, self.dictDesignItem[strDescId])

#     def model2csv(self, fd):
#         # fd.write(header
#         fd.write("Level;Item;Id;Responsible;Input Data;Output Data;Description;Realization;\n")
#         for strId, myItem in self.dictDesignItem.items():
#             if myItem.siLevel == 0:
#                 self.row2csv(fd, myItem)
        
#     def importUuid(self, classModel):
#         logger = logging.getLogger()
        
#         for strId, myDesignItem in self.dictDesignItem.items():
#             if strId in classModel.dictDesignItem:
#                 myDesignItem.uuid = classModel.dictDesignItem[strId].uuid
#                 logging.info(" uuid updated for: " + myDesignItem.strIdPlusName)
        
#         setAssociationsToDelete = set()
#         for strAssociationId, myAssociation in self.dictAssociation.items():
#             if myAssociation.strSourceId in classModel.dictDesignItem:
#                 myAssociation.strSourceUuid = classModel.dictDesignItem[myAssociation.strSourceId].uuid
#             if myAssociation.strTargetId in classModel.dictDesignItem:
#                 myAssociation.strTargetUuid = classModel.dictDesignItem[myAssociation.strTargetId].uuid
#             if (myAssociation.strTargetId not in classModel.dictDesignItem) and (myAssociation.strType == "Realisation"):
#                 logging.error(" Realisation not found in XMI: " + myAssociation.strTargetId)
#                 setAssociationsToDelete.add(strAssociationId)
#         for strAssociationId in setAssociationsToDelete:
#             if strAssociationId in self.dictAssociation.items():
#                 del self.dictAssociation[strAssociationId]
           
