import logging
import mysql.connector
import modeldef as md

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

    def insertElement(self, name, elementType, path):
        self.cursor.execute("INSERT INTO element(name, type, path, parentId) VALUES(" + "'{}','{}','{}','{}'".format(name, elementType, path, str(self.intCWI)) + ")")
        self.db.commit()
        logging.info(name + " inserted")

    def getIdperPath(self, path):
        self.cursor.execute("SELECT id FROM element WHERE path = '{}'".format(path))
        return self._fetchall(0)[0]

    def getElementNamePerId(self, id):
        self.cursor.execute("SELECT name, type FROM element WHERE id = '{}'".format(id))
        return self.cursor.fetchall()

    def selectCWIperPath(self, path):
        self.intCWI = self.getIdperPath(path)

    def getSonsPerId(self, intId):
        self.cursor.execute("SELECT id, parentId, name, type FROM element WHERE parentId = '{}'".format(str(intId)))
        return self.cursor.fetchall()
        
    def insertLink(self, path_origin, path_destination, type, name):
        sourceId = self.getIdperPath(path_origin)
        destinationId = self.getIdperPath(path_destination)
        self.cursor.execute("INSERT INTO link(source, destination, type, name) VALUES(" + "{},{},'{}','{}'".format(sourceId, destinationId, str(type), str(name)) + ")")
        self.db.commit()
        logging.info(type + "link inserted: " + path_origin + " -> " + path_destination)

    def getLinksPerId(self, id):
        self.cursor.execute("SELECT source, destination FROM link  WHERE source = '{}' OR destination = '{}'".format(str(id), str(id)))
        return self.cursor.fetchall()
