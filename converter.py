import base64
import json
import os
import sys
import fire
from lxml import etree as ET

class WidgetDecoder(object):
    def __init__(self, file_name, output_folder=False):
        # Check if input file exists
        if not os.path.isfile(file_name):
            sys.exit(f"File '{file_name}' does not exist.")

        # Check if input file contains valid XML
        # TODO: check if valid Telligent Widget
        try:
            tree = ET.parse(file_name)
        except ET.ParseError:
            exit("Invalid XML")

        # Set fallback output folder to equal the name of the widget
        if not output_folder:
            output_folder = file_name.split('.')[0]

        # Create output folder
        if os.path.exists(output_folder) is False:
            os.mkdir(output_folder)

        # Start parsing the widget XML
        self._xmlRoot = tree.getroot()
        self._outputFolder = output_folder

    def decode(self):
        self.save_content_script_attributes()
        self.save_widget_header_script()
        self.save_widget_content_script()
        self.save_widget_configuration()
        self.save_widget_language_resources()
        self.save_widget_files()

    def save_content_script_attributes(self):
        scripted_content_node = self._xmlRoot.find(".//scriptedContentFragment")

        data = {}
        for attribute, value in scripted_content_node.attrib.items():
            data[attribute] = value

        json_data = json.dumps(data, indent=4, separators=(',', ': '))
        self.write_file("content_script_attributes.json", json_data)

    # Decode contents of each file and save it in output folder
    def save_widget_files(self):
        for file in self._xmlRoot.findall(".//file"):
            contents_encoded = file.text
            contents = base64.b64decode(contents_encoded)

            file_name = file.get("name")
            self.write_file(file_name, contents, "wb")

    def save_widget_header_script(self):
        header_script = self._xmlRoot.find(".//headerScript").text
        file_name = "headerScript.vm"
        self.write_file(file_name, header_script)

    def save_widget_content_script(self):
        content_script = self._xmlRoot.find(".//contentScript").text
        file_name = "contentScript.vm"
        self.write_file(file_name, content_script)

    def save_widget_configuration(self):
        content_script = self._xmlRoot.find(".//configuration").text
        file_name = "configuration.xml"
        self.write_file(file_name, content_script)

    def save_widget_language_resources(self):
        content_script = self._xmlRoot.find(".//languageResources").text
        file_name = "languageResources.xml"
        self.write_file(file_name, content_script)

    # Set correct output file and write contents to it
    def write_file(self, file_name, contents, mode="w"):
        output_file = "/".join((self._outputFolder, file_name))
        f = open(output_file, mode)
        f.write(contents)
        f.close()


class WidgetEncoder(object):
    def __init__(self, input_folder, output_file=False):
        # Check if input folder exists
        if os.path.exists(input_folder) is False:
            sys.exit(f"Folder '{input_folder}' does not exist.")

        if not output_file:
            output_file = ".".join((input_folder, "xml"))

        self._input_folder = input_folder
        self._output_file = output_file
        self._root = ET.Element("scriptedContentFragments")
        self._root.tail = "\n"
        self._first_child = ET.SubElement(self._root, "scriptedContentFragment")
        self._first_child.tail = "\n"

    def encode(self):
        self.add_scripted_content_attributes()
        self.add_content_script()
        self.add_header_script()
        self.add_configuration()
        self.add_language_resources()
        self.add_additional_css_script()
        self.add_files()

        for element in self._root.iter():
            element.tail = None
        self.write_file(self._output_file, ET.tostring(self._root, pretty_print=True), 'wb')

    def add_scripted_content_attributes(self):
        content_script_attributes = "/".join((self._input_folder, "content_script_attributes.json"))
        with open(content_script_attributes) as json_file:
            data = json.load(json_file)
            for key, value in data.items():
                self._first_child.set(key, value)

    def add_content_script(self):
        child = ET.SubElement(self._first_child, "contentScript")
        child.set("language", "Velocity")

        content_script = "/".join((self._input_folder, "contentScript.vm"))
        f = open(content_script, "r")
        child.text = ET.CDATA(f.read())
        f.close()

    def add_header_script(self):
        child = ET.SubElement(self._first_child, "headerScript")
        child.set("language", "Velocity")

        content_script = "/".join((self._input_folder, "headerScript.vm"))
        f = open(content_script, "r")
        child.text = ET.CDATA(f.read())
        f.close()

    def add_configuration(self):
        child = ET.SubElement(self._first_child, "configuration")

        content_script = "/".join((self._input_folder, "configuration.xml"))
        f = open(content_script, "r")
        child.text = ET.CDATA(f.read())
        f.close()

    def add_language_resources(self):
        child = ET.SubElement(self._first_child, "languageResources")

        content_script = "/".join((self._input_folder, "languageResources.xml"))
        f = open(content_script, "r")
        child.text = ET.CDATA(f.read())
        f.close()

    def add_additional_css_script(self):
        child = ET.SubElement(self._first_child, "additionalCssScript")
        child.set("language", "Unknown")

    def add_files(self):
        child = ET.SubElement(self._first_child, "files")

        exclude = [
            "headerScript.vm",
            "contentScript.vm",
            "configuration.xml",
            "languageResources.xml",
            "content_script_attributes.json"
        ]

        for file_name in os.listdir(self._input_folder):
            if file_name not in exclude:
                file = ET.SubElement(child, "file")
                file_name_full = "/".join((self._input_folder, file_name))
                f = open(file_name_full, "rb")
                file.set("name", file_name)
                file.text = base64.b64encode(f.read())
                f.close()

    # Set correct output file and write contents to it
    def write_file(self, file_name, contents, mode="w"):
        f = open(file_name, mode)
        f.write(contents)
        f.close()


# Decode XML to source files
def decode(input_file, output_folder=False):
    decoder = WidgetDecoder(input_file, output_folder)
    decoder.decode()


# Encode source folder to XML
def encode(input_folder, output_file=False):
    encoder = WidgetEncoder(input_folder, output_file)
    encoder.encode()


if __name__ == "__main__":
    fire.Fire({
        "decode": decode,
        "encode": encode,
    })
