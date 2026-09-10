# callbacks/core_viz.py
from dash import Input, Output, State, ctx, no_update, Patch
from helpers import get_book_color

def register_core_visualization_callbacks(app, ctx_obj):
    
    @app.callback(
        [Output('network-graph', 'figure'),
         Output('similarity-heatmap', 'figure')],
        [Input('font-type-store', 'data'),
         Input('umap-pos-source-store', 'data')],
        [State('edge-opacity-slider', 'value'),
         State('node-size-slider', 'value'),
         State('label-size-slider', 'value'),
         State('additional-books-dropdown', 'value')]  # ← Added this
    )
    def update_visualizations(font_type, umap_source, edge_opacity, node_size, label_size, selected_books):
        
        umap_array = ctx_obj.umap_positions[umap_source]
        edges_data = ctx_obj.edges[font_type]
        
        network_fig = ctx_obj.create_network_graph(
            umap_positions=umap_array,
            edges_data=edges_data,
            edge_opacity=edge_opacity or 1.0, 
            marker_size=node_size, 
            label_size=label_size
        )
        
        heatmap_fig = ctx_obj.create_heatmap(font=font_type)
        
        # Restore overlays if books are selected
        if selected_books:
            heatmap_dict = heatmap_fig.to_plotly_json() if hasattr(heatmap_fig, 'to_plotly_json') else heatmap_fig
            book_list = list(ctx_obj.books)
            
            for book in selected_books:
                if book not in book_list:
                    continue
                
                color = get_book_color(ctx_obj.books, book)
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                overlay_color = f'rgba({r}, {g}, {b}, 0.35)'
                
                # Horizontal line (row)
                heatmap_dict['data'].append({
                    'type': 'scatter',
                    'x': [book_list[0], book_list[-1]],
                    'y': [book, book],
                    'mode': 'lines',
                    'line': {'color': overlay_color, 'width': 3},
                    'showlegend': False,
                    'hoverinfo': 'skip',
                    'name': f'overlay_row_{book}'
                })
                
                # Vertical line (column)
                heatmap_dict['data'].append({
                    'type': 'scatter',
                    'x': [book, book],
                    'y': [book_list[0], book_list[-1]],
                    'mode': 'lines',
                    'line': {'color': overlay_color, 'width': 3},
                    'showlegend': False,
                    'hoverinfo': 'skip',
                    'name': f'overlay_col_{book}'
                })
            
            heatmap_fig = heatmap_dict
                    
        return network_fig, heatmap_fig