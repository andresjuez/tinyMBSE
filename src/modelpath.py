import os
from os import environ
import shutil

class modelpath():
    """ This class keeps the model state """

    def __init__(self):

        # TINYMBSE_PATH = environment variable for deploying path_complete (./ if not provided)
        self.TINYMBSE_PATH = "./.tinyMBSE"

        if environ.get("TINYMBSE_PATH") is not None:
            self.TINYMBSE_PATH = environ.get("TINYMBSE_PATH")

        # clean previous
        self.removeFolder(self.TINYMBSE_PATH)

        if not os.path.exists(self.TINYMBSE_PATH):
            os.makedirs(self.TINYMBSE_PATH)

        os.chdir(self.TINYMBSE_PATH)

        self.TINYMBSE_PATH = os.getcwd()

    def initFolders(self, name, id, modelsql):
        self.newFolder(name)
        self.cd(name)
        strCD = os.getcwd()
        for sonId, parentId, sonName, type, path in modelsql.getSonsPerId(id):
            self.cd(strCD)
            self.initFolders(sonName, sonId, modelsql)
        self.cd(self.TINYMBSE_PATH)
        return

    def getCWD(self):
        return os.getcwd().replace(self.TINYMBSE_PATH,'')

    def getToolAbsPath(self, strRelativePath):
        return os.path.abspath(strRelativePath).replace(self.TINYMBSE_PATH,'')
    
    def getToolAbsDirectory(self, strRelativePath):
        return os.path.dirname(os.path.abspath(strRelativePath).replace(self.TINYMBSE_PATH,''))

    def cd(self, foldername): 
        return os.chdir(foldername)
        
    def newFolder(self, foldername):
        return os.makedirs(foldername)

    def removeFolder(self, foldername):
        if os.path.exists(foldername):
            return shutil.rmtree(foldername)

    def mv(self, source, destination):
        if os.path.exists(source):
            return shutil.move(source, destination)


 
        
        
