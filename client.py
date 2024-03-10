# References:
# - https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client
# - https://docs.python.org/3/library/tkinter.ttk.html#treeview
# - https://docs.python.org/3/library/xml.etree.elementtree.html

import tkinter as tk
from tkinter import ttk
import xmlrpc.client
import xml.etree.ElementTree as ET
import datetime


notes_tree = None


def validate_search_notes(note):
    try:
        # Check if input is valid XML
        root = ET.fromstring(note)

        note = root.find("note")
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


def send_note(topic_entry, title_entry, text_entry):
    print("Sending note...")

    # Get form data
    topic = topic_entry.get()
    title = title_entry.get()
    text = text_entry.get()
    timestamp = datetime.datetime.now().isoformat()

    # XML payload
    root = ET.Element("data")
    topic_element = ET.SubElement(root, "topic", {'name': topic})
    note_element = ET.SubElement(topic_element, "note", {'name': title})
    ET.SubElement(note_element, "text").text = text
    ET.SubElement(note_element, "timestamp").text = timestamp

    xml_data = ET.tostring(root, encoding="unicode")

    # XML-RPC client
    with xmlrpc.client.ServerProxy("http://localhost:5000") as proxy:
        # Send note to server
        if proxy.save_input(xml_data):
            print("Data sent successfully!")
        else:
            print("Failed to save data.")

    # Clear form fields
    topic_entry.delete(0, tk.END)
    title_entry.delete(0, tk.END)
    text_entry.delete(0, tk.END)


def search_notes(topic_entry):
    print("Searching notes...")

    # Get form data
    topic = topic_entry.get()

    # XML payload
    root = ET.Element("data")
    topic_element = ET.SubElement(root, "topic", {'name': topic})

    xml_data = ET.tostring(root, encoding="unicode")

    # XML-RPC client
    with xmlrpc.client.ServerProxy("http://localhost:5000") as proxy:
        # Search notes on server
        notes = proxy.search_notes_by_topic(xml_data)
        print("Notes found: ", notes)
        parsed_notes = []
        for note in notes:
            print(note)
            if validate_search_notes(note):
                # Parse XML
                root = ET.fromstring(note)
                title = root.find("note").get("name")
                text = root.find("note/text").text
                timestamp = root.find("note/timestamp").text

                note_obj = {
                    "title": title,
                    "text": text,
                    "timestamp": timestamp
                }

                parsed_notes.append(note_obj)

        print("Parsed notes: ", parsed_notes)
        # Add notes to Treeview
        global notes_tree
        print("Search notes, notes tree: ", notes_tree)
        if notes_tree is not None:
            notes_tree.delete(*notes_tree.get_children())
            for note in parsed_notes:
                notes_tree.insert("", "end", values=(
                    note["title"], note["text"], note["timestamp"]))

    # Clear form fields
    topic_entry.delete(0, tk.END)


def view_notes_frame(window):
    # Create frame
    view_notes_frm = tk.Frame(window)

    # Title
    title = tk.Label(view_notes_frm, text="View Notes")
    title.pack()

    # Create form fields
    topic_label = tk.Label(view_notes_frm, text="Topic: ")
    topic_label.pack()
    topic_entry = tk.Entry(view_notes_frm)
    topic_entry.pack()

    search_button = tk.Button(
        view_notes_frm, text="Search", command=lambda: search_notes(topic_entry))
    search_button.pack()

    # Found notes
    notes_label = tk.Label(view_notes_frm, text="Found Notes: ")
    notes_label.pack()

    # Create Treeview
    global notes_tree
    notes_tree = ttk.Treeview(view_notes_frm, columns=(
        "Title", "Text", "Timestamp"), show="headings")
    notes_tree.heading("Title", text="Title")
    notes_tree.heading("Text", text="Text")
    notes_tree.heading("Timestamp", text="Timestamp")
    notes_tree.pack()

    return view_notes_frm


def add_note_frame(window):
    # Create frame
    add_note_frm = tk.Frame(window)

    # Title
    title = tk.Label(add_note_frm, text="Add Note")
    title.pack()

    # Create form fields
    topic_label = tk.Label(add_note_frm, text="Topic:")
    topic_label.pack()
    topic_entry = tk.Entry(add_note_frm)
    topic_entry.pack()

    title_label = tk.Label(add_note_frm, text="Title:")
    title_label.pack()
    title_entry = tk.Entry(add_note_frm)
    title_entry.pack()

    text_label = tk.Label(add_note_frm, text="Text:")
    text_label.pack()
    text_entry = tk.Entry(add_note_frm)
    text_entry.pack()

    send_button = tk.Button(add_note_frm, text="Send", command=lambda: send_note(
        topic_entry, title_entry, text_entry))
    send_button.pack()

    return add_note_frm


def view_notes_view(add_note_frame, view_notes_frame):
    add_note_frame.pack_forget()
    view_notes_frame.pack()


def add_note_view(add_note_frame, view_notes_frame):
    view_notes_frame.pack_forget()
    add_note_frame.pack()


def main():
    # Create main window
    window = tk.Tk()
    window.title("Notebook")
    window.geometry("800x600")

    # Create frames
    view_notes_frm = view_notes_frame(window)
    add_note_frm = add_note_frame(window)

    # Create navbar
    navbar = tk.Menu(window)
    navbar.add_command(label="Add Note", command=lambda: add_note_view(
        add_note_frm, view_notes_frm))
    navbar.add_command(label="View Notes",
                       command=lambda: view_notes_view(add_note_frm, view_notes_frm))
    window.config(menu=navbar)

    # Show add note view by default
    add_note_view(add_note_frm, view_notes_frm)

    # Start the Tkinter event loop
    window.mainloop()


main()
