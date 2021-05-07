"""
This module for customition of the graph
The used Collections are defined in the config

The example values are for the "World Graph" example graph of ArangoDB
"""

# Define the attributes that are used for spezific features
# reminde to use the same attribute name for evry node in evry nodecollection
# Attribute to
CATEGORY = "type"  # groupe Nodes and hide them, example uses "type" (root, continent, country, capital)
COLOR = CATEGORY  # color nodes, example uses same as to groupe
ZPOS = CATEGORY  # define position on the z-axis, example uses same as to groupe
KEY = "_key"  # find nodes in the legende, it is recomented to use _key or other attributes with unique data
LABEL = "name"  # represent nodes in the legende, example uses "name" (Africa, Asia, ...)

# Define the attributes for possibility to limit search on, example uses "type", "name" and "_id" but not "code", "_from", "_to"
# label is the text shown in the UI, value is the attribute used in ArangoDB
SEARCHOPTIONS = [
    {"label": "Type", "value": "type"},
    {"label": "Name", "value": "name"},
    {"label": "Key", "value": "_key"},
]
# Define the usable modes
# to deny using a mode, just remove it/ comment it out
# to add new modes it is nessecary to define them in the dashboard.py
# label is the text shown in the UI, value is the keyword used in the dashboard.py
MODEOPTIONS = [
    {"label": "Mark", "value": "mark"},
    {"label": "Path", "value": "path"},
    {"label": "Neighbor", "value": "neighbor"},
]
MODEDEFAULT = "mark"  # active mode while loading graph

# information that are shown when hower over a node or edge middle point
# make sure to include KEY for nodes
# it is recomended to cut or split long data, cause they will shown in one line without <br>
def info(datadict):
    text = []
    for key, data in datadict.items():
        # if not used KEY: data replace KEY in findLabel()
        if key == KEY:
            text.append(f"{KEY}: {data}")
            continue
        if key == "_rev":
            continue
        if key == "_id":
            continue
        if key == "pos":
            continue
        if key == "_key":
            if not "_from" in datadict:
                text.append(f"id: {data}")
            continue
        if key == "_from":
            text.append(f'from: {data[data.index("/")+1:]}')
            continue
        if key == "_to":
            text.append(f'to: {data[data.index("/")+1:]}')
            continue
        text.append(f"{key}: {str(data)[:20]}")
    text = "<br>".join(text)
    return text


def color(colortype):
    # rules for the color
    # color for edges and edge middle points
    if colortype == "edge":
        return "#E69F00"
    # color for the different marks
    # example color try to be visible even for color blind people
    elif colortype == "search":
        return "#D55E00"
    elif colortype == "marked":
        return "#56B4E9"
    elif colortype == "path":
        return "#CC79A7"
    # color for the nodes
    # example uses type
    elif colortype == "default":
        return "#221100"
    elif colortype == "continent":
        return "#442200"
    elif colortype == "country":
        return "#664400"
    elif colortype == "capital":
        return "#886600"
    else:
        return "#000000"


def zpos(nodetype):
    # position of the nodes on the z-axis
    # example uses type
    if nodetype == "default":
        return 1
    elif nodetype == "continent":
        return 0.75
    elif nodetype == "country":
        return 0.5
    elif nodetype == "capital":
        return 0.25
    else:
        return 0


def findLabel(text):
    # position of the KEY for the legend in the howertext
    # (defined bei info())
    try:
        text = text[text.index(KEY):] # start of 
        return text[len(KEY)+2: text.index("<br>")]
    except:
        return "notFound"
