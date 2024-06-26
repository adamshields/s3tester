```
import os
import xml.etree.ElementTree as ET

# Define the directory containing the XML files
directory = 'TABLES'

# Register the namespace to avoid ns0 prefix
ET.register_namespace('', "http://www.liquibase.org/xml/ns/dbchangelog")

# Function to modify XML files
def modify_xml(file_path, new_id, new_author, context, label):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Modify each changeSet
    for changeSet in root.findall('{http://www.liquibase.org/xml/ns/dbchangelog}changeSet'):
        changeSet.set('id', new_id)
        changeSet.set('author', new_author)
        changeSet.set('context', context)
        changeSet.set('labels', label)
    
    # Write back the modified XML to the file
    tree.write(file_path, encoding='utf-8', xml_declaration=True)

# Custom values to be used for replacement
new_id = 'custom-id-123'
new_author = 'custom-author'
context = '1'
label = 'custom-label'

# Iterate through all XML files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.xml'):
        file_path = os.path.join(directory, filename)
        modify_xml(file_path, new_id, new_author, context, label)

print('All XML files have been modified.')
```
