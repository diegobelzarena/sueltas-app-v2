import dash
from layout import setup_layout

from context import DashboardContext
from callbacks.core_viz import register_core_visualization_callbacks
from callbacks.fonts import register_font_callbacks
from callbacks.filters import register_filter_callbacks
from callbacks.network import register_network_callbacks
from callbacks.heatmap import register_heatmap_callbacks
from callbacks.comparison import register_comparison_callbacks
from callbacks.export import register_export_and_comparison_callbacks

# 1. Initialize App
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# 2. Create the lightweight context object (loads all data once)
ctx_obj = DashboardContext()

# 3. Register callbacks modularly
register_core_visualization_callbacks(app, ctx_obj)
register_font_callbacks(app, ctx_obj)
register_filter_callbacks(app, ctx_obj)
register_network_callbacks(app, ctx_obj)
register_heatmap_callbacks(app, ctx_obj)
register_comparison_callbacks(app, ctx_obj)
register_export_and_comparison_callbacks(app, ctx_obj)

# 5. Define layout
app.layout = setup_layout(ctx_obj)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)