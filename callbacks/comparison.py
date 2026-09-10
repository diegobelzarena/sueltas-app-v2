# callbacks/comparison.py
from dash import html, Input, Output, ctx, no_update
from helpers import get_book_color  # Assuming this is your helper

def register_comparison_callbacks(app, ctx_obj):
    
    @app.callback(
        Output('letter-comparison-panel', 'children'),
        [Input('font-type-store', 'data'),
         Input('letter-filter', 'value'),
         Input('additional-books-dropdown', 'value')],
        prevent_initial_call=False
    )
    def update_letter_comparison(font_type, selected_letters, selected_books):
        # 1. Early exits for empty states
        if not selected_books:
            return html.P(
                "Click a cell in the similarity matrix or select books above",
                style={'textAlign': 'center', 'color': '#888', 'marginTop': '150px'}
            )
        
        if not selected_letters:
            return html.P(
                "Select letters above to compare",
                style={'textAlign': 'center', 'color': '#888', 'marginTop': '150px'}
            )
        
        try:
            books = list(selected_books)
            n_books = len(books)
            col_width = f'{100 // n_books}%'
            
            # 2. Build header (book names + printers)
            header_items = []
            for i, book in enumerate(books):
                printer = ctx_obj.printers[i] if ctx_obj.printers[i] not in ['n. nan', 'm. missing', 'unknown'] else 'Unknown'
                color = get_book_color(ctx_obj.books, book)
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                bg = f'rgba({r}, {g}, {b}, 0.35)'
                
                header_items.append(
                    html.Div([
                        html.P(book, style={'fontSize': '10px', 'fontWeight': 'bold', 'margin': '0'}),
                        html.P(printer, style={'fontSize': '9px', 'color': '#666', 'margin': '0'})
                    ], style={
                        'width': col_width, 'textAlign': 'center',
                        'backgroundColor': bg, 'padding': '5px',
                        'borderRadius': '4px', 'boxSizing': 'border-box'
                    })
                )
            
            content = [
                html.Div(header_items, style={'marginBottom': '15px', 'display': 'flex', 'gap': '2px'}),
                html.P(
                    f"Comparing {n_books} book{'s' if n_books > 1 else ''} • Font: {font_type}",
                    style={'textAlign': 'center', 'fontSize': '11px', 'marginBottom': '15px', 'color': '#666'}
                ),
            ]
            
            # 3. Find letters that are BOTH selected AND available
            available_letters = ctx_obj.get_available_letters_for_books(books, font_type)
            letters_to_show = sorted(set(selected_letters) & available_letters)
            
            if not letters_to_show:
                content.append(html.P(
                    f"No {font_type} images found for selected letters",
                    style={'textAlign': 'center', 'color': '#999', 'marginTop': '30px'}
                ))
                return html.Div(content)
            
            # 4. Build the comparison grid
            letters_rendered = 0
            
            for letter in letters_to_show:
                # Collect images for each book
                book_images = [ctx_obj.get_images_for_book_letter(b, letter, font_type) for b in books]
                
                # Skip this letter ENTIRELY if NO book has images for it
                if not any(book_images):
                    continue
                
                letters_rendered += 1
                book_columns = []
                
                for book, img_urls in zip(books, book_images):
                    # STRICT CHECK: If the list is empty, render a clean placeholder 
                    # to maintain column alignment without showing a broken image box.
                    if not img_urls:
                        color = get_book_color(ctx_obj.books, book)
                        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                        bg = f'rgba({r}, {g}, {b}, 0.35)'
                        
                        book_columns.append(
                            html.Div(
                                html.Span("—", style={'color': '#999', 'fontSize': '24px', 'fontWeight': 'bold'}),
                                style={
                                    'width': col_width, 'textAlign': 'center',
                                    'backgroundColor': bg, 'padding': '5px',
                                    'borderRadius': '4px', 'boxSizing': 'border-box'
                                }
                            )
                        )
                        continue
                    
                    # Filter to ensure we ONLY pass valid base64 strings to html.Img
                    valid_imgs = [url for url in img_urls if isinstance(url, str) and url.startswith('data:image')]
                    
                    if not valid_imgs:
                        continue # Skip if filtering removed everything
                    
                    color = get_book_color(ctx_obj.books, book)
                    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                    bg = f'rgba({r}, {g}, {b}, 0.35)'
                    
                    imgs = [
                        html.Img(src=url, style={
                            'height': '70px', 'margin': '2px',
                            'border': '2px solid #ccc', 'borderRadius': '4px',
                            'backgroundColor': '#fff'     # Keep this for clean transparency handling
                        })
                        for url in valid_imgs
                    ]
                    
                    book_columns.append(
                        html.Div(imgs, style={
                            'width': col_width, 'textAlign': 'center',
                            'backgroundColor': bg, 'padding': '5px',
                            'borderRadius': '4px', 'boxSizing': 'border-box'
                        })
                    )
                
                # This is the part that was broken in the previous response:
                content.append(
                    html.Div([
                        html.H5(
                            f"'{letter}'",
                            style={'marginBottom': '8px', 'textAlign': 'center',
                                   'fontSize': '14px', 'fontWeight': 'bold'}
                        ),
                        html.Div(book_columns, style={
                            'marginBottom': '12px', 'paddingBottom': '12px',
                            'borderBottom': '1px solid #eee',
                            'display': 'flex', 'gap': '2px'
                        })
                    ])
                )
            
            if letters_rendered == 0:
                content.append(html.P(
                    "Selected letters have no images for these books.",
                    style={'textAlign': 'center', 'color': '#f59e0b', 'marginTop': '30px'}
                ))
            
            return html.Div(content, style={'maxHeight': '600px', 'overflowY': 'auto', 'padding': '10px'})
        
        except Exception as e:
            import traceback
            print(f"ERROR in update_letter_comparison: {e}\n{traceback.format_exc()}")
            return html.Div([
                html.P(f"Error loading comparison: {str(e)}",
                      style={'textAlign': 'center', 'color': '#ef4444', 'padding': '20px'})
            ])