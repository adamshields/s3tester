import xml.etree.ElementTree as ET
import os

def write_changelog(file_path, root_element):
    # Remove the namespace prefixes
    for elem in root_element.iter():
        elem.tag = elem.tag.replace("{http://www.liquibase.org/xml/ns/dbchangelog}", "")
        for key, value in elem.attrib.items():
            if key.startswith("{http://www.liquibase.org/xml/ns/dbchangelog}"):
                new_key = key.replace("{http://www.liquibase.org/xml/ns/dbchangelog}", "")
                elem.attrib[new_key] = value
                del elem.attrib[key]

    # Create a new XML tree
    tree = ET.ElementTree(root_element)
    # Write the XML to the file
    tree.write(file_path, encoding="utf-8", xml_declaration=True)
    print(f"Created {file_path}")

def split_changelog_by_table(input_file):
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
        namespace = {"ns": "http://www.liquibase.org/xml/ns/dbchangelog"}

        # Ensure output directory exists
        output_dir = "output_tables"
        os.makedirs(output_dir, exist_ok=True)

        table_change_sets = {}

        for changeSet in root.findall('ns:changeSet', namespace):
            for change in changeSet:
                table_name = None
                if change.tag == f"{{{namespace['ns']}}}createTable":
                    table_name = change.get('tableName')
                elif change.tag == f"{{{namespace['ns']}}}addForeignKeyConstraint":
                    table_name = change.get('baseTableName')
                elif change.tag == f"{{{namespace['ns']}}}addUniqueConstraint":
                    table_name = change.get('tableName')

                if table_name:
                    if table_name not in table_change_sets:
                        table_change_sets[table_name] = ET.Element("databaseChangeLog", xmlns="http://www.liquibase.org/xml/ns/dbchangelog",
                                                                   attrib={
                                                                       "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                                                       "xsi:schemaLocation": "http://www.liquibase.org/xml/ns/dbchangelog http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd"
                                                                   })
                    # Append the current changeSet to the respective table's root
                    table_change_sets[table_name].append(changeSet)

        # Write out each table's changeSets to their own file
        for table_name, table_root in table_change_sets.items():
            output_file = os.path.join(output_dir, f"{table_name}.xml")
            write_changelog(output_file, table_root)

        # Create the master changelog
        master_changelog = ET.Element("databaseChangeLog", xmlns="http://www.liquibase.org/xml/ns/dbchangelog",
                                      attrib={
                                          "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                          "xsi:schemaLocation": "http://www.liquibase.org/xml/ns/dbchangelog http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd"
                                      })

        for table_name in table_change_sets.keys():
            ET.SubElement(master_changelog, "include", file=f"{table_name}.xml")

        output_file = os.path.join(output_dir, "db.changelog-master.xml")
        write_changelog(output_file, master_changelog)

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_file = "changelog.xml"
    split_changelog_by_table(input_file)
