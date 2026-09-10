# callbacks/network.py
from dash import Input, Output, State, ctx, no_update, Patch
import numpy as np
from helpers import get_book_color

def register_network_callbacks(app, ctx_obj):
    
    # ==========================================
    # 1. FAST UI TOGGLES (Using Patch)
    # ==========================================
    
    @app.callback(
        [Output('network-graph', 'figure', allow_duplicate=True),
         Output('show-all-labels-btn', 'style'),
         Output('hide-all-labels-btn', 'style')],
        [Input('show-all-labels-btn', 'n_clicks'),
         Input('hide-all-labels-btn', 'n_clicks')],
        [State('network-graph', 'figure')],
        prevent_initial_call=True
    )
    def toggle_network_labels(show_clicks, hide_clicks, current_fig):
        if not ctx.triggered or not current_fig or not current_fig.get('data'):
            return no_update, no_update, no_update
        
        show_labels = (ctx.triggered_id == 'show-all-labels-btn')
        show_style = {**ctx_obj.active_btn_style, 'marginBottom': '8px'} if show_labels else {**ctx_obj.inactive_btn_style, 'marginRight': '5px', 'marginBottom': '8px'}
        hide_style = {**ctx_obj.active_btn_style, 'marginRight': '5px', 'marginBottom': '8px'} if not show_labels else {**ctx_obj.inactive_btn_style, 'marginBottom': '8px'}
        
        patched_fig = Patch()
        for i, trace in enumerate(current_fig['data']):
            name = trace.get('name', '')
            if name.startswith('bin_') or name.startswith('selected_'):
                continue
            
            has_markers = 'markers' in trace.get('mode', 'markers')
            patched_fig['data'][i]['mode'] = 'markers+text' if (show_labels and has_markers) else ('text' if show_labels else ('markers' if has_markers else 'none'))
            
        return patched_fig, show_style, hide_style

    @app.callback(
        [Output('network-graph', 'figure', allow_duplicate=True),
         Output('show-all-markers-btn', 'style'),
         Output('hide-all-markers-btn', 'style')],
        [Input('show-all-markers-btn', 'n_clicks'),
         Input('hide-all-markers-btn', 'n_clicks')],
        [State('network-graph', 'figure')],
        prevent_initial_call=True
    )
    def toggle_network_markers(show_clicks, hide_clicks, current_fig):
        if not ctx.triggered or not current_fig or not current_fig.get('data'):
            return no_update, no_update, no_update
        
        show_markers = (ctx.triggered_id == 'show-all-markers-btn')
        show_style = {**ctx_obj.active_btn_style, 'marginBottom': '8px'} if show_markers else {**ctx_obj.inactive_btn_style, 'marginRight': '5px', 'marginBottom': '8px'}
        hide_style = {**ctx_obj.active_btn_style, 'marginRight': '5px', 'marginBottom': '8px'} if not show_markers else {**ctx_obj.inactive_btn_style, 'marginBottom': '8px'}
        
        patched_fig = Patch()
        for i, trace in enumerate(current_fig['data']):
            name = trace.get('name', '')
            if name.startswith('bin_') or name.startswith('selected_'):
                continue
            
            has_text = 'text' in trace.get('mode', 'markers')
            patched_fig['data'][i]['mode'] = 'markers+text' if (show_markers and has_text) else ('markers' if show_markers else ('text' if has_text else 'none'))
            
        return patched_fig, show_style, hide_style

    @app.callback(
        Output('network-graph', 'figure', allow_duplicate=True),
        [Input('edge-opacity-slider', 'value')],
        [State('network-graph', 'figure')],
        prevent_initial_call=True
    )
    def update_edge_opacity_only(edge_opacity, current_fig):
        if not ctx.triggered or not current_fig or not current_fig.get('data') or edge_opacity is None:
            return no_update

        patched = Patch()
        for i, trace in enumerate(current_fig['data']):
            name = trace.get('name', '')
            if name.startswith('bin_') or name.startswith('selected_edge_'):
                customdata = trace.get('customdata', [])
                if customdata and len(customdata) > 0:
                    w = float(customdata[0])
                    new_a = min(1.0, w) if name.startswith('selected_edge_') else min(1.0, w * float(edge_opacity))
                    patched['data'][i]['line']['color'] = f'rgba(100,100,100,{new_a})'
        return patched

    @app.callback(
        Output('network-graph', 'figure', allow_duplicate=True),
        [Input('node-size-slider', 'value'),
         Input('label-size-slider', 'value')],
        [State('network-graph', 'figure')],
        prevent_initial_call=True
    )
    def update_node_label_size(node_size, label_size, current_fig):
        if not ctx.triggered or not current_fig or not current_fig.get('data'):
            return no_update
            
        patched_fig = Patch()
        for i, trace in enumerate(current_fig['data']):
            # Skip edges
            if trace.get('name', '').startswith('bin_') or trace.get('name', '').startswith('selected_'):
                continue
                
            # Safer check for unknown printers (avoids fragile string matching on rgba)
            is_unknown = 'unknown' in trace.get('name', '').lower() or 'missing' in trace.get('name', '').lower()
            size_mult = 0.5 if is_unknown else 1.0
            
            if 'marker' in trace:
                patched_fig['data'][i]['marker']['size'] = float(node_size * size_mult)
            if 'textfont' in trace:
                patched_fig['data'][i]['textfont']['size'] = float(label_size * size_mult)
                
        return patched_fig

    # ==========================================
    # 2. SELECTION & OVERLAYS (Optimized)
    # ==========================================

    @app.callback(
        [Output('clicked-books-store', 'data', allow_duplicate=True),
         Output('additional-books-dropdown', 'value', allow_duplicate=True)],
        [Input('network-graph', 'clickData')],
        [State('additional-books-dropdown', 'value')],
        prevent_initial_call=True
    )
    def handle_network_click(click_data, dropdown_books):
        if click_data is None:
            return no_update, no_update

        point = click_data['points'][0]
        custom = point.get('customdata')
        if not custom:
            return no_update, no_update
            
        book_name = custom[0] if isinstance(custom, list) else str(custom)
        current_books = list(dropdown_books) if dropdown_books else []
        
        if book_name in current_books:
            current_books = [b for b in current_books if b != book_name]
        else:
            current_books.append(book_name)

        return current_books, current_books

    @app.callback(
        [Output('network-graph', 'figure', allow_duplicate=True),
         Output('network-selected-books-visibility-store', 'data', allow_duplicate=True)],
        [Input('additional-books-dropdown', 'value'),
         Input('show-selected-books-btn', 'n_clicks'),
         Input('hide-selected-books-btn', 'n_clicks')],
        [State('network-graph', 'figure'),
         State('network-selected-books-visibility-store', 'data'),
         State('umap-positions-store', 'data'),
         State('node-size-slider', 'value'),
         State('label-size-slider', 'value'),
         State('font-type-store', 'data'),
         State('edge-opacity-slider', 'value')],
        prevent_initial_call=True
    )
    def handle_selected_books_in_network(selected_books, show_clicks, hide_clicks, current_fig, 
                                          is_visible, umap_positions, node_size, label_size, font_type, edge_opacity):
        if not current_fig or not current_fig.get('data'):
            return no_update, no_update

        trigger_id = ctx.triggered_id
        selected_books = selected_books or []
        
        # 1. Update visibility state cleanly based on button clicks
        if trigger_id == 'show-selected-books-btn':
            is_visible = True
        elif trigger_id == 'hide-selected-books-btn':
            is_visible = False
        # If triggered by dropdown, preserve the existing `is_visible` state

        # 2. Prepare Patch: Remove old selected traces
        patched_fig = Patch()
        patched_fig['data'] = [
            trace for trace in current_fig['data'] 
            if not trace.get('name', '').startswith('selected_')
        ]
        
        # 3. Add new selected traces if visible
        if is_visible and selected_books and umap_positions is not None:
            umap_array = np.asarray(umap_positions, dtype=np.float32)
            book_list = list(ctx_obj.books)
            edge_op = float(edge_opacity) if edge_opacity is not None else 1.0
            bins = ctx_obj.edges[font_type]['binned_edges']
            
            for book in selected_books:
                if book not in book_list:
                    continue
                    
                book_idx = book_list.index(book)
                book_color = get_book_color(ctx_obj.books, book)
                
                printer_name = ctx_obj.printers[book_idx] if book_idx < len(ctx_obj.printers) else 'Unknown'
                if printer_name in ['n. nan', 'm. missing', 'unknown']:
                    printer_name = 'Unknown'
                
                # Add Book Node (cast to float to prevent NumPy serialization errors)
                patched_fig['data'].append({
                    'type': 'scatter',
                    'x': [float(umap_array[book_idx, 0])],
                    'y': [float(umap_array[book_idx, 1])],
                    'mode': 'markers+text',
                    'marker': {
                        'symbol': 'star',
                        'size': float(node_size * 1.3) if node_size else 18.0,
                        'color': book_color,
                        'line': {'width': 2, 'color': 'white'}
                    },
                    'text': [book],
                    'textposition': 'top center',
                    'textfont': {
                        'size': float(label_size) if label_size else 8.0,
                        'color': book_color,
                        'family': 'Arial, bold'
                    },
                    'hovertemplate': f'{book}<br>Printer: {printer_name}<extra></extra>',
                    'name': f'selected_book_{book}',
                    'showlegend': False
                })
                
                # Add Edges for this book (VECTORIZED FOR SPEED)
                r, g, b = int(book_color[1:3], 16), int(book_color[3:5], 16), int(book_color[5:7], 16)
                
                for bin_idx, bin_data in bins.items():
                    edges_in_bin = bin_data.get('edges', [])
                    if not edges_in_bin:
                        continue
                    
                    # Fast NumPy masking
                    edges_array = np.array(edges_in_bin, dtype=np.int32)
                    mask = (edges_array[:, 0] == book_idx) | (edges_array[:, 1] == book_idx)
                    matching_edges = edges_array[mask]
                    
                    if len(matching_edges) > 0:
                        # Vectorized coordinate extraction (10-50x faster than Python for-loop)
                        x_coords = umap_array[matching_edges, 0] # N x 2
                        y_coords = umap_array[matching_edges, 1] # N x 2
                        
                        n_edges = len(matching_edges)
                        xs = np.empty(n_edges * 3, dtype=object)
                        ys = np.empty(n_edges * 3, dtype=object)
                        
                        # Interleave with None for Plotly line breaks: [x0, x1, None, x2, x3, None...]
                        xs[0::3] = x_coords[:, 0]
                        xs[1::3] = x_coords[:, 1]
                        xs[2::3] = None
                        ys[0::3] = y_coords[:, 0]
                        ys[1::3] = y_coords[:, 1]
                        ys[2::3] = None
                        
                        avg_w = float(bin_data.get('avg_w', 0))
                        opacity = min(1.0, avg_w)
                        color = f'rgba({r},{g},{b},{opacity})'
                        
                        patched_fig['data'].append({
                            'type': 'scatter',
                            'x': xs.tolist(),
                            'y': ys.tolist(),
                            'mode': 'lines',
                            'line': {'width': 2, 'color': color},
                            'showlegend': False,
                            'customdata': [avg_w],
                            'name': f'selected_edge_{book}_bin{bin_idx}',
                            'hoverinfo': 'skip'
                        })

        return patched_fig, is_visible

    @app.callback(
        [Output('show-selected-books-btn', 'style'), 
         Output('hide-selected-books-btn', 'style')],
        [Input('network-selected-books-visibility-store', 'data')],
        prevent_initial_call=False
    )
    def sync_selected_books_buttons(is_visible):
        # Default fallback if store is empty/None (e.g., on initial page load)
        if is_visible is None:
            is_visible = False 
            
        if is_visible:
            # Show is ACTIVE, Hide is INACTIVE
            # Note: ctx_obj.active_btn_style already has 'marginRight': '5px'
            show_style = {**ctx_obj.active_btn_style, 'marginBottom': '8px'}
            hide_style = {**ctx_obj.inactive_btn_style, 'marginRight': '0', 'marginBottom': '8px'}
        else:
            # Show is INACTIVE, Hide is ACTIVE
            show_style = {**ctx_obj.inactive_btn_style, 'marginBottom': '8px'}
            hide_style = {**ctx_obj.active_btn_style, 'marginRight': '0', 'marginBottom': '8px'}
            
        return show_style, hide_style

    # ==========================================
    # 3. LEGEND SYNC
    # ==========================================

    @app.callback(
        [Output('network-graph', 'figure', allow_duplicate=True),
         Output('show-all-network-printers-btn', 'style', allow_duplicate=True),
         Output('hide-all-network-printers-btn', 'style', allow_duplicate=True),
         Output('network-legend-visibility-store', 'data', allow_duplicate=True)],
        [Input('show-all-network-printers-btn', 'n_clicks'),
         Input('hide-all-network-printers-btn', 'n_clicks')],
        [State('network-graph', 'figure')],
        prevent_initial_call=True
    )
    def toggle_all_network_printers(show_clicks, hide_clicks, current_fig):
        if not ctx.triggered or not current_fig or not current_fig.get('data'):
            return no_update, no_update, no_update, no_update
        
        show_all = (ctx.triggered_id == 'show-all-network-printers-btn')
        show_style = {**ctx_obj.active_btn_style, 'marginBottom': '8px'} if show_all else {**ctx_obj.inactive_btn_style, 'marginRight': '5px', 'marginBottom': '8px'}
        hide_style = {**ctx_obj.active_btn_style, 'marginRight': '5px', 'marginBottom': '8px'} if not show_all else {**ctx_obj.inactive_btn_style, 'marginBottom': '8px'}
        
        patched_fig = Patch()
        store_update = {}
        
        for i, trace in enumerate(current_fig['data']):
            name = trace.get('name', '')
            if name.startswith('bin_') or name.startswith('selected_'):
                continue
            
            vis_state = True if show_all else 'legendonly'
            patched_fig['data'][i]['visible'] = vis_state
            store_update[name] = vis_state

        return patched_fig, show_style, hide_style, store_update

    @app.callback(
        Output('network-legend-visibility-store', 'data', allow_duplicate=True),
        [Input('network-graph', 'restyleData')],
        [State('network-graph', 'figure'), State('network-legend-visibility-store', 'data')],
        prevent_initial_call=True
    )
    def sync_network_legend_visibility(restyleData, current_fig, store):
        if restyleData is None:
            return no_update
        try:
            changes = restyleData[0]
            idxs = restyleData[1] if len(restyleData) > 1 else None
            new_store = dict(store) if store else {}
            
            if 'visible' in changes:
                vals = changes['visible']
                if idxs:
                    for i, idx in enumerate(idxs):
                        val = vals[i] if isinstance(vals, list) and len(vals) > i else vals[0]
                        new_store[current_fig['data'][idx].get('name', '')] = val
                else:
                    arr = vals[0] if isinstance(vals, list) and len(vals) == 1 and isinstance(vals[0], list) else vals
                    for idx, tr in enumerate(current_fig.get('data', [])):
                        if idx < len(arr):
                            new_store[tr.get('name', '')] = arr[idx]
            return new_store
        except Exception as e:
            print(f"Warning: sync_network_legend_visibility failed: {e}")
            return no_update

    @app.callback(
        [Output('show-all-network-printers-btn', 'style'), Output('hide-all-network-printers-btn', 'style')],
        [Input('network-legend-visibility-store', 'data')],
        prevent_initial_call=False
    )
    def sync_network_printer_buttons(store):
        if not store:
            return no_update, no_update
            
        vals = list(store.values())
        all_visible = all(v is True for v in vals)
        all_hidden = all(v == 'legendonly' for v in vals)
        
        if all_visible:
            return {**ctx_obj.active_btn_style, 'marginBottom': '8px'}, {**ctx_obj.inactive_btn_style, 'marginRight': '5px', 'marginBottom': '8px'}
        if all_hidden:
            return {**ctx_obj.inactive_btn_style, 'marginRight': '5px', 'marginBottom': '8px'}, {**ctx_obj.active_btn_style, 'marginBottom': '8px'}
            
        return {**ctx_obj.inactive_btn_style, 'marginRight': '5px', 'marginBottom': '8px'}, {**ctx_obj.inactive_btn_style, 'marginBottom': '8px'}

        # ==========================================
    # 4. UMAP POSITION SOURCE SWITCHING
    # ==========================================

    @app.callback(
        [Output('umap-pos-source-store', 'data'),
         Output('umap-pos-combined-btn', 'style'),
         Output('umap-pos-roman-btn', 'style'),
         Output('umap-pos-italic-btn', 'style')],
        [Input('umap-pos-combined-btn', 'n_clicks'),
         Input('umap-pos-roman-btn', 'n_clicks'),
         Input('umap-pos-italic-btn', 'n_clicks')],
        [State('umap-pos-source-store', 'data')],
        prevent_initial_call=True
    )
    def update_umap_pos_source(combined_clicks, roman_clicks, italic_clicks, current_source):
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update
        
        trigger_id = ctx.triggered_id
        
        # Define styles using ctx_obj to keep it DRY
        active_style = {**ctx_obj.active_btn_style}
        inactive_style = {**ctx_obj.inactive_btn_style}
        inactive_style_last = {**inactive_style, 'marginRight': '0'}
        active_style_last = {**active_style, 'marginRight': '0'}
        
        if trigger_id == 'umap-pos-combined-btn':
            return 'combined', active_style, inactive_style, inactive_style_last
        elif trigger_id == 'umap-pos-roman-btn':
            return 'roman', inactive_style, active_style, inactive_style_last
        elif trigger_id == 'umap-pos-italic-btn':
            return 'italic', inactive_style, inactive_style, active_style_last
            
        return no_update, no_update, no_update, no_update

    @app.callback(
        [Output('umap-positions-store', 'data', allow_duplicate=True),
         Output('network-graph', 'figure', allow_duplicate=True)],
        [Input('umap-pos-source-store', 'data')],
        [State('network-graph', 'figure'), 
         State('edge-opacity-slider', 'value'),
         State('node-size-slider', 'value'), 
         State('label-size-slider', 'value'),
         State('font-type-store', 'data'), 
         State('network-legend-visibility-store', 'data')],
        prevent_initial_call=True
    )
    def handle_umap_pos_source_change(pos_source, current_network_fig, edge_opacity, 
                                      node_size, label_size, current_edge_font, network_legend_vis):
        if not pos_source:
            return no_update, no_update

        umap_positions = ctx_obj.umap_positions.get(pos_source)            
        umap_array = np.asarray(umap_positions, dtype=np.float32)

        edges_data = ctx_obj.edges[current_edge_font]

        network_fig = ctx_obj.create_network_graph(
            umap_positions=umap_array,
            edges_data=edges_data,
            edge_opacity=edge_opacity or 1.0, 
            marker_size=node_size, 
            label_size=label_size
        )
        
        if network_legend_vis and network_fig:
            # Convert to dict if it's a go.Figure, otherwise it's already a dict
            nf = network_fig.to_plotly_json() if hasattr(network_fig, 'to_plotly_json') else network_fig
            for tr in nf.get('data', []):
                name = tr.get('name', '')
                if name in network_legend_vis:
                    tr['visible'] = network_legend_vis[name]
            network_fig = nf

        return umap_array.tolist(), network_fig