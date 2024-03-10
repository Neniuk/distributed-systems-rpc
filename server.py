# References:
# - https://docs.python.org/3/library/xmlrpc.server.html#module-xmlrpc.server
# - https://docs.python.org/3/library/socketserver.html
# - https://docs.python.org/3/library/xml.etree.elementtree.html

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xml.etree.ElementTree as ET
from socketserver import ThreadingMixIn


class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class NotebookRequestHandler:
    def __validate_input_save__(self, input):
        try:
            # Check if input is valid XML
            root = ET.fromstring(input)

            # Check if input has the correct tags
            topic = root.find("topic")
            if topic is None:
                print("Tag not found: topic")
                return False

            note = topic.find("note")
            if note is None:
                print("Tag not found: note")
                return False

            text = note.find("text")
            if text is None:
                print("Tag not found: text")
                return False

            timestamp = note.find("timestamp")
            if timestamp is None:
                print("Tag not found: timestamp")
                return False

            print("Input is valid.")
            return True

        except ET.ParseError:
            print("Invalid XML.")
            return False

    def __validate_input_search__(self, input):
        try:
            # Check if input is valid XML
            root = ET.fromstring(input)

            # Check if input has the correct tags
            topic = root.find("topic")
            if topic is None:
                print("Tag not found: topic")
                return False

            print("Input is valid.")
            return True

        except ET.ParseError:
            print("Invalid XML.")
            return False

    def save_input(self, input):
        print("Input received: ", input)
        if self.__validate_input_save__(input):
            input = ET.fromstring(input)

            # Parse existing XML file
            try:
                tree = ET.parse("db.xml")
                root = tree.getroot()
            except ET.ParseError:
                root = ET.Element("data")

            # Check if topic with same name exists
            topic_name = input.find("topic").get("name")
            topic = root.find(f"topic[@name='{topic_name}']")
            if topic is None:
                topic = ET.SubElement(root, "topic", {"name": topic_name})

            print("Topic found: ", topic)

            # Create new note
            note_element = input.find("topic/note")
            print("Note found: ", note_element)
            note = ET.SubElement(
                topic, "note", {"name": note_element.get("name")})
            ET.SubElement(note, "text").text = note_element.find("text").text
            ET.SubElement(note, "timestamp").text = note_element.find(
                "timestamp").text

            tree = ET.ElementTree(root)
            tree.write("db.xml")

            print("Data saved successfully!")
            return True
        else:
            print("Invalid input.")
            return False

    def search_notes_by_topic(self, topic):
        print("Topic received: ", topic)
        if self.__validate_input_search__(topic):
            topic = ET.fromstring(topic).find("topic").get("name")
            print("Searching notes by topic: ", topic)

            # Parse existing XML file
            try:
                tree = ET.parse("db.xml")
                root = tree.getroot()
            except ET.ParseError:
                print("No data found.")
                return []

            # Check if topic with same name exists
            topic = root.find(f"topic[@name='{topic}']")
            if topic is None:
                print("No notes found.")
                return []

            found_notes = topic.findall("note")

            # Wrap each note in <data> tag
            found_notes_wrapped = []
            for note in found_notes:
                data = ET.Element("data")
                data.append(note)
                note = data
                # print(note)
                found_notes_wrapped.append(note)

            found_notes_wrapped = [ET.tostring(note, encoding="unicode")
                                   for note in found_notes_wrapped]
            print("Notes found: ", found_notes_wrapped)
            return found_notes_wrapped
        else:
            print("Invalid input.")
            return []


handler = NotebookRequestHandler()
# Reference: https://docs.python.org/3/library/socketserver.html
server = ThreadedXMLRPCServer(
    ("localhost", 5000), requestHandler=SimpleXMLRPCRequestHandler)
print("Server listening on port 5000")
server.register_instance(handler)
server.serve_forever()
