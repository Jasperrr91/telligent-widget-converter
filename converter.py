import xml.etree.ElementTree as ET
import base64
import os, sys
import fire


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
            output = file_name.split('.')[0]

        # Create output folder
        if os.path.exists(output_folder) is False:
            os.mkdir(output_folder)

        # Start parsing the widget XML
        self._xmlRoot = tree.getroot()
        self._outputFolder = output_folder

    def decode(self):
        self.save_widget_files()

    # Decode contents of each file and save it in output folder
    def save_widget_files(self):
        for file in self._xmlRoot.findall(".//file"):
            contents_encoded = file.text
            contents = base64.b64decode(contents_encoded)

            file_name = file.get("name")
            self.write_file(file_name, contents, "wb")

    # Set correct output file and write contents to it
    def write_file(self, file_name, contents, mode="w"):
        output_file = "/".join((self._outputFolder, file_name))
        f = open(output_file, mode)
        f.write(contents)
        f.close()


# Decode XML to source files
def decode(input_file, output_folder=False):
    decoder = WidgetDecoder(input_file, output_folder)
    decoder.decode()


if __name__ == "__main__":
    fire.Fire({
        "decode": decode,
    })
