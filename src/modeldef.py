# Model definition lists

### elements def ###
listElementField = ['id', 'name', 'description', 'creationDate', 'version', 'type', 'parentId', 'path']
listElementTypes = ['folder', 'function', 'block', 'component', 'data']
# SQL
strElementTableName = "element"
listElementFieldSQL = ['INT PRIMARY KEY AUTO_INCREMENT UNIQUE',
                       'VARCHAR(255) NOT NULL',
                       'VARCHAR(1000)',
                       'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                       'FLOAT',
                       'ENUM(' + ",".join(["'{}'".format(x) for x in listElementTypes]) + ") NOT NULL",
                       'INT REFERENCES ' + strElementTableName + '(id)',
                       'VARCHAR(1024)']
# CMD 
listElementTypesColours = ['blue', 'bright_green', 'bright_cyan', 'bright_magenta', 'magenta']




### links def ###
listLinkField = ['id', 'name', 'description', 'creationDate', 'version', 'type', 'parentId', 'source', 'destination']
listLinkTypes = ['dataflow', 'aggregation', 'link']
# SQL
strLinkTableName = "link"
listLinkFieldSQL = ['INT PRIMARY KEY AUTO_INCREMENT UNIQUE',
                    'VARCHAR(255) NOT NULL',
                    'VARCHAR(1000)',
                    'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                    'FLOAT',
                    'ENUM(' + ",".join(["'{}'".format(x) for x in listLinkTypes]) + ") NOT NULL",
                    'INT REFERENCES ' + strLinkTableName + '(id)',
                    'INT, FOREIGN KEY (source) REFERENCES ' + strElementTableName + '(id)', 
                    'INT, FOREIGN KEY (destination) REFERENCES ' + strElementTableName + '(id)']

# CMD 
listLinkTypesSymbols = ['->', '-|>', '-']

### conveyed ###
listConveyedField = ['link', 'element']
# SQL
strConveyedTableName = "conveyed"
listConveyedFieldSQL = ['INT, FOREIGN KEY ' + strLinkTableName+ '(id)',
                        'INT, FOREIGN KEY ' + strElementTableName + '(id)']


