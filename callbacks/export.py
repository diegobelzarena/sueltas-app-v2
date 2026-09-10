# callbacks/export.py
import json
from datetime import datetime
from dash import Input, Output, State, ctx, no_update, html

def register_export_and_comparison_callbacks(app, ctx_obj):
    
    @app.callback(
        [Output('export-status', 'children'),
         Output('download-html', 'data')],
        [Input('export-html-btn', 'n_clicks')],
        [State('font-type-store', 'data'),
         State('similarity-heatmap', 'figure'),
         State('network-graph', 'figure')]
    )
    def export_data(html_clicks, font_type, heatmap_fig, network_fig):
        if not html_clicks:
            return "", None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        threshold = getattr(ctx_obj, 'threshold', 0.1) # Fixed the undefined variable bug
        
        if font_type == 'roman':
            n1hat = ctx_obj.n1hat_rm
        elif font_type == 'italic':
            n1hat = ctx_obj.n1hat_it
        else:
            n1hat = ctx_obj.n1hat_combined
        
        total_connections = int((n1hat > threshold).sum())
        connected_books = int(len((n1hat > threshold).sum(axis=0).nonzero()[0]))
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<title>Book Typography Similarity Analysis - {timestamp}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
<h1>Book Typography Similarity Analysis ({font_type})</h1>
<p>Threshold: {threshold} | Connections: {total_connections} | Books: {connected_books}</p>
<div id="heatmap"></div>
<div id="network"></div>
<script>
    Plotly.newPlot('heatmap', {json.dumps(heatmap_fig)});
    Plotly.newPlot('network', {json.dumps(network_fig)});
</script>
</body>
</html>"""
        
        filename = f'dashboard_export_{font_type}_{timestamp}.html'
        return html.P("✅ HTML export ready!", style={'color': 'green'}), dict(content=html_content, filename=filename)