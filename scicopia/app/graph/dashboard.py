import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import networkx as nx
import plotly.graph_objs as go
from flask import current_app, render_template
from collections import defaultdict


def create_dashboard(server):
    dash_app = dash.Dash(
        server=server,
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    )

    nodes = []
    for collection in current_app.config["NODECOLLECTIONS"]:
        AQL = f"FOR x in {collection} RETURN [x.type, [x._id, x]]"
        nodes += current_app.config["DB"].AQLQuery(AQL, rawResults=True, batchSize=1000, ttl=3600)
        nodedict = defaultdict(list)
        for entry in nodes:
            nodedict[entry[0]].append(entry[1])

    edges = []
    for collection in current_app.config["EDGECOLLECTIONS"]:
        AQL = f"FOR x in {collection} RETURN [x._from, x._to, x]"
        edges += current_app.config["DB"].AQLQuery(AQL, rawResults=True, batchSize=1000, ttl=3600)

    legende = {}
                         
    # Create Dash Layout
    dash_app.layout = html.Div(
        className = "row",
        children=[
            html.Div(
                className = "ten columns",
                style={"maxWidth": "50vw"},
                children=[dcc.Graph(id="my-graph", figure=network_graph(nodedict, edges, legende))],
            ),
            get_checklist(legende),
            get_dropdown(legende),
            html.Div(
                className="two columns",
                children=[
                    dcc.Input(id="input", type="text", placeholder="search"),
                    html.Div(id="output"),
                    dcc.Dropdown(
                        id="drop",
                        options=[
                            {'label': 'Type', 'value': 'type'},
                            {'label': 'Name', 'value': 'name'},
                            {'label': 'ID', 'value': '_id'}
                        ],
                        value=[],
                        multi=True
                    ),
                    dcc.Checklist(
                        id='check',
                        options=[{'label':x,'value': x} for x in nodedict
                        ],
                        value=[]
                    ),
                ],
            ),
            
            html.Div([], id='previously-selected', style={'display': 'none'}),
            html.Div([], id='previously-selected2', style={'display': 'none'}),
            html.Div([], id='previously-selected3', style={'display': 'none'}),
        ]
    )
    
    init_callbacks(dash_app, nodedict, edges, legende)
    
    @server.route("/dash")
    def graph():
        return render_template('layout.html', footer=dash_app.index())

    return dash_app.server

def init_callbacks(app, nodedict, edges, legende):
    @app.callback(
        [Output('my-graph', 'figure'), Output('dropdown-container', 'children'), Output('previously-selected', 'children'), Output('previously-selected3', 'children')],
        [Input('input', 'value'), Input('drop', 'value'),Input('check', 'value'), Input('namelist', 'value')],
        [State('previously-selected', 'children'), State('previously-selected2', 'children'), State('previously-selected3', 'children')]
    )
    def update_graph(input, drop, check, value, prev_selected, prev_selected2, prev_selected3):
        if sorted(value) == sorted(prev_selected) and sorted(prev_selected) != sorted(prev_selected2) and (input, drop, check) == prev_selected3:
            raise PreventUpdate#return network_graph(nodedict, edges, legende, search = input, drop = drop, check = check, sonder = prev_selected2), get_dropdown(legende, value=prev_selected2), prev_selected2
        return network_graph(nodedict, edges, legende, search = input, drop = drop, check = check, sonder = value), get_dropdown(legende, value=value), value, (input, drop, check)
        
    @app.callback(
        Output('namelist', 'value'),
        [Input('namedrop', 'value')],
        [State('previously-selected', 'children'), State('previously-selected2', 'children')]
    )
    def display_namelist(value, prev_selected, prev_selected2):
        if sorted(value) == sorted(prev_selected) and sorted(prev_selected) != sorted(prev_selected2):
            raise PreventUpdate
        return value

    @app.callback(
        [Output('checklist-container', 'children'), Output('previously-selected2', 'children')],
        [Input('my-graph', 'clickData')],
        [State('previously-selected', 'children')]
    )
    def display_click_data(clickData, prev_selected):
        if clickData and 'text' in clickData['points'][0]:
            text = clickData['points'][0]['text']
            text = text[4:text.index("<br>")]
            if text in legende:
                id = legende[text]['id']
                if id in prev_selected:
                    prev_selected.remove(id)
                else:
                    prev_selected.append(id)
        return get_checklist(legende, value=prev_selected), prev_selected

def get_dropdown(legende, value=None):
    value = [] if value is None else value
    return html.Div(
                style={"minHeight": "400px","maxHeight": "400px", "maxWidth": "200px", "minWidth": "200px", "overflow": "auto"},
                children=[
                    dcc.Dropdown(
                        id="namedrop",
                        options=[{'label': legende[i]['name'], 'value': legende[i]['id']} for i in legende],
                        value = value,
                        multi=True
                    )
                ],
        id='dropdown-container'
    )

def get_checklist(legende, value=None):
    value = [] if value is None else value
    return html.Div(
                style={"maxHeight": "400px", "maxWidth": "200px", "overflow": "auto"},
                children=[
                    dcc.Checklist(
                        id='namelist',
                        options=[{'label': legende[i]['name'], 'value': legende[i]['id']} for i in legende],
                        value = value
                    )
                ],
        id='checklist-container'
    )

def info(datadict):
    text = []
    for key, data in datadict.items():
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
            text.append(f"from: {data[data.index('/')+1:]}")
            continue
        if key == "_to":
            text.append(f"to: {data[data.index('/')+1:]}")
            continue
        text.append(f"{key}: {data}")
    text = "<br>".join(text)
    return text

def color(nodetype): 
    # rules for the node color
    # example, dependend on type
    if nodetype == "root":
        return '#000088'
    if nodetype == "continent":
        return '#000080'
    if nodetype == "country":
        return '#888800'
    if nodetype == "capital":
        return '#008888'
    return '#000000'

def network_graph(nodedict, alledges, legende, search = "", drop = [], sonder = [], check = []):
    # add nodes from nodedict dependent of check
    nodes = []
    for type, node in nodedict.items():
        if not check or type in check:
            nodes += node

    # add nodes to graph
    G = nx.Graph()
    G.add_nodes_from(nodes)

    # add edges from alledges debendent of nodes in graph
    edges = [edge for edge in alledges if edge[0] in G.nodes and edge[1] in G.nodes]

    # add edges to graph  
    G.add_edges_from(edges)

    # calculate position with layoutfunction
    # recommended to choose kamada_kawai_layout or spring_layout
    pos = nx.layout.kamada_kawai_layout(G)
    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])

    # drawing graph
    # Create Edges

    edge_x = []
    edge_y = []
    middle_x = []
    middle_y = []
    edge_text = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
        middle_x.append((x0+x1)/2)
        middle_y.append((y0+y1)/2)
        edge_text.append(info(G.edges[edge]))

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#080'),
        hoverinfo='text',
        mode='lines')

    middle_trace = go.Scatter(
        x=middle_x, y=middle_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            color='#080',
            size=1,
            line_width=1)
    )

    node_x = []
    node_y = []
    node_text = []
    colors = []
    if search:
        search_x = []
        search_y = []
    for node in G.nodes():
        node = G.nodes[node]
        x, y = node['pos']
        node_x.append(x)
        node_y.append(y)
        node_text.append(info(node))
        colors.append(color(node['type']))
        legende[node['_key']] = {'name': node['name'], 'id': node['_id']}
        if search:
            if drop:
                for att in drop:
                    if att == "_id":
                        search = search.replace(" ", "_")
                    if search.lower() in node[att].lower():
                        search_x.append(x)
                        search_y.append(y)
                        break
            elif search.lower() in str(node).lower():
                search_x.append(x)
                search_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            color=colors,
            size=10,
            line_width=1))
            
    if search:
        search_trace = go.Scatter(
            x=search_x, y=search_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color='#800',
                size=12,
                line_width=1)
        )
    else:
        search_trace = go.Scatter(x=[], y=[])

    if sonder:
        sonder_x = []
        sonder_y = []
        for value in sonder:
            if value in G.nodes().keys():
                x, y = G.nodes[value]["pos"]
                sonder_x.append(x)
                sonder_y.append(y)
        sonder_trace = go.Scatter(
            x=sonder_x, y=sonder_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color='#080',
                size=15,
                line_width=1)
        )
    else:
        sonder_trace = go.Scatter(x=[], y=[])

    node_trace.text = node_text
    middle_trace.text = edge_text

    # Create Network Graph

    fig = go.Figure(data=[edge_trace, node_trace, middle_trace, sonder_trace, search_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig
