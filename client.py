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
wiki_tree = None


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


def validate_search_wiki(result):
    try:
        # Check if input is valid XML
        root = ET.fromstring(result)

        url = root.find("url")
        if url is None:
            print("Tag not found: url")
            return False

        text = root.find("text")
        if text is None:
            print("Tag not found: text")
            return False

        print("Input is valid.")
        return True

    except ET.ParseError:
        print("Invalid XML.")
        return False


def send_note(topic_entry, title_entry, text_entry):
    print("Sending note...")

    # Get form data
    if isinstance(title_entry, tk.Entry):
        title = title_entry.get()
    elif isinstance(title_entry, str):
        title = title_entry

    if isinstance(text_entry, tk.Entry):
        text = text_entry.get()
    elif isinstance(text_entry, str):
        text = text_entry

    if isinstance(topic_entry, tk.Entry):
        topic = topic_entry.get()
    elif isinstance(topic_entry, str):
        topic = topic_entry

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

    # Clear form fields if they are Entry widgets
    if isinstance(topic_entry, tk.Entry):
        topic_entry.delete(0, tk.END)
    if isinstance(title_entry, tk.Entry):
        title_entry.delete(0, tk.END)
    if isinstance(text_entry, tk.Entry):
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


def search_wiki(search_entry):
    # Get form data
    search = search_entry.get()

    # XML payload
    root = ET.Element("data")
    ET.SubElement(root, "query").text = search

    xml_data = ET.tostring(root, encoding="unicode")

    # XML-RPC client
    with xmlrpc.client.ServerProxy("http://localhost:5000") as proxy:
        # Search Wikipedia on server
        result = proxy.search_wikipedia(xml_data)
        print("Wikipedia result:", result)
        if validate_search_wiki(result):
            # Parse XML
            root = ET.fromstring(result)
            url = root.find("url").text
            text = root.find("text").text

            wiki_obj = {
                "url": url,
                "text": text
            }

            # Add Wikipedia result to Treeview
            global wiki_tree
            if wiki_tree is not None:
                wiki_tree.delete(*wiki_tree.get_children())
                wiki_tree.insert("", "end", values=(
                    wiki_obj["url"], wiki_obj["text"]))

    # Clear form fields
    search_entry.delete(0, tk.END)


def add_to_topic_window(title, url, window):
    # Create new window
    new_window = tk.Toplevel(window)
    new_window.title("Add To Topic")
    new_window.geometry("200x100")

    # Create form fields
    topic_label = tk.Label(new_window, text="Topic: ")
    topic_label.pack()
    topic_entry = tk.Entry(new_window)
    topic_entry.pack()

    add_button = tk.Button(new_window, text="Add",
                           command=lambda: send_note(topic_entry, title, url))
    add_button.pack()


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


def search_wiki_frame(window):
    # Create frame
    search_wiki_frm = tk.Frame(window)

    # Title
    title = tk.Label(search_wiki_frm, text="Search Wikipedia")
    title.pack()

    # Create form fields
    search_label = tk.Label(search_wiki_frm, text="Search:")
    search_label.pack()
    search_entry = tk.Entry(search_wiki_frm)
    search_entry.pack()

    search_button = tk.Button(
        search_wiki_frm, text="Search", command=lambda: search_wiki(search_entry))
    search_button.pack()

    # Found articles
    articles_label = tk.Label(search_wiki_frm, text="Found Articles: ")
    articles_label.pack()

    # Create Treeview
    global wiki_tree
    wiki_tree = ttk.Treeview(search_wiki_frm, columns=(
        "URL", "Description", "Add To Notes Topic"), show="headings")
    wiki_tree.heading("URL", text="URL")
    wiki_tree.heading("Description", text="Description")
    wiki_tree.heading("Add To Notes Topic", text="Add To Notes Topic")
    wiki_tree.column("URL", width=300)
    wiki_tree.column("Description", width=200)
    wiki_tree.column("Add To Notes Topic", width=100)
    wiki_tree.pack()

    # Create button
    button = tk.Button(search_wiki_frm, text="Add To Notes Topic", command=lambda: add_to_topic_window(
        wiki_tree.item(wiki_tree.selection())[
            "values"][1] if wiki_tree.selection() else "",
        wiki_tree.item(wiki_tree.selection())[
            "values"][0] if wiki_tree.selection() else "",
        window))
    button.pack()

    return search_wiki_frm


def view_notes_view(add_note_frame, view_notes_frame, search_wiki_frame):
    add_note_frame.pack_forget()
    search_wiki_frame.pack_forget()
    view_notes_frame.pack()


def add_note_view(add_note_frame, view_notes_frame, search_wiki_frame):
    view_notes_frame.pack_forget()
    search_wiki_frame.pack_forget()
    add_note_frame.pack()


def search_wiki_view(search_wiki_frame, view_notes_frame, add_note_frame):
    view_notes_frame.pack_forget()
    add_note_frame.pack_forget()
    search_wiki_frame.pack()


def main():
    # Create main window
    window = tk.Tk()
    window.title("Notebook")
    window.geometry("800x600")

    # Create frames
    view_notes_frm = view_notes_frame(window)
    add_note_frm = add_note_frame(window)
    search_wiki_frm = search_wiki_frame(window)

    # Create navbar
    navbar = tk.Menu(window)
    navbar.add_command(label="Add Note", command=lambda: add_note_view(
        add_note_frm, view_notes_frm, search_wiki_frm))
    navbar.add_command(label="View Notes",
                       command=lambda: view_notes_view(add_note_frm, view_notes_frm, search_wiki_frm))
    navbar.add_command(label="Search Wikipedia",
                       command=lambda: search_wiki_view(search_wiki_frm, view_notes_frm, add_note_frm))
    window.config(menu=navbar)

    # Show add note view by default
    add_note_view(add_note_frm, view_notes_frm, search_wiki_frm)

    # Start the Tkinter event loop
    window.mainloop()


main()
