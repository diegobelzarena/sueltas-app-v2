import plotly.graph_objects as go
from dash import dcc, html

def setup_layout(ctx_obj):
    """Compose the dashboard layout from sub-method components."""
    # Load cached UMAP positions, computing via umap-learn if missing
    umap_pos = ctx_obj.umap_positions["combined"]
    umap_pos_list = umap_pos.tolist()
    print("UMAP positions loaded (if cached), figures will be created on first render")

    # Empty placeholder figures (actual content created on first callback)
    initial_network_fig = go.Figure()
    initial_heatmap_fig = go.Figure()
    # initial_dendro_fig = go.Figure()

    return html.Div([
        build_page_header(),
        build_font_selector(),
        *build_data_stores(umap_pos_list),
        build_heatmap_and_comparison(initial_heatmap_fig),
        build_network_section(initial_network_fig),
        # build_dendrogram_section(initial_dendro_fig),
        # build_export_section(),
        # dcc.Download(id="download-html"),
    ])


def build_page_header():
    """Page title and subtitle."""
    return html.Div([
        html.H1("Theatre Chapbooks At Scale",
                    style={'textAlign': 'center', 'margin': '0', 'fontFamily': 'Inter, Arial, sans-serif',
                        'fontWeight': '700', 'fontSize': '2.2rem', 'color': '#374151',
                        'letterSpacing': '-0.5px'}),
        html.P("A Statistical Comparative Analysis of Typography",
                style={'textAlign': 'center', 'margin': '5px 0 0 0', 'fontFamily': 'Inter, Arial, sans-serif',
                        'fontWeight': '400', 'fontSize': '1rem', 'color': '#887C57',
                        'letterSpacing': '0.5px'}),
    ], style={'marginBottom': '20px', 'padding': '20px 0'})

def build_font_selector():
    """Global font-type selector bar (Combined / Roman / Italic)."""
    active = {'marginRight': '5px', 'padding': '8px 16px', 'fontSize': '12px', 'fontWeight': '500',
                'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#2f4a84', 'color': 'white',
                'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                'display': 'inline-flex', 'alignItems': 'center', 'justifyContent': 'center',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.2)', 'width': '100px'}
    inactive = {**active, 'backgroundColor': '#DBD1B5', 'color': '#5a5040'}
    inactive_last = {**inactive, 'marginRight': '0'}

    return html.Div([
        html.Div([
            html.Div(
                html.Label("Font type",
                            style={'fontSize': '13px', 'fontWeight': '600', 'color': '#887C57',
                                    'fontFamily': 'Inter, Arial, sans-serif'}),
                style={'position': 'absolute', 'left': '20px', 'top': '50%', 'transform': 'translateY(-50%)'}
            ),
            html.Div([
                html.Button("Combined", id='font-combined-btn', n_clicks=0, style=active),
                html.Button("Roman", id='font-roman-btn', n_clicks=0, style=inactive),
                html.Button("Italic", id='font-italic-btn', n_clicks=0, style=inactive_last),
            ], style={'display': 'flex', 'justifyContent': 'center', 'width': '100%'}),
            dcc.Store(id='font-type-store', data='combined'),
        ], style={'position': 'relative', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
    ], style={'marginBottom': '15px', 'padding': '12px 20px', 'backgroundColor': '#DBD1B5',
                'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.15)'})

def build_data_stores(initial_umap_list):
    """Hidden dcc.Store components that persist application state."""
    return [
        dcc.Store(id='umap-positions-store', data=initial_umap_list),
        dcc.Store(id='network-selected-books-store', data=[]),
        dcc.Store(id='network-selected-books-visibility-store', data=False),
        dcc.Store(id='network-legend-visibility-store', data={}),
        dcc.Store(id='heatmap-legend-visibility-store', data={}),
    ]


def build_heatmap_and_comparison(initial_heatmap_fig):
    """Similarity matrix (left) + letter comparison panel (right)."""
    section_header = html.Div(
        html.H3("Typographic Similarity Analysis",
                    style={"margin": "0", "fontFamily": "Inter, Arial, sans-serif",
                        "fontWeight": "600", "letterSpacing": "0.5px", "color": "#887C57"}),
        style={"textAlign": "center", "padding": "6px 0", "backgroundColor": "#F8F5EC",
                "borderRadius": "6px", "marginBottom": "10px",
                "boxShadow": "0 1px 2px rgba(0,0,0,0.15)"})

    heatmap_col = html.Div([
        html.Div("Similarity Matrix",
                    style={'textAlign': 'center', 'marginBottom': '8px', 'fontFamily': 'Inter, Arial, sans-serif',
                            'fontWeight': '600', 'fontSize': '13px', 'color': '#887C57'}),
        html.Div([
            html.Button("Hide Printers", id='hide-all-printers-btn', n_clicks=0,
                            style={'marginRight': '5px', 'padding': '8px 16px', 'fontSize': '12px', 'fontWeight': '500',
                                'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#DBD1B5', 'color': '#5a5040',
                                'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer', 'display': 'inline-flex',
                                'alignItems': 'center', 'justifyContent': 'center', 'boxShadow': '0 1px 3px rgba(0,0,0,0.2)',
                                'width': '110px', 'minWidth': '110px'}),
            html.Button("Show Printers", id='show-all-printers-btn', n_clicks=0,
                            style={'padding': '8px 16px', 'fontSize': '12px', 'fontWeight': '500',
                                'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#2f4a84', 'color': 'white',
                                'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer', 'display': 'inline-flex',
                                'alignItems': 'center', 'justifyContent': 'center', 'boxShadow': '0 1px 3px rgba(0,0,0,0.2)',
                                'width': '110px', 'minWidth': '110px'}),
        ], style={'marginBottom': '8px', 'textAlign': 'center'}),
        dcc.Graph(id='similarity-heatmap', figure=initial_heatmap_fig,
                    style={'width': '100%', 'aspectRatio': '1 / 1', 'borderRadius': '8px',
                            'boxShadow': '0 1px 3px rgba(0,0,0,0.2)s', "margin": "0 auto"},
                    config={'responsive': True})
    ], style={'flex': '1 1 45%', 'minWidth': '0', 'maxWidth': '48%', 'boxSizing': 'border-box',
                'backgroundColor': '#F8F5EC', 'borderRadius': '8px', 'padding': '2px', 'overflow': 'hidden'})

    comparison_col = html.Div([
        html.Div("Letter Comparison",
                    style={'textAlign': 'center', 'marginBottom': '8px', 'fontFamily': 'Inter, Arial, sans-serif',
                            'fontWeight': '600', 'fontSize': '13px', 'color': '#887C57'}),
        # Printer filter
        html.Div([
            html.Label("Filter by printer: ",
                        style={'fontWeight': '500', 'marginRight': '10px', 'fontSize': '11px',
                                'color': '#5a5040', 'fontFamily': 'Inter, Arial, sans-serif'}),
            dcc.Dropdown(id='printer-filter-dropdown', options=[], value=None, multi=False,
                            placeholder='All printers', clearable=True, style={'width': '100%', 'fontSize': '11px'}),
            html.Button("Select all from this printer", id='select-all-printer-books-btn', n_clicks=0,
                            style={'marginTop': '5px', 'padding': '6px 12px', 'fontSize': '11px', 'fontWeight': '500',
                                'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#2f4a84', 'color': 'white',
                                'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer', 'display': 'none',
                                'boxShadow': '0 1px 3px rgba(0,0,0,0.2)'}),
        ], style={'marginBottom': '8px', 'padding': '8px', 'backgroundColor': '#DBD1B5', 'borderRadius': '6px'}),
        # Book selector
        html.Div([
            html.Label("Select books: ",
                        style={'fontWeight': '500', 'marginRight': '10px', 'fontSize': '11px',
                                'color': '#5a5040', 'fontFamily': 'Inter, Arial, sans-serif'}),
            html.Button("Clear", id='clear-comparison-btn', n_clicks=0,
                            style={'float': 'right', 'padding': '4px 10px', 'fontSize': '10px', 'fontWeight': '500',
                                'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#DBD1B5', 'color': '#5a5040',
                                'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                                'boxShadow': '0 1px 3px rgba(0,0,0,0.2)'}),
            dcc.Dropdown(id='additional-books-dropdown', options=[], value=[], multi=True,
                            placeholder='+ Click matrix or select books here...', style={'width': '100%', 'fontSize': '11px'}),
            dcc.Store(id='clicked-books-store', data=[]),
        ], style={'marginBottom': '8px', 'padding': '8px', 'backgroundColor': '#DBD1B5', 'borderRadius': '6px'}),
        # Letter filter
        html.Div([
            html.Label("Filter: ", style={'fontWeight': '500', 'marginRight': '5px', 'fontSize': '11px',
                                            'color': '#5a5040', 'fontFamily': 'Inter, Arial, sans-serif'}),
            html.Button("All", id='select-all-letters', n_clicks=0,
                            style={'marginRight': '3px', 'padding': '4px 8px', 'fontSize': '10px', 'fontWeight': '500',
                                'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#2f4a84', 'color': 'white',
                                'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
            html.Button("None", id='select-no-letters', n_clicks=0,
                            style={'marginRight': '8px', 'padding': '4px 8px', 'fontSize': '10px', 'fontWeight': '500',
                                'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#DBD1B5', 'color': '#5a5040',
                                'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
            html.Button("a-z", id='select-lowercase', n_clicks=0,
                            style={'marginRight': '3px', 'padding': '4px 8px', 'fontSize': '10px', 'fontWeight': '500',
                                'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#2f4a84', 'color': 'white',
                                'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
            html.Button("A-Z", id='select-uppercase', n_clicks=0,
                            style={'marginRight': '8px', 'padding': '4px 8px', 'fontSize': '10px', 'fontWeight': '500',
                                'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#2f4a84', 'color': 'white',
                                'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}),
            dcc.Checklist(id='letter-filter', options=[], value=[], inline=True,
                            style={'display': 'inline-block', 'fontSize': '11px'},
                            inputStyle={'marginRight': '2px', 'marginLeft': '6px'})
        ], style={'marginBottom': '8px', 'padding': '8px', 'backgroundColor': '#DBD1B5', 'borderRadius': '6px'}),
        # Comparison output
        html.Div(id='letter-comparison-panel',
                    style={'border': '1px solid #d1c7ad', 'borderRadius': '6px', 'padding': '15px',
                            'backgroundColor': '#F8F5EC', 'minHeight': '500px', 'maxHeight': '800px', 'overflowY': 'auto'},
                    children=[html.P("Click on a cell in the similarity matrix or a node in the network graph",
                                    style={'textAlign': 'center', 'color': '#6b7280', 'marginTop': '200px',
                                            'fontSize': '13px', 'fontFamily': 'Inter, Arial, sans-serif'})])
    ], style={'flex': '1 1 45%', 'minWidth': '0', 'maxWidth': '48%', 'boxSizing': 'border-box',
                'backgroundColor': '#F8F5EC', 'borderRadius': '8px', 'padding': '10px', 'overflow': 'hidden'})

    return html.Div([
        section_header,
        html.Div([heatmap_col, comparison_col],
                    style={'display': 'flex', 'gap': '2%', 'alignItems': 'flex-start', 'justifyContent': 'space-between'}),
    ], style={"width": "100%", "backgroundColor": "#DBD1B5", "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.15)", "padding": "10px", "marginBottom": "20px"})

def build_network_section(initial_network_fig):
    """Network graph with controls (visibility toggles, sliders, UMAP source)."""
    edge_opacity_val = 1.0
    node_size_val = 12
    label_size_val = 8

    section_header = html.Div(
        html.H3("Graph of Typographic Similarity",
                    style={"margin": "0", "fontFamily": "Inter, Arial, sans-serif",
                        "fontWeight": "600", "letterSpacing": "0.5px", "color": "#887C57"}),
        style={"textAlign": "center", "padding": "6px 0", "backgroundColor": "#F8F5EC",
                "borderRadius": "6px", "marginBottom": "10px",
                "boxShadow": "0 1px 2px rgba(0,0,0,0.15)"})

    # --- Reusable button style helpers ---
    _toggle_base = {'marginBottom': '8px', 'padding': '8px 16px', 'fontSize': '12px', 'fontWeight': '500',
                    'fontFamily': 'Inter, Arial, sans-serif', 'border': 'none', 'borderRadius': '6px',
                    'cursor': 'pointer', 'display': 'inline-flex', 'alignItems': 'center', 'justifyContent': 'center',
                    'boxShadow': '0 1px 3px rgba(0,0,0,0.2)', 'transition': 'background-color 0.15s ease, transform 0.05s ease',
                    'lineHeight': '1', 'width': '120px', 'minWidth': '120px'}
    _active = {**_toggle_base, 'backgroundColor': '#2f4a84', 'color': 'white'}
    _inactive = {**_toggle_base, 'backgroundColor': '#DBD1B5', 'color': '#5a5040'}
    _active_mr = {**_active, 'marginRight': '5px'}
    _inactive_mr = {**_inactive, 'marginRight': '5px'}

    col1 = html.Div([
        html.Div([
            html.Button("Hide Labels", id='hide-all-labels-btn', n_clicks=0, style=_inactive_mr),
            html.Button("Show Labels", id='show-all-labels-btn', n_clicks=0, style=_active),
            html.Br(),
            html.Button("Hide Markers", id='hide-all-markers-btn', n_clicks=0, style=_inactive_mr),
            html.Button("Show Markers", id='show-all-markers-btn', n_clicks=0, style=_active),
            html.Br(),
            html.Button("Hide Printers", id='hide-all-network-printers-btn', n_clicks=0, style=_inactive_mr),
            html.Button("Show Printers", id='show-all-network-printers-btn', n_clicks=0, style=_active),
            html.Br(),
            html.Button("Hide Selected", id='hide-selected-books-btn', n_clicks=0, style=_active_mr),
            html.Button("Show Selected", id='show-selected-books-btn', n_clicks=0, style=_inactive),
        ], style={'display': 'inline-block', 'textAlign': 'center'})
    ], style={'width': '30%', 'flexShrink': '0', 'flexGrow': '0', 'display': 'flex',
                'alignItems': 'center', 'justifyContent': 'center'})

    slider_label = {'fontSize': '11px', 'fontWeight': '500', 'color': 'dimgray',
                    'fontFamily': 'Inter, Arial, sans-serif', 'marginBottom': '2px'}
    col2 = html.Div([
        html.Div([
            html.Div([
                html.Label("Edge Opacity:", style=slider_label),
                dcc.Slider(id='edge-opacity-slider', min=0, max=2, step=0.1, value=edge_opacity_val,
                            marks={0: {'label': '0', 'style': {'fontSize': '10px'}},
                                    1: {'label': '1', 'style': {'fontSize': '10px'}},
                                    2: {'label': '2', 'style': {'fontSize': '10px'}}},
                            tooltip={"placement": "bottom", "always_visible": False}, className="compact-slider")
            ], style={'marginBottom': '-10px'}),
            html.Div([
                html.Label("Node Size:", style=slider_label),
                dcc.Slider(id='node-size-slider', min=6, max=24, step=1, value=node_size_val,
                            marks={6: {'label': '6', 'style': {'fontSize': '10px'}},
                                    15: {'label': '15', 'style': {'fontSize': '10px'}},
                                    24: {'label': '24', 'style': {'fontSize': '10px'}}},
                            tooltip={"placement": "bottom", "always_visible": False}, className="compact-slider"),
            ], style={'marginBottom': '-10px'}),
            html.Div([
                html.Label("Label Size:", style=slider_label),
                dcc.Slider(id='label-size-slider', min=6, max=24, step=1, value=label_size_val,
                            marks={6: {'label': '6', 'style': {'fontSize': '10px'}},
                                    15: {'label': '15', 'style': {'fontSize': '10px'}},
                                    24: {'label': '24', 'style': {'fontSize': '10px'}}},
                            tooltip={"placement": "bottom", "always_visible": False}, className="compact-slider"),
            ]),
        ], style={'width': '85%'})
    ], style={'width': '30%', 'flexShrink': '0', 'flexGrow': '0', 'display': 'flex',
                'flexDirection': 'column', 'justifyContent': 'center'})

    umap_active = {'marginRight': '5px', 'padding': '8px 16px', 'fontSize': '12px', 'fontWeight': '500',
                    'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#2f4a84', 'color': 'white',
                    'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
                    'display': 'inline-flex', 'alignItems': 'center', 'justifyContent': 'center',
                    'boxShadow': '0 1px 3px rgba(0,0,0,0.2)', 'width': '100px'}
    umap_inactive = {**umap_active, 'backgroundColor': '#DBD1B5', 'color': '#5a5040'}
    umap_inactive_last = {**umap_inactive, 'marginRight': '0'}

    col3 = html.Div([
        html.Div([
            html.Div("Node positions source",
                        style={'fontWeight': '600', 'fontSize': '11px', 'color': '#887C57',
                                'marginBottom': '8px', 'textAlign': 'center', 'fontFamily': 'Inter, Arial, sans-serif'}),
            html.Div([
                html.Button("Combined", id='umap-pos-combined-btn', n_clicks=0, style=umap_active),
                html.Button("Roman", id='umap-pos-roman-btn', n_clicks=0, style=umap_inactive),
                html.Button("Italic", id='umap-pos-italic-btn', n_clicks=0, style=umap_inactive_last),
            ], style={'display': 'flex', 'justifyContent': 'center', 'gap': '2px'})
        ], style={'backgroundColor': '#DBD1B5', 'borderRadius': '8px', 'padding': '8px 10px', 'width': '100%'})
    ], style={'width': '30%', 'flexShrink': '0', 'flexGrow': '0', 'display': 'flex',
                'alignItems': 'center', 'justifyContent': 'center'})

    controls_row = html.Div([col1, col2, col3],
                                style={'marginBottom': '5px', 'padding': '10px', 'backgroundColor': "#DBD1B5",
                                    'borderRadius': '8px', 'display': 'flex', 'flexWrap': 'nowrap',
                                    'alignItems': 'stretch', 'justifyContent': 'space-between'})

    return html.Div([
        section_header,
        dcc.Store(id='umap-pos-source-store', data='combined'),
        controls_row,
        dcc.Graph(id='network-graph', figure=initial_network_fig,
                    style={'height': '800px', 'marginTop': '8px', 'borderRadius': '8px', 'overflow': 'hidden'})
    ], style={"width": "100%", "backgroundColor": "#DBD1B5", "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.15)", "padding": "5px"})

# def build_dendrogram_section(initial_dendro_fig, books):
#     """Typographic Dendrogram panel — font selector, cut-level slider, truncation, drill-down, groups."""

#     default_level = 6
#     default_p = 30

#     _font = {'fontSize': '12px', 'fontFamily': 'Inter, Arial, sans-serif'}
#     _label = {'fontSize': '12px', 'fontWeight': '600', 'color': '#5a5040', 'fontFamily': 'Inter, Arial, sans-serif'}

#     section_header = html.Div(
#         html.H3("Typographic Dendrogram",
#                     style={"margin": "0", "fontFamily": "Inter, Arial, sans-serif",
#                         "fontWeight": "600", "letterSpacing": "0.5px", "color": "#887C57"}),
#         style={"textAlign": "center", "padding": "6px 0", "backgroundColor": "#F8F5EC",
#                 "borderRadius": "6px", "marginBottom": "10px",
#                 "boxShadow": "0 1px 2px rgba(0,0,0,0.15)"})

#     font_active = {'marginRight': '5px', 'padding': '8px 16px', 'fontSize': '12px', 'fontWeight': '500',
#                     'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#2f4a84', 'color': 'white',
#                     'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer',
#                     'display': 'inline-flex', 'alignItems': 'center', 'justifyContent': 'center',
#                     'boxShadow': '0 1px 3px rgba(0,0,0,0.2)', 'width': '100px'}
#     font_inactive = {**font_active, 'backgroundColor': '#DBD1B5', 'color': '#5a5040', 'marginRight': '0'}

#     _toggle_base = {'marginBottom': '8px', 'padding': '8px 16px', 'fontSize': '12px', 'fontWeight': '500',
#                     'fontFamily': 'Inter, Arial, sans-serif', 'border': 'none', 'borderRadius': '6px',
#                     'cursor': 'pointer', 'display': 'inline-flex', 'alignItems': 'center', 'justifyContent': 'center',
#                     'boxShadow': '0 1px 3px rgba(0,0,0,0.2)', 'transition': 'background-color 0.15s ease, transform 0.05s ease',
#                     'lineHeight': '1', 'width': '120px', 'minWidth': '120px'}
#     _active = {**_toggle_base, 'backgroundColor': '#2f4a84', 'color': 'white'}
#     _inactive = {**_toggle_base, 'backgroundColor': '#DBD1B5', 'color': '#5a5040'}

#     # Truncation controls: how many leaf-clusters to show
#     n_books = len(books)
#     p_marks = {}
#     for v in [10, 20, 30, 50, 100, 150]:
#         if v <= n_books:
#             p_marks[v] = {'label': str(v) if v < 150 else 'Max', 'style': {'fontSize': '10px'}}

#     return html.Div([
#         section_header,
#         # help_guide,
#         # Font selector row
#         html.Div([
#             html.Button("Combined", id='dendro-combined-btn', n_clicks=0, style=font_active),
#             html.Button("Roman", id='dendro-roman-btn', n_clicks=0, style=font_inactive),
#             html.Button("Italic", id='dendro-italic-btn', n_clicks=0, style=font_inactive),
#             dcc.Store(id='dendro-font-store', data='combined'),
#             dcc.Store(id='dendro-highlight-store', data=None),
#             # Store: which subtree to drill into (None = full tree, int = linkage node id)
#             dcc.Store(id='dendro-drilldown-store', data=None),
#         ], style={'textAlign': 'center', 'marginBottom': '8px'}),
#         # Controls row: two columns
#         html.Div([
#             # Left column — cut level
#             html.Div([
#                 html.Label('Cut Level (threshold to form groups):', style=_label),
#                 dcc.Slider(id='dendro-level-slider', min=0, max=self._maxv_cache['combined'], step=1,
#                             value=default_level, marks=level_marks,
#                             tooltip={"placement": "bottom", "always_visible": False}, className='compact-slider'),
#             ], style={'flex': '1', 'padding': '0 8px'}),
#             # Right column — truncation p
#             html.Div([
#                 html.Label('Detail level (visible clusters):', style=_label),
#                 dcc.Slider(id='dendro-truncation-slider', min=5, max=150, step=1,
#                             value=min(default_p, n_books), marks=p_marks,
#                             tooltip={"placement": "bottom", "always_visible": False}, className='compact-slider'),
#             ], style={'flex': '1', 'padding': '0 8px'}),
#         ], style={'display': 'flex', 'padding': '6px 0'}),
#         # Status row: level label + breadcrumb + show/hide buttons
#         html.Div([
#             html.Div(id='dendro-level-label', style={'textAlign': 'center', 'color': '#5a5040', **_font}),
#             html.Div(id='dendro-breadcrumb', children=[
#                 html.Button("← Back to full tree", id='dendro-back-btn', n_clicks=0,
#                             style={'display': 'none'})
#             ], style={'textAlign': 'center', 'marginTop': '4px'}),
#             html.Div([
#                 html.Div([
#                     html.Label('Search book:', style={**_label, 'marginRight': '6px', 'display': 'inline-block', 'verticalAlign': 'middle'}),
#                     dcc.Dropdown(
#                         id='dendro-search-book-dropdown',
#                         options=[{'label': str(b), 'value': str(b)} for b in sorted(self.books)],
#                         placeholder='Type a book name...',
#                         searchable=True,
#                         clearable=True,
#                         style={'width': '350px', 'display': 'inline-block', 'verticalAlign': 'middle',
#                                 'fontSize': '11px', 'fontFamily': 'Inter, Arial, sans-serif'},
#                     ),
#                 ], style={'display': 'inline-flex', 'alignItems': 'center', 'marginRight': '16px'}),
#                 html.Button('Hide Singletons', id='dendro-hide-singletons-btn', n_clicks=0,
#                                 style=_inactive),
#             ], style={'textAlign': 'center', 'marginTop': '8px', 'display': 'flex',
#                         'justifyContent': 'center', 'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '6px'}),
#             dcc.Store(id='dendro-hide-singletons', data=False),
#         ], style={'padding': '4px 12px'}),
#         # Graph — dynamic height set by callback
#         dcc.Graph(id='dendrogram-graph', figure=initial_dendro_fig,
#                     style={'marginTop': '8px', 'borderRadius': '8px', 'overflow': 'hidden'}),
#         # Group summaries
#         html.Div(id='dendro-groups-container',
#                     style={'marginTop': '10px', 'maxHeight': '300px', 'overflowY': 'auto',
#                             'padding': '8px', 'backgroundColor': '#F8F5EC', 'borderRadius': '6px'}),
#     ], style={'marginTop': '20px', 'padding': '10px', 'backgroundColor': '#DBD1B5',
#                 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.15)'})

# def build_export_section():
#     """Export controls and download component."""
#     return html.Div([
#         html.Div(
#             html.H3("Export",
#                         style={"margin": "0", "fontFamily": "Inter, Arial, sans-serif",
#                             "fontWeight": "600", "letterSpacing": "0.5px", "color": "#887C57"}),
#             style={"textAlign": "center", "padding": "6px 0", "backgroundColor": "#F8F5EC",
#                     "borderRadius": "6px", "marginBottom": "10px",
#                     "boxShadow": "0 1px 2px rgba(0,0,0,0.15)"}),
#         html.Div([
#             html.Button("Download HTML", id="export-html-btn", n_clicks=0,
#                             style={'padding': '10px 20px', 'backgroundColor': '#2f4a84', 'color': 'white',
#                                 'border': 'none', 'borderRadius': '6px', 'fontSize': '13px',
#                                 'cursor': 'pointer', 'fontWeight': '500', 'fontFamily': 'Inter, Arial, sans-serif',
#                                 'boxShadow': '0 1px 3px rgba(0,0,0,0.2)'}),
#         ], style={'textAlign': 'center'}),
#         html.Div(id="export-status",
#                     style={'textAlign': 'center', 'marginTop': '10px', 'fontFamily': 'Inter, Arial, sans-serif',
#                             'color': '#5a5040'})
#     ], style={'marginTop': '20px', 'padding': '10px', 'backgroundColor': '#DBD1B5',
#                 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.15)'})
