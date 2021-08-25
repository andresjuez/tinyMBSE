# Model definition lists

### elements ###
# Definition
# the indices        0     1       2              3               4          5       6           7       8
listElementField = ['id', 'name', 'description', 'creationDate', 'version', 'type', 'parentId', 'path', 'refId']
# the indices        0         1           2        3            4       5        6          7
listElementTypes = ['folder', 'function', 'block', 'component', 'data', 'actor', 'usecase', 'reference']
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
listElementTypesPlot = ['folder', 'storage', 'node', 'component', 'rectangle', 'actor', 'usecase', 'hexagon']



### links def ###
# Definition
# the indices     0     1       2              3               4          5       6           7         8
listLinkField = ['id', 'name', 'description', 'creationDate', 'version', 'type', 'parentId', 'source', 'destination']
listLinkTypes = ['dataflow', 'aggregation', 'link']
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


