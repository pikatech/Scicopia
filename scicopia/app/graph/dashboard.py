import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go
from flask import current_app, render_template
from bs4 import BeautifulSoup


def create_dashboard(server):
    dash_app = dash.Dash(
        server=server
    )

    nodes = []
    for collection in current_app.config["NODECOLLECTIONS"]:
        AQL = f"FOR x in {collection} RETURN [x._id, x]"
        nodes += current_app.config["DB"].AQLQuery(AQL, rawResults=True, batchSize=1000, ttl=3600)

    edges = []
    for collection in current_app.config["EDGECOLLECTIONS"]:
        AQL = f"FOR x in {collection} RETURN [x._from, x._to, x]"
        edges += current_app.config["DB"].AQLQuery(AQL, rawResults=True, batchSize=1000, ttl=3600)

    legende = {'None': 'None'}
                         
    # Create Dash Layout
    dash_app.layout = html.Div(
        children=[
            html.Div(
                style={"maxWidth": "50vw"},
                children=[dcc.Graph(id="my-graph", figure=network_graph(nodes, edges, legende))],
            ),
            html.Div(
                style={"maxHeight": "400px", "maxWidth": "200px", "overflow": "auto"},
                children=[
                    dcc.RadioItems(
                        id='namelist',
                        options=[{'label': i, 'value': i} for i in legende],
                        value = 'None'
                    )
                ]
            )
        ]
    )
    
    init_callbacks(dash_app, nodes, edges, legende)
    
    @server.route("/dash")
    def graph():
        soup = BeautifulSoup(dash_app.index(), 'html.parser')
        footer = soup.footer
        return render_template('layout.html', footer=footer)

    return dash_app.server

def init_callbacks(app, nodes, edges, legende):
    @app.callback(
        dash.dependencies.Output('my-graph', 'figure'),
        [dash.dependencies.Input('namelist', 'value')]
    )
    def update_graph(value):
        if value != 'None':
            sonder = {"pos": legende[value]["pos"]}
        else:
            sonder = None
        return network_graph(nodes, edges, legende, sonder)
        
    @app.callback(
        dash.dependencies.Output('namelist', 'value'),
        [dash.dependencies.Input('my-graph', 'clickData')])
    def display_click_data(clickData):
        if clickData:
            text = clickData['points'][0]['text']
            text = text[4:text.index("<br>")]
            if text in legende:
                return text
        return "None"

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

def network_graph(nodes, edges, legende, sonder = None):


    # füge die daten Graph hinzu
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    # erstelle positionen und füge sie knoten hinzu
    pos = nx.layout.kamada_kawai_layout(G) # choose kamada_kawai_layout or spring_layout
    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])

    # zeichne graph
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
    for node in G.nodes():
        node = G.nodes[node]
        x, y = node['pos']
        node_x.append(x)
        node_y.append(y)
        node_text.append(info(node))
        legende[node["_key"]] = {'name': f'{node["name"]}', 'pos': (x, y)}

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Greens',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))
            
    if sonder:
        sonder_trace = go.Scatter(
            x=[sonder['pos'][0]], y=[sonder['pos'][1]],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color='#800',
                size=12,
                line_width=1)
        )
    else:
        sonder_trace = go.Scatter(x=[], y=[])
    # Color Node Points

    node_adjacencies = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text
    middle_trace.text = edge_text

    # Create Network Graph

    fig = go.Figure(data=[edge_trace, node_trace, middle_trace, sonder_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig
