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
                self.msql.insertElement(args.model[0], 'folder', self.mp.getCWD())
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
        return [item[2] for item in self.msql.getSonsPerId(self.msql.intCWI)] 

    parser = argparse.ArgumentParser(description='insert element')
    parser.add_argument('type', help="type of element to be created", choices=md.listElementTypes)
    parser.add_argument('name', help="element name", choices_method=insert_options)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_insert(self, args):
        """Creates insert element""" 
        if self.cmd_can_be_executed():
            # manage Paths
            self.mp.newFolder(args.name)
            # manage DB
            self.msql.insertElement(args.name, args.type, self.mp.getCWD()+"/"+args.name)
            return;

    # CMD: ls #
    parser = argparse.ArgumentParser(description='list elements and links')
    parser.add_argument('-l', '--links', required=False, default=False, action='store_true', help="host to connect to database")
    parser.add_argument('path', help="path", nargs='?', completer_method=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_ls(self, args):
        """list elements""" 
        if self.cmd_can_be_executed():
            if (args.path):
                intId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.path))
            else:
                intId = self.msql.intCWI                
            listSons = self.msql.getSonsPerId(intId)
            dictTypeColours = dict(zip(md.listElementTypes,md.listElementTypesColours))
            if (args.links):
                listLinks = []
                for id, parentId, name, type, path in listSons:
                    listLinks += self.msql.getLinksPerId(id)
                for source, destination in set(listLinks):
                    sourceData = self.msql.getElementNamePerId(source)
                    destinationData = self.msql.getElementNamePerId(destination)
                    print (ansi.style(sourceData[0][0], fg=dictTypeColours[sourceData[0][1]]) + "\t->\t" + ansi.style(destinationData[0][0], fg=dictTypeColours[destinationData[0][1]]))
            else:
                self.ppaged("\t".join([ansi.style(i[2], fg=dictTypeColours[i[3]]) for i in listSons]), chop=True)
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
        for id, parentId, name, type, path in listSons:
            self.msql.updatePathPerId(id, path.replace(oldPath, newPath, 1))
            listSonsOfSons = self.msql.getSonsPerId(id)
            self.updatePath(listSonsOfSons, oldPath, newPath)
        return;
    
    parser = argparse.ArgumentParser(description='mv elements')
    parser.add_argument('source', help="source", completer_method=cmd2.Cmd.path_complete)
    parser.add_argument('destination', help="destination", completer_method=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_mv(self, args):
        """moves an element""" 
        if self.cmd_can_be_executed():
            self.mp.mv(args.source, args.destination)
            intSourceId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.source))
            intDestinationId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.destination))
            strSourceDirectory = self.mp.getToolAbsDirectory(args.source)
            print (str(intSourceId) + " --> " + str(intDestinationId) + " --> " + str(strSourceDirectory))
            self.msql.updateParentIdPerId(intSourceId, intDestinationId)
            self.msql.updatePathPerId(intSourceId, self.mp.getToolAbsPath(args.source).replace(strSourceDirectory, self.mp.getToolAbsPath(args.destination), 1))
            listSons = self.msql.getSonsPerId(intSourceId)
            self.updatePath(listSons, strSourceDirectory, self.mp.getToolAbsPath(args.destination))
        return;

