import logging
from collections import defaultdict

import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask import current_app, render_template, session, g

import scicopia.app.graph.customize as c


def create_dashboard(server):
    dash_app = dash.Dash(server=server, routes_pathname_prefix="/dash/")
    error = False

    nodes = []
    nodedict = defaultdict(list)
    edges = []
    try:
        for collection in current_app.config["NODECOLLECTIONS"]:
            AQL = f'FOR x in {collection} RETURN [x["{c.CATEGORY}"], [x._id, x]]'
            nodes += current_app.config["DB"].AQLQuery(
                AQL, rawResults=True, batchSize=1000, ttl=3600
            )
            for entry in nodes:
                nodedict[entry[0]].append(entry[1])

        for collection in current_app.config["EDGECOLLECTIONS"]:
            AQL = f"FOR x in {collection} RETURN [x._from, x._to, x]"
            edges += current_app.config["DB"].AQLQuery(
                AQL, rawResults=True, batchSize=1000, ttl=3600
            )
    except:
        error = True

    if error:
        logging.error(
            "An Error occurred while loading the Graphdata. Maybe the defined Collections don't exist."
        )
        dash_app.layout = html.Div(children=html.H1(children="Graph Not Found"))

        @server.route("/graph")
        def graph():
            return render_template("nograph.html")

        return dash_app.server

    legende = {}

    # Create Dash Layout
    dash_app.layout = html.Div()

    init_callbacks(dash_app, nodedict, edges, legende)

    @server.route("/graph")
    def graph():
        # {"mode":mode, "searchfield":searchfield,"searchdropdown":searchdropdown,"marked":marked,"categories":categories}
        if "graph" in session:
            mode = session["graph"]["mode"]
            marked = session["graph"]["marked"]
            searchfield = session["graph"]["searchfield"]
            searchdropdown = session["graph"]["searchdropdown"]
            categories = session["graph"]["categories"]
        else:
            mode = c.MODEDEFAULT
            marked = []
            searchfield = ""
            searchdropdown = []
            categories = []
        dash_app.layout = html.Div(
            children=[
                html.Div(
                    className = 'six columns',
                    children=[dcc.Graph(id='graph', figure=network_graph(nodedict, edges, legende, 'mark'), style={'height':'100%'})],
                ),
                html.Div(
                    className='two columns',
                    children=[get_checklist(legende)]
                ),
                html.Div(
                    className='two columns',
                    children=[get_dropdown(legende, marked)]
                ),
                html.Div(
                    className='two columns',
                    
                    children=[
                        dcc.Input(id='searchfield', type='search', placeholder='search', style={'minWidth':'100%', 'maxWidth':'100%'},value=searchfield),
                        dcc.Dropdown(
                            id='searchdropdown',
                            options= c.SEARCHOPTIONS,
                            value=searchdropdown,
                            multi=True
                        ),
                        dcc.Checklist(
                            id='categories',
                            options=[{'label':x,'value': x} for x in nodedict
                            ],
                            value=categories
                        ),
                        dcc.RadioItems(
                            id='mode',
                            options= c.MODEOPTIONS,
                            value = mode
                        ),
                    ],
                ),
                
                html.Div(marked, id='previously-selected', style={'display': 'none'}),
                html.Div([], id='previously-selected2', style={'display': 'none'}),
                html.Div([], id='previously-selected3', style={'display': 'none'}),
            ]
        )
        return render_template('layout.html', footer=dash_app.index())

    return dash_app.server


def init_callbacks(app, nodedict, edges, legende):
    # no solution to update namecheck in neighbormode
    @app.callback(
        [Output('graph', 'figure'), Output('dropdown-container', 'children'), Output('previously-selected', 'children'), Output('previously-selected3', 'children')],
        [Input('searchfield', 'value'), Input('searchdropdown', 'value'), Input('categories', 'value'), Input('namecheck', 'value'), Input('mode', 'value')],
        [State('previously-selected', 'children'), State('previously-selected2', 'children'), State('previously-selected3', 'children')]
    )
    def update_graph(searchfield, searchdropdown, categories, marked, mode, prev_selected, prev_selected2, prev_selected3):
        if mode == 'neighbor' and len(marked) > 1:
            marked = [marked[-1]]
        if sorted(marked) == sorted(prev_selected) and sorted(prev_selected) != sorted(prev_selected2) and (searchfield, searchdropdown, categories) == prev_selected3:
            raise PreventUpdate
        return network_graph(nodedict, edges, legende, mode, marked = marked, searchfield = searchfield, searchdropdown = searchdropdown, categories = categories), get_dropdown(legende, marked=marked), marked, (searchfield, searchdropdown, categories)
        
    @app.callback(
        Output("namecheck", "value"),
        [Input("namedrop", "value")],
        [
            State("previously-selected", "children"),
            State("previously-selected2", "children"),
        ],
    )
    def display_namecheck(marked, prev_selected, prev_selected2):
        if sorted(marked) == sorted(prev_selected) and sorted(prev_selected) != sorted(prev_selected2):
            raise PreventUpdate
        return marked

    @app.callback(
        [Output('checklist-container', 'children'), Output('previously-selected2', 'children')],
        [Input('graph', 'clickData')],
        [State('previously-selected', 'children')]
    )
    def display_click_data(clickData, prev_selected):
        if clickData and "text" in clickData["points"][0]:
            text = clickData["points"][0]["text"]
            text = c.findLabel(text)
            if text in legende:
                id = legende[text]["id"]
                if id in prev_selected:
                    prev_selected.remove(id)
                else:
                    prev_selected.append(id)
        return get_checklist(legende, marked=prev_selected), prev_selected

def get_dropdown(legende, marked=None):
    marked = [] if marked is None else marked
    return html.Div(
                style={'minHeight': '50vh', 'maxHeight': 'calc(100vh - 150px)', 'overflow': 'auto'},
                children=[
                    dcc.Dropdown(
                        id='namedrop',
                        options=[{'label': legende[i]['name'], 'value': legende[i]['id']} for i in legende],
                        value = marked,
                        multi=True
                    )
                ],
                value=value,
                multi=True,
            )
        ],
        id="dropdown-container",
    )

def get_checklist(legende, marked=None):
    marked = [] if marked is None else marked
    return html.Div(
                style={'maxHeight': 'calc(100vh - 150px)', 'overflow': 'auto'},
                children=[
                    dcc.Checklist(
                        id='namecheck',
                        options=[{'label': legende[i]['name'], 'value': legende[i]['id']} for i in legende],
                        value = marked
                    )
                ],
                value=value,
            )
        ],
        id="checklist-container",
    )

def network_graph(nodedict, alledges, legende, mode, marked = [], searchfield = '', searchdropdown = [], categories = []):
    # add nodes from nodedict dependent of categories
    nodes = []
    for type, node in nodedict.items():
        if not categories or type in categories:
            nodes += node

    # add nodes to graph
    G = nx.Graph()
    G.add_nodes_from(nodes)

    # add edges from alledges debendent of nodes in graph
    edges = [edge for edge in alledges if edge[0] in G.nodes and edge[1] in G.nodes]

    # add edges to graph
    G.add_edges_from(edges)

    if mode == "neighbor":
        # reduce graph to neighborhood of last entry of marked
        if len(marked) >= 1:
            try:
                neighbors = {n for n in G.neighbors(marked[-1])}
                for n in neighbors:
                    neighbors = neighbors.union({n for n in G.neighbors(n)})
                neighbors.add(marked[-1]) # possibility of no neighbors
                nodes = [(node, G.nodes[node]) for node in neighbors]
                G.clear()
                G.add_nodes_from(nodes)
                edges = [
                    edge
                    for edge in alledges
                    if edge[0] in G.nodes and edge[1] in G.nodes
                ]
                G.add_edges_from(edges)
            except:
                pass

    # calculate position with layoutfunction
    # recommended to choose kamada_kawai_layout or spring_layout
    pos = nx.layout.spring_layout(G)
    for node in G.nodes:
        G.nodes[node]["pos"] = list(pos[node])
        G.nodes[node]["pos"].append(c.zpos(G.nodes[node][c.ZPOS]))

    path_node_trace = go.Scatter3d(x=[], y=[], z=[])
    path_edge_trace = go.Scatter3d(x=[], y=[], z=[])
    if mode == "path":
        # calculate path between last 2 entrys of marked
        if len(marked) >= 2:
            try:
                path = nx.shortest_path(G, source=marked[-2], target=marked[-1])
                path_node_x = []
                path_node_y = []
                path_node_z = []
                for node in path:
                    x, y, z = G.nodes[node]["pos"]
                    path_node_x.append(x)
                    path_node_y.append(y)
                    path_node_z.append(z)

                path_node_trace = go.Scatter3d(
                    x=path_node_x,
                    y=path_node_y,
                    z=path_node_z,
                    mode="markers",
                    hoverinfo="text",
                    marker=dict(color=c.color("path"), size=12, line_width=1),
                )
                path_edge_trace = go.Scatter3d(
                    x=path_node_x,
                    y=path_node_y,
                    z=path_node_z,
                    line=dict(width=1, color=c.color("path")),
                    hoverinfo="text",
                    mode="lines",
                )
            except:
                pass

    # drawing graph
    # Create Edges

    edge_x = []
    edge_y = []
    edge_z = []
    middle_x = []
    middle_y = []
    middle_z = []
    edge_text = []
    for edge in G.edges():
        x0, y0, z0 = G.nodes[edge[0]]["pos"]
        x1, y1, z1 = G.nodes[edge[1]]["pos"]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
        edge_z.append(z0)
        edge_z.append(z1)
        edge_z.append(None)
        middle_x.append((x0 + x1) / 2)
        middle_y.append((y0 + y1) / 2)
        middle_z.append((z0 + z1) / 2)
        edge_text.append(c.info(G.edges[edge]))

    edge_trace = go.Scatter3d(
        x=edge_x,
        y=edge_y,
        z=edge_z,
        line=dict(width=1, color=c.color("edge")),
        hoverinfo="text",
        mode="lines",
    )

    middle_trace = go.Scatter3d(
        x=middle_x,
        y=middle_y,
        z=middle_z,
        mode="markers",
        hoverinfo="text",
        marker=dict(color=c.color("edge"), size=1, line_width=1),
    )

    node_x = []
    node_y = []
    node_z = []
    node_text = []
    colors = []
    if searchfield:
        search_x = []
        search_y = []
        search_z = []
    for node in G.nodes():
        node = G.nodes[node]
        x, y, z = node["pos"]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_text.append(c.info(node))
        colors.append(c.color(node[c.COLOR]))
        legende[node[c.KEY]] = {'name': node[c.LABEL], 'id': node['_id']}
        if searchfield:
            if searchdropdown:
                for att in searchdropdown:
                    if att == '_id':
                        searchfield = searchfield.replace(' ', '_')
                    if searchfield.lower() in node[att].lower():
                        search_x.append(x)
                        search_y.append(y)
                        search_z.append(z)
                        break
            elif searchfield.lower() in str(node).lower():
                search_x.append(x)
                search_y.append(y)
                search_z.append(z)

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            color=colors,
            size=10,
            line_width=1))
            
    if searchfield:
        search_trace = go.Scatter3d(
            x=search_x,
            y=search_y,
            z=search_z,
            mode="markers",
            hoverinfo="text",
            marker=dict(color=c.color("search"), size=12, line_width=1),
        )
    else:
        search_trace = go.Scatter3d(x=[], y=[], z=[])

    if marked:
        marked_x = []
        marked_y = []
        marked_z = []
        for value in marked:
            if value in G.nodes().keys():
                x, y, z = G.nodes[value]["pos"]
                marked_x.append(x)
                marked_y.append(y)
                marked_z.append(z)
        marked_trace = go.Scatter3d(
            x=marked_x,
            y=marked_y,
            z=marked_z,
            mode="markers",
            hoverinfo="text",
            marker=dict(color=c.color("marked"), size=15, line_width=1),
        )
    else:
        marked_trace = go.Scatter3d(x=[], y=[], z=[])

    node_trace.text = node_text
    middle_trace.text = edge_text

    # Create Network Graph

    fig = go.Figure(data=[edge_trace, node_trace, middle_trace, marked_trace, path_node_trace, path_edge_trace, search_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    session["graph"] = {"mode":mode, "searchfield":searchfield,"searchdropdown":searchdropdown,"marked":marked,"categories":categories}
    return fig
