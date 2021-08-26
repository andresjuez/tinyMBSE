import logging
import mysql.connector
import src.definitions as md

class modelsql():

    def __init__(self):

        # indicates if it is connected to mysql server or not
        self.bConnected = False

        # indicates if a dabase is selected
        self.bSelected = False
        self.strSelectedDB = ""

        # indicates user and host
        self.strUser = ""
        self.strHost = ""

        # CWI: current workding item, id from elemement table, which could be an element (either of type folder or not) 
        self.intCWI = 0

        # start logger
        logger = logging.getLogger()
        LOGGINGFORMAT = "%(levelname)s: %(message)s"
        logging.basicConfig(format=LOGGINGFORMAT)
        logger.setLevel(logging.INFO)

    def _fetchall(self, intIndex):
        return [item[intIndex] for item in self.cursor.fetchall()] 

    def connect(self, host, user, password):
        """Connects to mysql server"""
        self.db =  mysql.connector.connect(host=host, user=user, password=password)
        if (self.db):
            self.cursor = self.db.cursor()
            logging.info("Connected to mysql server")
            self.bConnected = True
            self.strUser = user
            self.strHost = host
            return True
        else:
            logging.error("Unable to connect to mysql server")
            return False

    def showDBs(self):
        """Show DBs"""
        self.cursor.execute("SHOW DATABASES")
        return (self._fetchall(0))

    def useDB(self, dbname):
        self.cursor.execute("SHOW DATABASES")
        listDB = self._fetchall(0)
        if dbname in listDB:
            self.cursor.execute("USE " + dbname)
            logging.info(dbname + " selected")
            self.bSelected = True
            self.strSelectedDB = dbname
            return True
        else:
            logging.error(dbname + " does not exist")
            return False

    def listDB(self):
        self.cursor.execute("SHOW DATABASES")
        return(self._fetchall(0))
                
    def createDB(self, dbname):
        self.cursor.execute("CREATE DATABASE " + dbname)
        logging.info(dbname + " created")
        bSelected = self.useDB(dbname)
        if bSelected:
            strElementTable = md.strElementTableName + "(" + ",".join("{} {}".format(x,y) for x,y in zip(md.listElementField, md.listElementFieldSQL)) + ")"
            self.cursor.execute("CREATE TABLE " + strElementTable)          
            strLinkTable = md.strLinkTableName + "(" + ",".join("{} {}".format(x,y) for x,y in zip(md.listLinkField, md.listLinkFieldSQL)) + ")"
            self.cursor.execute("CREATE TABLE " + strLinkTable)
        return bSelected

    def dropDB(self, dbname):
        self.cursor.execute("DROP DATABASE " + dbname)
        if self.strSelectedDB == dbname:
            self.bSelected = False
            self.strSelectedDB = ""
        logging.info(dbname + " deleted")

    def insertElement(self, name, elementType, path, parentId, refId):
        if (parentId == 0):
            self.cursor.execute("INSERT INTO " + md.strElementTableName + "(name, type, path) VALUES(" + "'{}','{}',{}".format(name, elementType, repr(path)) + ")")    
        else:
            self.cursor.execute("INSERT INTO " + md.strElementTableName + "(name, type, path, parentId, refId) VALUES(" + "'{}','{}',{},'{}','{}'".format(name, elementType, repr(path), parentId, refId) + ")")
        self.db.commit()
        logging.info(name + " inserted")

    def getIdperPath(self, path):
        self.cursor.execute("SELECT id FROM " + md.strElementTableName + " WHERE path = {}".format(repr(path)))
        return self._fetchall(0)[0]

    def getElementPerId(self, id):
        self.cursor.execute("SELECT " + ",".join(md.listElementField) + " FROM " + md.strElementTableName + " WHERE id = '{}'".format(id))
        return self.cursor.fetchall()[0]

    def selectCWIperPath(self, path):
        self.intCWI = self.getIdperPath(path)

    def getSonsPerId(self, intId):
        self.cursor.execute("SELECT " + ",".join(md.listElementField) + " FROM element WHERE parentId = '{}'".format(str(intId)))
        return self.cursor.fetchall()

    def getDescendantsPerId(self, intId, listDescendants):
        listSons = self.getSonsPerId(intId)
        listDescendants.extend(listSons)
        for element in listSons:
            self.getDescendantsPerId(element[0], listDescendants)

    def updateNamePerId(self, intId, newName):
        self.cursor.execute("UPDATE " + md.strElementTableName + " SET name = '{}' WHERE id = '{}'".format(str(newName), str(intId)))
        self.db.commit()
    
    def updatePathPerId(self, intId, newPath):
        self.cursor.execute("UPDATE " + md.strElementTableName + " SET path = {} WHERE id = '{}'".format(repr(str(newPath)), str(intId)))
        self.db.commit()

    def updateParentIdPerId(self, intId, newParentId):
        self.cursor.execute("UPDATE " + md.strElementTableName + " SET parentId = '{}' WHERE id = '{}'".format(str(newParentId), str(intId)))
        self.db.commit()
        
    def insertLink(self, path_origin, path_destination, type, name):
        sourceId = self.getIdperPath(path_origin)
        destinationId = self.getIdperPath(path_destination)
        dictTypesSymbols = dict(zip(md.listLinkTypes, md.listLinkTypesSymbols))
        self.cursor.execute("INSERT INTO " + md.strLinkTableName + "(source, destination, type, name) VALUES(" + "{},{},'{}','{}'".format(repr(sourceId), repr(destinationId), str(type), str(name)) + ")")
        self.db.commit()
        logging.info(type + "link inserted: " + path_origin + " " + dictTypesSymbols[type] + " " + path_destination)

    def getLinksPerId(self, id):
        self.cursor.execute("SELECT " + ",".join(md.listLinkField) + " FROM " + md.strLinkTableName + "  WHERE source = '{}' OR destination = '{}'".format(str(id), str(id)))
        return self.cursor.fetchall()
  
    def deleteElementPerId(self, intId):
        self.cursor.execute("DELETE FROM " + md.strElementTableName + " WHERE id = '{}'".format(str(intId)))
        self.db.commit()

    def deleteLinkPerId(self, intSourceId, intDestinationId):
        self.cursor.execute("DELETE FROM " + md.strLinkTableName + " WHERE source = '{}' AND destination = '{}'".format(str(intSourceId), str(intDestinationId))) 
        self.db.commit()
