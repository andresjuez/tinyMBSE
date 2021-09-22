import sys
import argparse
import cmd2
from cmd2 import bg, fg, style, ansi
from typing import List
import src.sql as msql
import src.path as mp
import src.plot as mplt
import src.term as mt
import src.definitions as md
import src.links as ml
import logging
from prettytable import PrettyTable

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")
class modelcmd(cmd2.Cmd):
    """ This manages the model in the SQL database """
    # command categories
    strMODEL_COMMANDS = "Model Commands"
    strELEMENT_COMMANDS = "Element Commands"

    def __init__(self):

        # call parent
        super().__init__(multiline_commands=['echo'], persistent_history_file='.tinyMBSE_history.dat', include_ipy=True)

        # intro
        self.intro = style('Welcome to (tiny)MBSE! model using the command line interface', bold=True)

        # load configuration
        self.config = md.config()

        # model sql management
        self.msql = msql.modelsql()

        # model path management
        self.mp = mp.modelpath()

        # Allow access to your application in py and ipy via self
        self.self_in_py = True

        # connnect to the databse
        logging.info("Connecting to the SQL server")
        self.msql.connect(self.config.config["db"]["host"], self.config.config["db"]["user"], self.config.config["db"]["pwd"])

        # set prompt
        self._set_prompt()

    def _set_prompt(self):
        """Set prompt so it displays the current working directory."""
        if (self.msql.bConnected == False):
            self.prompt = ansi.style(f'Disconnected/> ', fg='bright_red')
            return
        self.prompt = ansi.style("[" + self.msql.strUser + "@" + self.msql.strHost + "][" + \
                                 str(self.msql.intCWI) + "] " + self.mp.getCWD() + "> ")

    def postcmd(self, stop: bool, line: str) -> bool:
        """Hook method executed just after a command dispatch is finished."""
        self._set_prompt()
        return stop

    # ANCILLIARY get model list
    def get_db_list(self) -> List[str]:
        """list of available db options"""
        return self.msql.listDB()

    def cmd_can_be_executed(self):
        if self.msql.bConnected:
            if self.msql.bSelected:
                return True
            else:
                logging.info("Please Select Model first")
        else:
            logging.info("Please connect first")
        return False

    #                #
    # MODEL COMMANDS #
    #                #

    # CMD: mls #
    @cmd2.with_category(strMODEL_COMMANDS)
    def do_mls(self, args):
        """List of models"""
        self.ppaged("\n".join(self.get_db_list()), chop=True)

    # CMD: msel #
    parser = argparse.ArgumentParser(description='select model to work with', add_help=False)
    parser.add_argument('model', nargs=1, help="model name", choices_provider=get_db_list)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strMODEL_COMMANDS)
    def do_msel(self, args):
        bSelected = self.msql.useDB(args.model[0])
        if (bSelected):
            # manage paths
            self.mp.cd(self.mp.TINYMBSE_PATH)
            self.mp.removeFolder(args.model[0])
            self.mp.initFolders(args.model[0], 1, md.listElementTypes[md.E_TYPE_FOLDER], self.msql)
            self.mp.cd(args.model[0])
            # manage DB
            self.msql.intCWI = 1

    # CMD: mnew #
    parser = argparse.ArgumentParser(description='create model', add_help=False)
    parser.add_argument('model', nargs=1, help="name of the model to be created", choices_provider=get_db_list)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strMODEL_COMMANDS)
    def do_mnew(self, args):
        bCreated = self.msql.createDB(args.model[0])
        if (bCreated):
            # manage paths
            self.mp.cd(self.mp.TINYMBSE_PATH)
            self.mp.newFolder(args.model[0])
            self.mp.cd(args.model[0])
            # manage DB
            self.msql.intCWI = 0
            self.msql.insertElement(args.model[0], 'folder', self.mp.getCWD(),0, 0)
            self.msql.selectCWIperPath(self.mp.getCWD())

    # CMD: mdel #
    parser = argparse.ArgumentParser(description='delete model', add_help=False)
    parser.add_argument('model', nargs=1, help="name of the model to be deleted", choices_provider=get_db_list)
    parser.add_argument('-f', '--force', required=False, default=False, action='store_true', help="force deletion without prompting question")
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strMODEL_COMMANDS)
    def do_mdel(self, args):
        response = True
        if not args.force:
            response = query_yes_no("are you sure you want to delete " + args.model[0] + "?", "no")
        if response is True:
            # manage Paths
            self.mp.removeFolder(self.mp.TINYMBSE_PATH + "/" + args.model[0])
            if (args.model[0] == self.msql.strSelectedDB):
                self.mp.cd(self.mp.TINYMBSE_PATH)
            # manage DB
            self.msql.dropDB(args.model[0])
        else:
            logging.info("Deletion canceled")

    #                   #
    # ELEMENTS COMMANDS #
    #                   #

    # CMD: cd #
    parser = argparse.ArgumentParser(description='changes directory')
    parser.add_argument('path', help="path", nargs='?', completer=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_cd(self, args: List[str]):
        """Change working directory"""
        if self.cmd_can_be_executed():
            if (args.path is None):
                rootElement = self.msql.getElementPerId(1) # get first element
                self.mp.cdHOME(rootElement[md.ELEMENT_PATH])
            else:
                self.mp.cd(args.path)
            self.msql.selectCWIperPath(self.mp.getCWD())
            return;

    # CMD: insert #
    def insert_options(self) -> List[str]:
        """insert options"""
        return [element[1] for element in self.msql.getSonsPerId(self.msql.intCWI)] #element[1] is the name

    parser = argparse.ArgumentParser(description='insert element')
    parser.add_argument('type', help="type of element to be created", choices=md.listElementTypes)
    parser.add_argument('path', help="element path", completer=cmd2.Cmd.path_complete)
    parser.add_argument('ref', nargs='?', help="referenced element (only in case a reference is inserted)", completer=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_insert(self, args):
        """Creates insert element"""
        if self.cmd_can_be_executed():
            # manage Paths
            if (args.type == md.listElementTypes[md.E_TYPE_REFERENCE]):
                self.mp.newReference(args.path, args.ref)
            else:
                self.mp.newFolder(args.path)
            # manage DB
            strPath = self.mp.getToolAbsPath(args.path)
            strName = self.mp.getNameFromPath(args.path)
            intParentId = self.msql.getIdperPath(self.mp.getToolAbsDirectory(args.path))
            strRefId = 1
            if (args.type == md.listElementTypes[md.E_TYPE_REFERENCE]):
                strRefId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.ref))
            self.msql.insertElement(strName, args.type, strPath, intParentId, strRefId)
            return;

    # CMD: ls #
    parser = argparse.ArgumentParser(description='list elements')
    parser.add_argument('path', help="path", nargs='?', default='.', completer=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_ls(self, args):
        """list elements"""
        if self.cmd_can_be_executed():
            intId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.path))
            listElements = self.msql.getSonsPerId(intId)
            mt.printelements(self.msql, listElements)
            return;

    # CMD: tree #
    parser = argparse.ArgumentParser(description='list elements in tree form')
    parser.add_argument('path', help="path", nargs='?', default='.', completer=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_tree(self, args):
        """list elements"""
        if self.cmd_can_be_executed():
            intId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.path))
            mt.printtree(self.msql, intId)
            return;

    # CMD: mv #
    def updatePath(self, listSons, oldPath, newPath):
        for element in listSons:
            self.msql.updatePathPerId(element[md.ELEMENT_ID], element[md.ELEMENT_PATH].replace(oldPath, newPath, 1)) 
            listSonsOfSons = self.msql.getSonsPerId(element[md.ELEMENT_ID]) 
            self.updatePath(listSonsOfSons, oldPath, newPath)
        return;
    parser = argparse.ArgumentParser(description='mv elements')
    parser.add_argument('source', help="source element", completer=cmd2.Cmd.path_complete)
    parser.add_argument('destination', help="destination folder", completer=cmd2.Cmd.path_complete)
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
            listSonsOfSons = self.msql.getSonsPerId(element[md.ELEMENT_ID])
            self.deleteDescendants(listSonsOfSons)
            self.msql.deleteElementPerId(element[md.ELEMENT_ID]) #element[0] is the id
        return;
    parser = argparse.ArgumentParser(description='delete elements')
    parser.add_argument('path', help="path to the element to be deleted", completer=cmd2.Cmd.path_complete)
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

    # CMD: info #
    parser = argparse.ArgumentParser(description='provides the information of a given element')
    parser.add_argument('path', help="path", nargs='?', default='.', completer=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_info(self, args):
        """generates a plot through plantUML"""
        if self.cmd_can_be_executed():
            intId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.path))
            element = self.msql.getElementPerId(intId)
            dictElementFieldvsContents = dict(zip(md.listElementField, list(element)))
            t = PrettyTable(['Field', 'Value'])
            t.align = "l"
            for field, content in dictElementFieldvsContents.items():
                t.add_row([field, content])
            print(t)
        return;

    #                #
    # LINKS COMMANDS #
    #                #

    # CMD: ll #
    parser = argparse.ArgumentParser(description='list elements links')
    parser.add_argument('-g', '--group', required=False, default=False, action='store_true', help="links which have the same source and destination are grouped")
    parser.add_argument('-e', '--external', required=False, default=False, action='store_true', help="considers also those elements outside this folder to show links")
    parser.add_argument('-f', '--fundamental', required=False, default=False, action='store_true', help="only fundamental links are shown")
    parser.add_argument('path', help="path", nargs='?', default='.', completer=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_ll(self, args):
        """list elements"""
        if self.cmd_can_be_executed():
            intId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.path)) # get id 
            listElements = self.msql.getSonsPerId(intId)
            if (args.external):
                listElements = ml.extendElements(self.msql, listElements)
            if (args.path != '.'):
                listElements = list()
                listElements.append(self.msql.getElementPerId(intId))
                listElements = ml.extendElements(self.msql, listElements)
            mt.printlinks(self.msql, self.mp, listElements, args.group, args.fundamental)
            return;

    # CMD: ln #
    parser = argparse.ArgumentParser(description='link to elements')
    parser.add_argument('origin', help="origin", completer=cmd2.Cmd.path_complete)
    parser.add_argument('destination', help="destination", completer=cmd2.Cmd.path_complete)
    parser.add_argument('-t', '--type', help="type of element to be created", choices=md.listLinkTypes)
    parser.add_argument('-n', '--name', help="name of the link")
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_ln(self, args):
        """Creates a link between two elements"""
        if self.cmd_can_be_executed():          
            strType = md.listLinkTypes[md.L_TYPE_DATAFLOW]
            if args.type:
                strType = args.type
            self.msql.insertLink(self.mp.getToolAbsPath(args.origin), self.mp.getToolAbsPath(args.destination), strType, args.name)
            return;

    # CMD: rml #
    parser = argparse.ArgumentParser(description='delete elements')
    parser.add_argument('path', help="path to element start element", completer=cmd2.Cmd.path_complete)
    parser.add_argument('dest', help="path to element destination element", completer=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_rml(self, args):
        """deletes an element and its descendants"""
        if self.cmd_can_be_executed():
            sourceId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.path))
            destinationId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.dest))
            self.msql.deleteLinkPerId(sourceId, destinationId)
        return;

    #                #
    # OTHER COMMANDS #
    #                #

    # CMD: plot #
    parser = argparse.ArgumentParser(description='generates a plot')
    parser.add_argument('-t', '--tree', required=False, default=False, action='store_true', help="show tree of elements")
    parser.add_argument('-g', '--group', required=False, default=False, action='store_true', help="links which have the same source and destination are grouped")
    parser.add_argument('-e', '--external', required=False, default=False, action='store_true', help="considers also those elements outside this folder to show links")
    parser.add_argument('-f', '--fundamental', required=False, default=False, action='store_true', help="only fundamental links are shown")
    parser.add_argument('path', help="path", nargs='?', default='.', completer=cmd2.Cmd.path_complete)
    @cmd2.with_argparser(parser)
    @cmd2.with_category(strELEMENT_COMMANDS)
    def do_plot(self, args):
        """generates a plot through plantUML"""
        if self.cmd_can_be_executed():
            if (args.tree):
                intId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.path))
                mplt.plotTree(self.msql, intId, self.config.config)
            else:
                intId = self.msql.getIdperPath(self.mp.getToolAbsPath(args.path)) # get id 
                listElements = self.msql.getSonsPerId(intId)
                if (args.external):
                    listElements = ml.extendElements(self.msql, listElements)
                mplt.plotDFD(self.msql, listElements, self.config.config, args.group, args.fundamental)
        return;
