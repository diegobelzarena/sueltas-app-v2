# callbacks/fonts.py
from dash import Input, Output, State, ctx, no_update

def register_font_callbacks(app, ctx_obj):
    """Font type toggle (Combined/Roman/Italic)."""
    
    # 1. Full, complete styles (prevents buttons from collapsing)
    active_style = {
        'marginRight': '5px', 'padding': '8px 16px', 'fontSize': '12px', 'fontWeight': '500',
        'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#2f4a84', 'color': 'white',
        'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer', 'display': 'inline-flex',
        'alignItems': 'center', 'justifyContent': 'center', 'boxShadow': '0 1px 3px rgba(0,0,0,0.2)',
        'width': '100px', 'minWidth': '100px'
    }
    inactive_style = {
        'marginRight': '5px', 'padding': '8px 16px', 'fontSize': '12px', 'fontWeight': '500',
        'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#DBD1B5', 'color': '#5a5040',
        'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer', 'display': 'inline-flex',
        'alignItems': 'center', 'justifyContent': 'center', 'boxShadow': '0 1px 3px rgba(0,0,0,0.2)',
        'width': '100px', 'minWidth': '100px'
    }
    
    # 2. The last button should not have a right margin to stay perfectly aligned
    active_style_last = {**active_style, 'marginRight': '0'}
    inactive_style_last = {**inactive_style, 'marginRight': '0'}

    @app.callback(
        [Output('font-type-store', 'data'),
         Output('font-combined-btn', 'style'),
         Output('font-roman-btn', 'style'),
         Output('font-italic-btn', 'style')],
        [Input('font-combined-btn', 'n_clicks'),
         Input('font-roman-btn', 'n_clicks'),
         Input('font-italic-btn', 'n_clicks')],
        [State('font-type-store', 'data')],
        prevent_initial_call=True  # Only runs when a button is actually clicked
    )
    def update_font_type(combined_clicks, roman_clicks, italic_clicks, current_font_type):
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update
        
        trigger_id = ctx.triggered_id
        
        if trigger_id == 'font-combined-btn':
            return 'combined', active_style, inactive_style, inactive_style_last
        elif trigger_id == 'font-roman-btn':
            return 'roman', inactive_style, active_style, inactive_style_last
        elif trigger_id == 'font-italic-btn':
            return 'italic', inactive_style, inactive_style, active_style_last
        
        return no_update, no_update, no_update, no_update