```
import os
import xml.etree.ElementTree as ET

# Define the base directory of the project
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
resources_dir = os.path.join(base_dir, 'src', 'main', 'resources')
changelog_dir = os.path.join(resources_dir, 'DATABASE', 'CHANGELOG')
table_dir = os.path.join(resources_dir, 'DATABASE', 'TABLE')
master_file = os.path.join(changelog_dir, 'master.xml')

# Register the namespace to avoid ns0 prefix
ET.register_namespace('', "http://www.liquibase.org/xml/ns/dbchangelog")

# Function to modify XML files
def modify_xml(file_path, base_id):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        change_set_counter = 1
        for changeSet in root.findall('{http://www.liquibase.org/xml/ns/dbchangelog}changeSet'):
            new_id = f"{base_id}-{change_set_counter}"
            changeSet.set('id', new_id)
            print(f"Updating file: {file_path} | changeSet ID: {new_id}")
            change_set_counter += 1
        
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

# Read the master file to determine the order of included files
try:
    master_tree = ET.parse(master_file)
    master_root = master_tree.getroot()
except Exception as e:
    print(f"Error reading master file: {e}")
    exit(1)

file_counter = 1
for include in master_root.findall('{http://www.liquibase.org/xml/ns/dbchangelog}include'):
    relative_file_path = include.get('file')
    file_path = os.path.join(resources_dir, relative_file_path.replace('/', os.sep))
    base_id = f"1.0.0-{file_counter}"
    
    if os.path.exists(file_path):
        print(f"Processing file: {file_path} with base ID: {base_id}")
        modify_xml(file_path, base_id)
        file_counter += 1
    else:
        print(f"File not found: {file_path}")

print('All XML files have been modified.')

```
