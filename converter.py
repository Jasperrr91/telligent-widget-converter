import xml.etree.ElementTree as ET
import base64
import os, sys

# Add ARGV
INPUT_FILE = "AchievementList-Widget.xml"

OUTPUT_DIR = INPUT_FILE.split('.')[0]

if os.path.exists(OUTPUT_DIR) is False:
    os.mkdir(OUTPUT_DIR)

tree = ET.parse(INPUT_FILE)
root = tree.getroot()

for file in root.findall(".//file"):
    contents_encoded = file.text
    contents = base64.b64decode(contents_encoded)
    file_name = file.get("name")
    output = "/".join((OUTPUT_DIR, file_name))
    f = open(output, "w")
    f.write(contents)
    f.close()
