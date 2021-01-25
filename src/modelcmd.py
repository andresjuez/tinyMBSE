import argparse
import cmd2
from cmd2 import bg, fg, style, ansi
from typing import List
import modelsql as msql
import modelpath as mp
import modeldef as md
import logging

class modelcmd(cmd2.Cmd):
    """ This manages the model in the SQL database """
    # command categories
    strMODEL_COMMANDS = "Model Commands"
    strELEMENT_COMMANDS = "Element Commands"

    def __init__(self):

        # call parent
        super().__init__(multiline_commands=['echo'], persistent_history_file='.tinyMBSE_history.dat', use_ipython=True)

        # intro
        self.intro = style('Welcome to (tiny)MBSE! model using the command line interface', bold=True)

        # model sql management
        self.msql = msql.modelsql()

        # model path management
        self.mp = mp.modelpath()

        # Allow access to your application in py and ipy via self
        self.self_in_py = True

        # set prompt
        self._set_prompt()
       
    def _set_prompt(self):
        """Set prompt so it displays the current working directory."""
        if (self.msql.bConnected == False):
            self.prompt = ansi.style(f'Disconnected/> ', fg='bright_red')
            return
        self.prompt = ansi.style("[" + self.msql.strUser + "@" + self.msql.strHost + " " + \
                                 str(self.msql.intCWI) + "] " + self.mp.getCWD() + "/> ")

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
        return self.msql.listDB()

    def mcmd_can_be_executed(self):
        if self.msql.bConnected:
            return True
        logging.info("Please connect first")
        return False

    def cmd_can_be_executed(self):
        if self.msql.bConnected:
            if self.msql.bSelected:
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
        self.msql.connect(args.host, args.user, args.password)

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
            bSelected = self.msql.useDB(args.model[0])
            if (bSelected):
                # manage paths
                self.mp.cd(self.mp.TINYMBSE_PATH)
                self.mp.removeFolder(args.model[0])
                self.mp.initFolders(args.model[0], 1, self.msql)
                self.mp.cd(args.model[0])
                # manage DB
                self.msql.intCWI = 1
        return

    # CMD: mnew #
    parser = argparse.ArgumentParser(description='create model', add_help=False)
    parser.add_argument('model', nargs=1, help="name of the model to be created", choices_method=get_db_list)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strMODEL_COMMANDS)
    def do_mnew(self, args):
        if self.mcmd_can_be_executed():
            bCreated = self.msql.createDB(args.model[0])
            if (bCreated):
                # manage paths
                self.mp.cd(self.mp.TINYMBSE_PATH)
                self.mp.newFolder(args.model[0])
                self.mp.cd(args.model[0])
                # manage DB
                self.msql.intCWI = 0
                self.msql.insertElement(args.model[0], 'folder', self.mp.getCWD(),0)
                self.msql.selectCWIperPath(self.mp.getCWD())

    # CMD: mdel #
    parser = argparse.ArgumentParser(description='delete model', add_help=False)
    parser.add_argument('model', nargs=1, help="name of the model to be deleted", choices_method=get_db_list)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strMODEL_COMMANDS)
    def do_mdel(self, args):
        if self.mcmd_can_be_executed():
            # manage Paths
            self.mp.removeFolder(self.mp.TINYMBSE_PATH + "/" + args.model[0])
            if (args.model[0] == self.msql.strSelectedDB):
                self.mp.cd(self.mp.TINYMBSE_PATH)
            # manage DB
            self.msql.dropDB(args.model[0])
        
    # CMD: insert #
    def insert_options(self) -> List[str]:
        """insert options"""
        return [element[1] for element in self.msql.getSonsPerId(self.msql.intCWI)] #element[1] is the name

    parser = argparse.ArgumentParser(description='insert element')
    parser.add_argument('type', help="type of element to be created", choices=md.listElementTypes)
    parser.add_argument('path', help="element path", completer_method=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_insert(self, args):
        """Creates insert element""" 
        if self.cmd_can_be_executed():
            # manage Paths
            self.mp.newFolder(args.path)
            # manage DB
            strPath = self.mp.getToolAbsPath(args.path)
            strName = self.mp.getNameFromPath(args.path)
            intParentId = self.msql.getIdperPath(self.mp.getToolAbsDirectory(args.path))
            self.msql.insertElement(strName, args.type, strPath, intParentId)
            return;

    # CMD: ls #
    parser = argparse.ArgumentParser(description='list elements and links')
    parser.add_argument('-l', '--links', required=False, default=False, action='store_true', help="show links")
    parser.add_argument('-p', '--showpath', required=False, default=False, action='store_true', help="show complete path instead of just name")
    parser.add_argument('path', help="path", nargs='?', default='.', completer_method=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_ls(self, args):
        """list elements""" 
        if self.cmd_can_be_executed():
            dictTypesSymbols = dict(zip(md.listLinkTypes, md.listLinkTypesSymbols))
            dictTypeColours = dict(zip(md.listElementTypes,md.listElementTypesColours))

            intId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.path))
            listSons = self.msql.getSonsPerId(intId)
            listLinks = []
            for element in listSons:
                links = self.msql.getLinksPerId(element[0]) #element[0] is the id
                for link in links:
                    if link not in listLinks:
                        listLinks.append(link)

            if (args.links):
                for source, destination, name, type in listLinks:
                    sourceData = self.msql.getElementPerId(source)
                    destinationData = self.msql.getElementPerId(destination)
                    intIndex = 1 #index for name in listElementField
                    if (args.showpath):
                        intIndex = 7 #index for path in listElementField
                        #5 is the index for type in listElementField
                    print ('{:<15} :: {:<30}{:^5}{:<30}'.format(name, ansi.style(sourceData[intIndex], fg=dictTypeColours[sourceData[5]]), dictTypesSymbols[type], ansi.style(destinationData[intIndex], fg=dictTypeColours[destinationData[5]])))
            else:
                strLine = ""
                for element in listSons:
                    listSonsOfSons = self.msql.getSonsPerId(element[0]) #element[0] is the id
                    if listSonsOfSons:
                        strLine += ansi.style('(+)' + element[1], fg=dictTypeColours[element[5]]) + "\t" #element[1] is the name, element[5] is the type
                    else:
                        strLine += ansi.style(element[1], fg=dictTypeColours[element[5]]) + "\t" #element[1] is the name, element[5] is the type
                self.ppaged(strLine, chop=True)
            return;

    # CMD: cd #
    @cmd2.with_argument_list
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_cd(self, args: List[str]):
        """Change working directory""" 
        if self.cmd_can_be_executed():
            self.mp.cd(args[0])
            self.msql.selectCWIperPath(self.mp.getCWD())
            self.ppaged(args[0], chop=True)
            return;

    complete_cd = cmd2.Cmd.path_complete

    # CMD: ln #
    parser = argparse.ArgumentParser(description='link to elements')
    parser.add_argument('origin', help="origin", completer_method=cmd2.Cmd.path_complete)
    parser.add_argument('destination', help="destination", completer_method=cmd2.Cmd.path_complete)
    parser.add_argument('-t', '--type', help="type of element to be created", choices=md.listLinkTypes)
    parser.add_argument('-n', '--name', help="name of the link")
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_ln(self, args):
        """Creates a link between two elements""" 
        if self.cmd_can_be_executed():
            strtype = 'dataflow'
            if args.type:
                strtype = args.type
            self.msql.insertLink(self.mp.getToolAbsPath(args.origin), self.mp.getToolAbsPath(args.destination), strtype, args.name) 
            return;

    # CMD: mv #
    def updatePath(self, listSons, oldPath, newPath):
        for element in listSons:
            self.msql.updatePathPerId(element[0], path.replace(oldPath, newPath, 1)) #element[0] is the id
            listSonsOfSons = self.msql.getSonsPerId(element[0]) #element[0] is the id
            self.updatePath(listSonsOfSons, oldPath, newPath)
        return;  
    parser = argparse.ArgumentParser(description='mv elements')
    parser.add_argument('source', help="source element", completer_method=cmd2.Cmd.path_complete)
    parser.add_argument('destination', help="destination folder", completer_method=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_mv(self, args):
        """moves an element""" 
        if self.cmd_can_be_executed():
            # manage Paths
            self.mp.mv(args.source, args.destination)
            # manage DB
            intSourceId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.source))
            intDestinationId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.destination))
            strSourceDirectory = self.mp.getToolAbsDirectory(args.source)
            self.msql.updateParentIdPerId(intSourceId, intDestinationId)
            self.msql.updatePathPerId(intSourceId, self.mp.getToolAbsPath(args.source).replace(strSourceDirectory, self.mp.getToolAbsPath(args.destination), 1))
            listSons = self.msql.getSonsPerId(intSourceId)
            self.updatePath(listSons, strSourceDirectory, self.mp.getToolAbsPath(args.destination))
        return;

    # CMD: rm #
    def deleteDescendants(self, listSons):
        for element in listSons:
            listSonsOfSons = self.msql.getSonsPerId(element[0]) #element[0] is the id
            self.deleteDescendants(listSonsOfSons)
            self.msql.deleteElementPerId(element[0]) #element[0] is the id
        return;
    parser = argparse.ArgumentParser(description='delete elements and its descendants')
    parser.add_argument('path', help="path to be deleted", completer_method=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_rm(self, args):
        """deletes an element and its descendants""" 
        if self.cmd_can_be_executed():
            # manage Paths
            self.mp.removeFolder(args.path)
            # manage DB
            intId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.path))
            listSons = self.msql.getSonsPerId(intId)
            self.deleteDescendants(listSons)
            self.msql.deleteElementPerId(intId)
        return;

