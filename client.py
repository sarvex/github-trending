# Entrypoint for Dash UI (renamed from client.py)
import dash
from dash import dcc, html, Input, Output, State, no_update
import dash_cytoscape as cyto
from server.services import TrendingAnalysisService
from dataclasses import asdict
import json as pyjson

# UI Constants
CYTO_HEIGHT = '900px'
CYTO_NODE_SIZE = 60
CYTO_NODE_FONT_SIZE = '10px'
CYTO_LAYOUT = {
    'name': 'grid',
    'fit': True,
    'padding': 80
}
CYTO_NODE_STYLE = {
    'label': 'data(label)',
    'background-color': '#0074D9',
    'width': CYTO_NODE_SIZE,
    'height': CYTO_NODE_SIZE,
    'font-size': CYTO_NODE_FONT_SIZE
}
CYTO_EDGE_STYLE = {
    'width': 2,
    'line-color': '#B10DC9'
}

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("GitHub Trending Graph Viewer"),
    html.Div([
        dcc.Input(
            id='language-input',
            type='text',
            placeholder='Enter programming language (e.g. python)',
            style={'width': '300px', 'marginRight': '10px'}
        ),
        html.Button('Fetch Trending Graph', id='fetch-btn', n_clicks=0),
    ], style={'marginBottom': '24px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
    dcc.Loading(
        id='loading',
        type='circle',
        children=[
            dcc.Store(id='graph-store'),
            html.Div(id='error-message', style={'color': 'red', 'marginTop': '10px'}),
            html.Div([
                html.Div([
                    html.H4("Trending Graph Visualization", style={'marginBottom': '8px'}),
                    cyto.Cytoscape(
                        id='cytoscape-graph',
                        elements=[],
                        style={'width': '100%', 'height': CYTO_HEIGHT, 'background': '#f9f9f9', 'padding': '16px', 'borderRadius': '12px'},
                        layout=CYTO_LAYOUT,
                        stylesheet=[
                            {
                                'selector': 'node',
                                'style': CYTO_NODE_STYLE
                            },
                            {
                                'selector': 'edge',
                                'style': CYTO_EDGE_STYLE
                            }
                        ]
                    )
                ], style={'flex': '1', 'padding': '12px', 'background': '#f0f4f8', 'borderRadius': '12px', 'marginRight': '16px', 'minWidth': '0'}),
                html.Div([
                    html.H4("Raw Graph JSON", style={'marginBottom': '8px'}),
                    html.Pre(id='pretty-json', style={
                        'background': '#23272e',
                        'color': '#f8f8f2',
                        'padding': '16px',
                        'borderRadius': '12px',
                        'fontSize': '13px',
                        'overflowX': 'auto',
                        'overflowY': 'auto',
                        'height': CYTO_HEIGHT,
                        'margin': 0
                    })
                ], style={'flex': '1', 'padding': '12px', 'background': '#f0f4f8', 'borderRadius': '12px', 'minWidth': '0'})
            ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '16px', 'marginTop': '16px'})
        ]
    )
], style={'padding': '32px', 'maxWidth': '1400px', 'margin': '0 auto'})

def graph_to_cytoscape_elements(graph):
    nodes = [
        {"data": {"id": node["id"], "label": node["id"].split("/")[-1] if "/" in node["id"] else node["id"]}}
        for node in graph.get("nodes", [])
    ]
    edges = []
    for edge in graph.get("edges", []):
        if edge.get("semantic_similarity") is not None and edge["semantic_similarity"] > 0.5:
            edges.append({
                "data": {
                    "source": edge["source"],
                    "target": edge["target"],
                    "weight": edge.get("weight", 1),
                    "semantic": True,
                    "similarity": round(edge["semantic_similarity"], 2)
                },
                "classes": "semantic-edge"
            })
        else:
            edges.append({
                "data": {
                    "source": edge["source"],
                    "target": edge["target"],
                    "weight": edge.get("weight", 1),
                    "semantic": False
                }
            })
    return nodes + edges

# This callback fetches the graph data by directly calling the service
@app.callback(
    Output('graph-store', 'data'),
    Output('error-message', 'children'),
    Input('fetch-btn', 'n_clicks'),
    Input('language-input', 'n_submit'),
    State('language-input', 'value'),
    prevent_initial_call=True
)
def fetch_graph(n_clicks, n_submit, language):
    # Trigger if either button is clicked or Enter is pressed
    if not language:
        return no_update, "Please enter a language."
    try:
        graph = TrendingAnalysisService.get_trending_graph(language.strip())
        return asdict(graph), ""
    except Exception as e:
        return None, f"Error: {str(e)}"

# This callback updates the graph and pretty JSON when the data in dcc.Store changes
@app.callback(
    Output('cytoscape-graph', 'elements'),
    Output('pretty-json', 'children'),
    Input('graph-store', 'data')
)
def update_graph_elements(graph):
    if not graph:
        return [], ""
    pretty_json = pyjson.dumps(graph, indent=2, ensure_ascii=False)
    elements = graph_to_cytoscape_elements(graph)
    # Error feedback for semantic analysis failures
    error_msg = ""
    if graph.get("nodes") and not graph.get("edges"):
        error_msg = "Warning: No edges were found. Semantic similarity or topic analysis may have failed."
    return elements, pretty_json if not error_msg else error_msg + "\n\n" + pretty_json


