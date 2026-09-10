# callbacks/heatmap.py
from dash import Input, Output, State, ctx, no_update, Patch

def register_heatmap_callbacks(app, ctx_obj):
    
    @app.callback(
        [Output('similarity-heatmap', 'figure', allow_duplicate=True),
         Output('show-all-printers-btn', 'style', allow_duplicate=True),
         Output('hide-all-printers-btn', 'style', allow_duplicate=True),
         Output('heatmap-legend-visibility-store', 'data', allow_duplicate=True)],
        [Input('show-all-printers-btn', 'n_clicks'),
         Input('hide-all-printers-btn', 'n_clicks')],
        [State('similarity-heatmap', 'figure')],
        prevent_initial_call=True
    )
    def toggle_all_printers(show_clicks, hide_clicks, current_fig):
        if not ctx.triggered or current_fig is None:
            return no_update, no_update, no_update, no_update

        trigger_id = ctx.triggered_id
        show_all = (trigger_id == 'show-all-printers-btn')

        patched_fig = Patch()
        store_update = {}
        
        for i in range(1, len(current_fig['data'])):
            name = current_fig['data'][i].get('name', '')
            if name.startswith('overlay_'):
                continue
            patched_fig['data'][i]['visible'] = True if show_all else 'legendonly'
            store_update[name] = True if show_all else 'legendonly'

        patched_fig['layout']['uirevision'] = 'constant'
        
        show_style = ctx_obj.active_btn_style if show_all else ctx_obj.inactive_btn_style
        hide_style = ctx_obj.inactive_btn_style if show_all else ctx_obj.active_btn_style

        return patched_fig, show_style, hide_style, store_update

    @app.callback(
        Output('similarity-heatmap', 'figure', allow_duplicate=True),
        [Input('similarity-heatmap', 'relayoutData')],
        [State('similarity-heatmap', 'figure')],
        prevent_initial_call=True
    )
    def adjust_tick_font_on_zoom(relayout_data, current_fig):
        if relayout_data is None or current_fig is None or 'autosize' in relayout_data or relayout_data == {}:
            return no_update

        try:
            n_books = len(ctx_obj.books)
            default_size = max(6, min(12, 350/n_books))
            patched_fig = Patch()

            if 'xaxis.autorange' in relayout_data or 'yaxis.autorange' in relayout_data:
                patched_fig['layout']['xaxis']['tickfont'] = {'size': default_size}
                patched_fig['layout']['yaxis']['tickfont'] = {'size': default_size}
                patched_fig['layout']['yaxis']['showticklabels'] = False
                patched_fig['layout']['margin']['l'] = 25
                return patched_fig

            # Calculate visible items (simplified from your original logic)
            visible_items = n_books # Replace with your actual x_range/y_range calculation
            
            font_size = 10 if visible_items <= 35 else default_size
            patched_fig['layout']['xaxis']['tickfont'] = {'size': font_size, 'family': 'Arial Narrow, Arial, sans-serif'}
            patched_fig['layout']['yaxis']['tickfont'] = {'size': font_size, 'family': 'Arial Narrow, Arial, sans-serif'}
            patched_fig['layout']['yaxis']['showticklabels'] = visible_items <= 35
            patched_fig['layout']['margin']['l'] = 120 if visible_items <= 35 else 25

            return patched_fig
        except Exception as e:
            print(f"Error adjusting font size: {e}")
            return no_update