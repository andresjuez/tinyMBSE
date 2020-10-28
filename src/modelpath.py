import os
from os import environ
import shutil

class modelpath():
    """ This class keeps the model state """

    def __init__(self):

        # CLIMB_PATH = environment variable for deploying path_complete (./ if not provided)
        self.CLIMB_PATH = "./.climb"

        if environ.get("CLIMB_PATH") is not None:
            self.CLIMB_PATH = environ.get("CLIMB_PATH")

        # clean previous
        self.removeFolder(self.CLIMB_PATH)

        if not os.path.exists(self.CLIMB_PATH):
            os.makedirs(self.CLIMB_PATH)

        os.chdir(self.CLIMB_PATH)

        self.CLIMB_PATH = os.getcwd()

    def initFolders(self, name, id, modelsql):
        self.newFolder(name)
        self.cd(name)
        strCD = os.getcwd()
        for sonId, parentId, sonName, type in modelsql.getSonsPerId(id):
            self.cd(strCD)
            self.initFolders(sonName, sonId, modelsql)
        self.cd(self.CLIMB_PATH)
        return

    def getCWD(self):
        return os.getcwd().replace(self.CLIMB_PATH,'')

    def getAbsPath(self, strRelativePath):
        return os.path.abspath(strRelativePath).replace(self.CLIMB_PATH,'')

    def cd(self, foldername): 
        return os.chdir(foldername)
        
    def newFolder(self, foldername):
        return os.makedirs(foldername)

    def removeFolder(self, foldername):
        if os.path.exists(foldername):
            return shutil.rmtree(foldername)



 
        
        
