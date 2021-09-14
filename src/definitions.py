import yaml

# Model definition lists

### elements ###
# Definition
# the indices        0     1       2              3               4          5       6           7       8
listElementField = ['id', 'name', 'description', 'creationDate', 'version', 'type', 'parentId', 'path', 'refId']
ELEMENT_ID = 0
ELEMENT_NAME = 1
ELEMENT_DESCRIPTION = 2
ELEMENT_DATE = 3
ELEMENT_VERSION = 4
ELEMENT_TYPE = 5
ELEMENT_PARENT_ID = 6
ELEMENT_PATH = 7
ELEMENT_REFERENCE_ID = 8
# the indices        0         1           2        3            4       5        6          7
listElementTypes = ['folder', 'function', 'block', 'component', 'data', 'actor', 'usecase', 'reference']
E_TYPE_FOLDER = 0
E_TYPE_FUNCTION = 1
E_TYPE_BLOCK = 2
E_TYPE_COMPONENT = 3
E_TYPE_DATA = 4
E_TYPE_ACTOR = 5
E_TYPE_USECASE = 6
E_TYPE_REFERENCE = 7
# SQL - Please keep it consistent with Definiton
strElementTableName = "element"
listElementFieldSQL = ['INT PRIMARY KEY AUTO_INCREMENT UNIQUE',
                       'VARCHAR(255) NOT NULL',
                       'VARCHAR(1000)',
                       'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                       'FLOAT',
                       'ENUM(' + ",".join(["'{}'".format(x) for x in listElementTypes]) + ") NOT NULL",
                       'INT REFERENCES ' + strElementTableName + '(id)',
                       'VARCHAR(1024)',
                       'INT REFERENCES ' + strElementTableName + '(id)']
# CMD  - Please keep it consistent with Definiton
listElementTypesColours = ['blue', 'bright_green', 'bright_cyan', 'bright_magenta', 'magenta', 'bright_yellow', 'on_blue', 'bright_blue']
# PlantUML
listElementTypesPlot = ['folder', 'rectangle', 'node', 'component', 'rectangle', 'actor', 'usecase', 'hexagon']



### links def ###
# Definition
# the indices     0     1       2              3               4          5       6           7         8
listLinkField = ['id', 'name', 'description', 'creationDate', 'version', 'type', 'parentId', 'source', 'destination']
LINK_ID = 0
LINK_NAME = 1
LINK_DESCRIPTION = 2
LINK_DATE = 3
LINK_VERSION = 4
LINK_TYPE = 5
LINK_PARENT_ID = 6
LINK_SOURCE_ID = 7
LINK_DESTINATION_ID = 8
# the indices     0           1              2
listLinkTypes = ['dataflow', 'aggregation', 'link']
L_TYPE_DATAFLOW = 0
L_TYPE_AGGREGATION = 1
L_TYPE_LINK = 2
# SQL  - Please keep it consistent with Definiton
strLinkTableName = "link"
listLinkFieldSQL = ['INT PRIMARY KEY AUTO_INCREMENT UNIQUE',
                    'VARCHAR(255) NOT NULL',
                    'VARCHAR(1000)',
                    'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                    'FLOAT',
                    'ENUM(' + ",".join(["'{}'".format(x) for x in listLinkTypes]) + ") NOT NULL",
                    'INT REFERENCES ' + strLinkTableName + '(id)',
                    'INT, FOREIGN KEY (source) REFERENCES ' + strElementTableName + '(id) ON DELETE CASCADE', 
                    'INT, FOREIGN KEY (destination) REFERENCES ' + strElementTableName + '(id) ON DELETE CASCADE']

# CMD  - Please keep it consistent with Definiton
listLinkTypesSymbols = ['->', '-|>', '-']

### conveyed ###
# Definition
listConveyedField = ['link', 'element']
# SQL
strConveyedTableName = "conveyed"
listConveyedFieldSQL = ['INT, FOREIGN KEY ' + strLinkTableName+ '(id)',
                        'INT, FOREIGN KEY ' + strElementTableName + '(id)']

class config():

    def __init__(self):

        # load configuration 
        with open("config.yml", 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        