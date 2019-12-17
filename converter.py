import xml.etree.ElementTree as ET
import base64
import os, sys
import fire

class TelligentWidget(object):
    """A Telligent Widget XML to source file decoder/encoder"""

    def decode(self, input, output=False):
        # Check if input file exists
        if not os.path.isfile(input):
            sys.exit(f"File '{input}' does not exist.")

        # Check if input file contains valid XML
        # TODO: check if valid Telligent Widget
        try:
            tree = ET.parse(input)
        except ET.ParseError:
            exit("Invalid XML")

        # Set fallback output folder to equal the name of the widget
        if not output:
            output = input.split('.')[0]

        # Create output folder
        if os.path.exists(output) is False:
            os.mkdir(output)

        # Start parsing the widget XML
        root = tree.getroot()

        # Decode contents of each file and save it in output folder
        for file in root.findall(".//file"):
            contents_encoded = file.text
            contents = base64.b64decode(contents_encoded)

            file_name = file.get("name")
            output = "/".join((output, file_name))

            f = open(output, "wb")
            f.write(contents)
            f.close()


if __name__ == '__main__':
    fire.Fire(TelligentWidget)
