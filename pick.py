# Server picker
# Originally written for Windows, modified to run in linux, only really tested in Debian 12.

# You may need to install tk if you get an error, on debian systems this can be done by running
# sudo apt install python3-tk

import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import csv
import subprocess
import os
import sys

# Server data available at:
# TODO: Work on this so path can be relative to the script or absolute.
csv_file = "servers.csv"

def load_header():
    o = []
    with open(csv_file, newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=',', quotechar='"')

        # get all data
        for row in data:
            for col in row:
                o.append(col)

            break
    return o

def load_data():
    x = []
    o = []
    with open(csv_file, newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=',', quotechar='"')

        is_header = True
        for row in data:
            if is_header:
                is_header = False
                continue
            else:
                for col in row:
                    x.append(col)
                o.append(tuple(x)) # outputting a list where each row is a tuple
                x = []

    return o
    
def get_index_by_name(name):
    """Get the index of a column by its name."""
    try:
        return csv_header.index(name)
    except ValueError:
        return -1
 
def go(event):
    tree = event.widget
    curItem = tree.focus()
    d = tree.item(curItem) # selected row data json
    print(csv_header)

    # grab the items we need from the selected row
    # user,ip,platform

    user = d["values"][get_index_by_name('user')]
    ip = d["values"][get_index_by_name('ip')]
    platform = d["values"][get_index_by_name('platform')]

    print("Connecting to " + platform + " server " + ip + " as " + user + "... ")
    if (platform == "linux"):
        cmd = [
            "ssh", "-A", user + "@" + ip
        ]
        print(cmd)
        # This hides the window, it gets destroyed when we disconnect from the server.
        # There's probaby a way to completely exit this script and still connect, but this works pretty well.
        root.withdraw()
    else:
        # Windows
        cmd = [
            "mstsc", "/v:" + ip, "/prompt"
        ]

    subprocess.call(cmd)
    exit()

def searchCallback(sv):
    searchString = sv.get()
    # searchString holds the text in the search bar here
    # need to find some way to scan through all the data and only include rows in the results
    # that have the searchString value as a substring
    csv_list = [] 
    sp._build_tree(searchString) # calling _build_tree() on the server picker class will reload it

# Launch the data source csv file in the systems default editor
def editFileCallback():
    if sys.platform == "win32":
        os.startfile(csv_file)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, csv_file])

# If user hits escape key exit
def esc(event):
    if (event.keysym == 'Escape'):
        quit()

def focusNextWidget(event):
    event.widget.tk_focusNext().focus()
    return("break")

class ServerPicker(object):
    """use a ttk.TreeView as a multicolumn ListBox"""
    def __init__(self):
        self.tree = None
        self._setup_widgets()
        self._build_tree('')

    def _setup_widgets(self):

        sv = tk.StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: searchCallback(sv))

        search_box = tk.Entry(root, textvariable=sv)
        search_box.pack(pady='8', padx='8', fill='both', anchor='w')

        #search_box.bind("<Tab>", focusNextWidget)
        search_box.focus_set()

        container = ttk.Frame()
        container.pack(fill='both', expand=True)

        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(columns=csv_header, show="headings")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Calibri', 11))
        style.configure("Treeview", font=('Calibri', 11))

        style.configure("Button", font=('Calibri', 11))
        edit_button = tk.Button(root, text = "Edit Servers List", command = editFileCallback, justify="right")
        edit_button.pack(pady='8', padx='8', anchor="w")

        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)

        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)

        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        #self.tree.bind("<<TreeviewSelect>>", go)
        self.tree.bind('<Double-1>', go)
        self.tree.bind('<Return>', go)

    def _build_tree(self, searchString):

        for col in csv_header:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title()))

        # Filter the results to only those containing the searchString value
        # Note we have to clear the grid before dumping the csv_list_filtered
        # values into it.
        csv_list_filtered = []
        for row in csv_list:
            for col in row:
                if searchString.lower() in col.lower():
                    csv_list_filtered.append(row)
                    break

        for row in self.tree.get_children():
            self.tree.delete(row)

        for item in csv_list_filtered:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)+4
                if self.tree.column(csv_header[ix],width=None)<col_w:
                    self.tree.column(csv_header[ix], width=col_w)

        # This gets all rows in tree, if any exist it sets focus to the first one.
        # You can't see that until you use the arrow keys to move up and down, but it's selected.
        # This was the last piece to complete navigation by keyboard only
        c = self.tree.get_children()
        if len(c) > 0:
            self.tree.focus(c[0])

def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) \
        for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, \
        int(not descending)))


# Load data this code needs
csv_header = load_header()
csv_list = load_data()

print("Pick a server from the popup to connect...")

root = tk.Tk()
root.geometry("1200x800")
root.wm_title("Server Picker")
root.bind("<KeyRelease>", esc)
sp = ServerPicker()
root.mainloop()

