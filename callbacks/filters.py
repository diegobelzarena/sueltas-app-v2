# callbacks/filters.py
from dash import Input, Output, State, ctx, no_update, Patch
from helpers import get_book_color

def register_filter_callbacks(app, ctx_obj):
    
    @app.callback(
        [Output('letter-filter', 'options'),
         Output('letter-filter', 'value'),
         Output('printer-filter-dropdown', 'options')],
        [Input('font-type-store', 'data')],
        [State('letter-filter', 'value')],
        prevent_initial_call=False
    )
    def init_filters(_, current_selected):
        letter_options = [{'label': f' {l}', 'value': l} for l in ctx_obj.symbols]
        if current_selected and isinstance(current_selected, list):
            preserved = [l for l in current_selected if l in ctx_obj.symbols]
            selected = preserved if preserved else ctx_obj.symbols
        else:
            selected = ctx_obj.symbols

        unique_printers = sorted(set(ctx_obj.printers))
        printer_options = [{'label': p, 'value': p} for p in unique_printers if p not in ['n. nan', 'm. missing']]
        return letter_options, selected, printer_options

    @app.callback(
        Output('additional-books-dropdown', 'options'),
        [Input('printer-filter-dropdown', 'value')],
        prevent_initial_call=False
    )
    def filter_books_by_printer(selected_printer):
        book_options = []
        for i, b in enumerate(ctx_obj.books):
            printer = ctx_obj.printers[i] if ctx_obj.printers[i] not in ['n. nan', 'm. missing', 'unknown'] else 'Unknown'
            if selected_printer is None or printer == selected_printer:
                book_options.append({'label': f"{b} ({printer})", 'value': b})
        return sorted(book_options, key=lambda x: x['label'])

    @app.callback(
        [Output('clicked-books-store', 'data', allow_duplicate=True),
         Output('additional-books-dropdown', 'value', allow_duplicate=True)],
        [Input('similarity-heatmap', 'clickData'),
         Input('clear-comparison-btn', 'n_clicks')],
        [State('clicked-books-store', 'data'),
         State('additional-books-dropdown', 'value')],
        prevent_initial_call=True
    )
    def handle_matrix_click_and_clear(click_data, clear_clicks, stored_books, dropdown_books):
        if not ctx.triggered:
            return no_update, no_update
        
        trigger_id = ctx.triggered_id
        if trigger_id == 'clear-comparison-btn':
            return [], []
        
        if trigger_id == 'similarity-heatmap' and click_data is not None:
            x_label = click_data['points'][0]['x']
            y_label = click_data['points'][0]['y']
            book1 = x_label.split(' | ')[0] if ' | ' in x_label else x_label
            book2 = y_label.split(' | ')[0] if ' | ' in y_label else y_label
            
            if book1 == book2:
                current_books = list(dropdown_books) if dropdown_books else []
                if book1 not in current_books:
                    current_books.append(book1)
                return current_books, current_books
            else:
                return [book1, book2], [book1, book2]
        
        return no_update, no_update

    @app.callback(
        Output('similarity-heatmap', 'figure', allow_duplicate=True),
        [Input('additional-books-dropdown', 'value')],
        [State('similarity-heatmap', 'figure')],
        prevent_initial_call=True
    )
    def update_matrix_overlays(selected_books, current_fig):
        if current_fig is None:
            return no_update
        
        patched_fig = Patch()
        data_to_keep = [trace for trace in current_fig.get('data', []) if not trace.get('name', '').startswith('overlay_')]
        patched_fig['data'] = data_to_keep
        
        if selected_books:
            book_list = list(ctx_obj.books)
            for book in selected_books:
                if book in book_list:
                    color = get_book_color(ctx_obj.books, book)
                    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                    overlay_color = f'rgba({r}, {g}, {b}, 0.35)'
                    
                    patched_fig['data'].append({
                        'type': 'scatter', 'x': [book_list[0], book_list[-1]], 'y': [book, book],
                        'mode': 'lines', 'line': {'color': overlay_color, 'width': 3},
                        'showlegend': False, 'hoverinfo': 'skip', 'name': f'overlay_row_{book}'
                    })
                    patched_fig['data'].append({
                        'type': 'scatter', 'x': [book, book], 'y': [book_list[0], book_list[-1]],
                        'mode': 'lines', 'line': {'color': overlay_color, 'width': 3},
                        'showlegend': False, 'hoverinfo': 'skip', 'name': f'overlay_col_{book}'
                    })
        return patched_fig