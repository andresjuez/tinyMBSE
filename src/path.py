import os
import shutil
import src.definitions as md

class modelpath():
    """ This class keeps the model state """

    def __init__(self):

        # TINYMBSE_PATH = get from configuration file
        self.TINYMBSE_PATH = md.config().config["general"]["pathtmp"]

        # clean previous
        self.removeFolder(self.TINYMBSE_PATH)

        if not os.path.exists(self.TINYMBSE_PATH):
            os.makedirs(self.TINYMBSE_PATH)

        os.chdir(self.TINYMBSE_PATH)

        self.TINYMBSE_PATH = os.getcwd()

        self.previousWD = os.getcwd()

    def initFolders(self, name, id, type, modelsql):
        if (type == md.listElementTypes[md.E_TYPE_REFERENCE]):
            element = modelsql.getElementPerId(id)
            referencedElement = modelsql.getElementPerId(element[md.ELEMENT_REFERENCE_ID])
            self.newReference(name, os.path.relpath(self.TINYMBSE_PATH + referencedElement[md.ELEMENT_PATH], os.getcwd()))
            return
        else:
            self.newFolder(name)
        self.cd(name)
        strCD = os.getcwd()
        for element in modelsql.getSonsPerId(id):
            self.cd(strCD)
            self.initFolders(element[md.ELEMENT_NAME], element[md.ELEMENT_ID], element[md.ELEMENT_TYPE], modelsql)
        self.cd(self.TINYMBSE_PATH)
        return

    def getCWD(self):
        return os.getcwd().replace(self.TINYMBSE_PATH,'')

    def getToolAbsPath(self, strRelativePath):
        return os.path.realpath(os.path.abspath(strRelativePath)).replace(self.TINYMBSE_PATH,'')

    def getRelativePath(self, strPath):
        return os.path.relpath(strPath, self.getCWD())
    
    def getToolAbsDirectory(self, strRelativePath):
        return os.path.dirname(os.path.abspath(strRelativePath).replace(self.TINYMBSE_PATH,''))

    def getNameFromPath(self, strPath):
        return os.path.basename(strPath)

    def cd(self, foldername):
        if (foldername == '-'):
            tempFolder = self.previousWD
            self.previousWD = os.getcwd()
            return os.chdir(tempFolder)
        else:
            self.previousWD = os.getcwd()
            return os.chdir(foldername)

    def cdHOME(self, rootElementPath):
        homepath = os.path.join(self.TINYMBSE_PATH, os.path.basename(rootElementPath))
        self.cd(homepath)
        
    def newFolder(self, foldername):
        return os.makedirs(foldername)

    def newReference(self, foldername, reference):
        return os.symlink(reference, foldername)

    def removeFolder(self, foldername):
        if os.path.exists(foldername):
            return shutil.rmtree(foldername)

    def mv(self, source, destination):
        if os.path.exists(source):
            return shutil.move(source, destination)
