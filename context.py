import dash
import numpy as np
from helpers import get_book_color, get_printer_colors, build_printer_marker_traces, glyph_filename
import plotly.graph_objects as go
from pathlib import Path
import pickle

DATA_DIR = Path("data")
IMGS_DIR = Path("data/images")

FONTS =  ["combined", "roman", "italic"]


class DashboardContext:
    """Holds shared read-only data and pure helper methods."""
    #  Centralized Theme
    THEME = {
        'bg_color': '#F8F5EC',
        'text_color': '#374151',
        'accent_color': '#887C57',
        'font_family': 'Inter, Arial, sans-serif',
    }

    def __init__(self):
        self._load_data()
        self.printer_markers = get_printer_colors(self.printers)
        

        # Button styles for toggle buttons (network panel)
        self.active_btn_style = {
            'padding': '8px 16px', 'fontSize': '12px', 'fontWeight': '500',
            'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#2f4a84', 'color': 'white',
            'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer', 'display': 'inline-flex',
            'alignItems': 'center', 'justifyContent': 'center', 'boxShadow': '0 1px 3px rgba(0,0,0,0.2)',
            'transition': 'background-color 0.15s ease, transform 0.05s ease', 'lineHeight': '1',
            'width': '120px', 'minWidth': '120px', 'maxWidth': '120px'
        }
        self.inactive_btn_style = {
            'padding': '8px 16px', 'fontSize': '12px', 'fontWeight': '500',
            'fontFamily': 'Inter, Arial, sans-serif', 'backgroundColor': '#DBD1B5', 'color': '#5a5040',
            'border': 'none', 'borderRadius': '6px', 'cursor': 'pointer', 'display': 'inline-flex',
            'alignItems': 'center', 'justifyContent': 'center', 'boxShadow': '0 1px 3px rgba(0,0,0,0.2)',
            'transition': 'background-color 0.15s ease, transform 0.05s ease', 'lineHeight': '1',
            'width': '120px', 'minWidth': '120px', 'maxWidth': '120px'
        }

    def _load_data(self):
        self.books = np.load(DATA_DIR / "book_names.npy")
        self.printers = np.load(DATA_DIR / "printer_names.npy")
        self.symbols = np.load(DATA_DIR / "symbols.npy")
        
        self.similarity_matrices = {
            "combined": np.load(DATA_DIR / "similarity_combined.npy"),
            "roman": np.load(DATA_DIR / "similarity_roman.npy"),
            "italic": np.load(DATA_DIR / "similarity_italic.npy")
        }
        
        self.umap_positions = {
            "combined": np.load(DATA_DIR / "umap_combined.npy"),
            "roman": np.load(DATA_DIR / "umap_roman.npy"),
            "italic": np.load(DATA_DIR / "umap_italic.npy")
        }
        
        with open(DATA_DIR / "edges.pkl", "rb") as f:
            self.edges = pickle.load(f)
            
        # Load the precomputed image cache
        with open(DATA_DIR / "image_cache.pkl", "rb") as f:
            self.image_cache = pickle.load(f)
        
        # Build secondary index for fast "available letters" queries
        # Structure: {(book, font): {letters}}
        self._letters_index = {}
        for (book, font, letter) in self.image_cache.keys():
            key = (book, font)
            if key not in self._letters_index:
                self._letters_index[key] = set()
            self._letters_index[key].add(letter[-1:])
        

    def create_heatmap(self, font="combined"):
        """Create similarity matrix heatmap matching notebook style."""     
           
        similarity = self.similarity_matrices[font]
        n_books = len(self.books)
        
        # 1. Create the main heatmap
        fig = go.Figure(data=go.Heatmap(
            z=similarity,
            x=self.books,
            y=self.books,
            colorscale='viridis',
            reversescale=False,
            hoverongaps=False,
            hovertemplate=(
                'Book 1: %{y}<br>'
                'Book 2: %{x}<br>'
                'Shared Types: %{z:.0f}<extra></extra>'
            ),
            showscale=False
        ))
        
        # 2. Add printer marker traces 
        marker_traces = build_printer_marker_traces(similarity, self.books, self.printers, self.printer_markers)
        for trace in marker_traces:
            fig.add_trace(trace)
        
        # 3. Clean layout - responsive sizing, no tick labels
        fig.update_layout(
            title=None,
            autosize=True,
            uirevision='constant',
            xaxis=dict(
                title="", side="bottom", showgrid=False, showticklabels=False,
                automargin=False, fixedrange=False, constrain='domain',
                categoryorder='array', categoryarray=self.books
            ),
            yaxis=dict(
                title="", showgrid=False, showticklabels=False,
                autorange='reversed', constrain="domain", automargin=False,
                fixedrange=False, categoryorder='array', categoryarray=self.books,
                scaleanchor="x", scaleratio=1
            ),
            margin=dict(l=25, r=25, t=15, b=15),
            
            # Use centralized theme colors
            plot_bgcolor=self.THEME['bg_color'],
            paper_bgcolor=self.THEME['bg_color'],
            
            legend=dict(
                title=dict(
                    text="<b>Printers:</b>",
                    font=dict(size=10, family=self.THEME['font_family'], color=self.THEME['accent_color']),
                    side="left"
                ),
                orientation="h",
                xanchor='center', x=0.5, y=0.02, yanchor='top',
                # 90% opacity of the background color (E6 in hex)
                bgcolor="rgba(248,245,236,0.9)", 
                borderwidth=0,
                font=dict(size=9, family=self.THEME['font_family'], color=self.THEME['text_color']),
                itemclick="toggle",
                itemdoubleclick="toggleothers",
                tracegroupgap=1,
            )
        )
        
        return fig
    
    # --- Pure Helper Methods ---
    def create_network_graph(self, umap_positions, edges_data, edge_opacity=1.0,marker_size=12,
                            label_size=8):
        """ Create network graph from weight matrix with UMAP positioning and printer colors
        
        Args:
            umap_positions: numpy array of UMAP coordinates 
            edges_data: precomputed edges data
        """
        
        edges = edges_data['top_edges']
        bins = edges_data['binned_edges']
                
        # Get printer colors and markers (matching heatmap)
        prnt_to_color = self.printer_markers['colors']
        prnt_to_marker = self.printer_markers['markers']
        unique_prnts = self.printer_markers['unique_printers']
                
        
        # Create figure
        fig = go.Figure()
                
        for bin_idx in range(10):  # n_bins
            bin_data = bins.get(bin_idx, {'edges': [], 'avg_w': 0})
            edges_in_bin = bin_data['edges']
            avg_w = bin_data['avg_w']
            if not edges_in_bin:
                continue
            x_all = []
            y_all = []
            for i, j in edges_in_bin:
                x0, y0 = umap_positions[i]
                x1, y1 = umap_positions[j]
                x_all.extend([x0, x1, None])
                y_all.extend([y0, y1, None])
            opacity = min(1.0, avg_w * edge_opacity)
            color = f'rgba(100,100,100,{opacity})'
            fig.add_trace(go.Scatter(
                x=x_all,
                y=y_all,
                mode='lines',
                line=dict(width=1, color=color),
                showlegend=False,
                name=f'bin_{bin_idx}',
                customdata=[avg_w],  # Store average weight for updating
                hoverinfo='skip'
            ))
        
        # Add nodes for unknown/missing printers with 0.5 alpha and no label
        unknown_mask = np.isin(self.printers, ['n. nan', 'm. missing', 'Unknown', 'unknown'])
        if np.any(unknown_mask):
            node_x = umap_positions[unknown_mask][:, 0].tolist()
            node_y = umap_positions[unknown_mask][:, 1].tolist()
            node_labels = ['' for _ in range(unknown_mask.sum())]
            
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    symbol='circle',  # Circle marker for unknown
                    size=int(marker_size * 1 / 2),
                    color='rgba(128, 128, 128, 0.5)',  # 0.5 alpha
                    line=dict(width=1, color='white')
                ),
                text=node_labels,
                textposition='top center',
                textfont=dict(size=int(label_size * 1 / 2), color='rgba(128, 128, 128, 0.5)'),
                hovertemplate='<b>%{customdata}</b><br>Printer: Unknown<extra></extra>',
                customdata=self.books[unknown_mask],
                name='Unknown',
                legendgroup='Unknown',
                showlegend=True
            ))

        # Add nodes colored by printer, one trace per printer for legend
        # Using same colors and markers as heatmap diagonal
        for prnt in unique_prnts:
            node_mask = self.printers == prnt
            if not np.any(node_mask):
                continue
            
            node_x = umap_positions[node_mask][:, 0].tolist()
            node_y = umap_positions[node_mask][:, 1].tolist()
            # node_text = [f"{self.books[i]}<br>Printer: {self.prnt_names[i]}" 
            #             for i in np.where(node_mask)[0]]
            # Show printer name as label on top of nodes
            node_labels = [prnt for _ in np.where(node_mask)[0]]
            
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    symbol=prnt_to_marker.get(prnt, 'circle'),  # Match heatmap marker
                    size=marker_size,
                    color=prnt_to_color[prnt],
                    line=dict(width=1, color='white')
                ),
                text=node_labels,
                textposition='top center',
                textfont=dict(
                    size=label_size, 
                    color=prnt_to_color[prnt],
                    family='Arial, bold'  # Bold font
                ),
                customdata=np.stack((self.books[node_mask], self.printers[node_mask]), axis=-1),
                hovertemplate='<b>%{customdata[0]}</b><br>Printer: %{customdata[1]}<extra></extra>',
                name=prnt,
                legendgroup=prnt,
                showlegend=True
            ))
        
        
        fig.update_layout(
            title=None,
            showlegend=True,
            legend=dict(
                title=dict(
                    text="<span style='font-weight:600'>  Printers  </span>",
                    font=dict(size=13, family="Inter, Arial, sans-serif", color="#887C57")
                ),
                x=1.02,
                y=1,
                bgcolor="#F8F5EC",
                bordercolor="#d1c7ad",
                borderwidth=1,
                font=dict(size=11, family="Inter, Arial, sans-serif", color="#374151"),
                itemclick="toggle",
                itemdoubleclick="toggleothers",
                tracegroupgap=1,
                itemsizing="constant"

            ),
            hovermode="closest",
            margin=dict(b=20, l=5, r=160, t=20),
            annotations=[
                dict(
                    text="Node color = printer · Edge opacity controlled by slider",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.005,
                    y=-0.02,
                    xanchor="left",
                    yanchor="bottom",
                    font=dict(
                        color="#6b7280",
                        size=10,
                        family="Inter, Arial, sans-serif"
                    ),
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="y"),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="#F8F5EC",
            paper_bgcolor="#F8F5EC",
        )

        
        return fig


    def update_network_edges(self, current_fig, edge_opacity, umap_positions, font_type, selected_books=None):
        """Update edge traces in the network figure for new weight_matrix and threshold, keeping node traces.
        
        Args:
            umap_pos_array: numpy array of UMAP positions (not list)
            selected_books: list of selected book names to recreate edges for (default None)
        """

        # Use binned edges for the font type
        bins = self.edges[font_type]['binned_edges']
        
        # Use Patch for efficient update
        patched = dash.Patch()
        
        # Use provided selected_books or default to empty list
        if selected_books is None:
            selected_books = []
        
        # Update bin traces and remove selected_edge_ traces
        for i, trace in enumerate(current_fig['data']):
            if trace['name'].startswith('bin_'):
                bin_idx = int(trace['name'].split('_')[1])
                bin_data = bins.get(bin_idx, {'edges': [], 'avg_w': 0})
                edges_in_bin = bin_data['edges']
                avg_w = bin_data['avg_w']
                if not edges_in_bin:
                    patched['data'][i]['x'] = []
                    patched['data'][i]['y'] = []
                    patched['data'][i]['line']['color'] = 'rgba(100,100,100,0)'
                else:
                    x_all = []
                    y_all = []
                    for edge_i, edge_j in edges_in_bin:
                        x0, y0 = umap_positions[edge_i]
                        x1, y1 = umap_positions[edge_j]
                        x_all.extend([x0, x1, None])
                        y_all.extend([y0, y1, None])
                    opacity = min(1.0, avg_w * edge_opacity)
                    color = f'rgba(100,100,100,{opacity})'
                    patched['data'][i]['x'] = x_all
                    patched['data'][i]['y'] = y_all
                    patched['data'][i]['line']['color'] = color
            elif trace['name'].startswith('selected_edge_'):
                # Remove selected edges - they will be recreated
                patched['data'][i]['x'] = []
                patched['data'][i]['y'] = []
        
        # Recreate selected book edges with new font type
        if selected_books:
            book_list = list(self.books)
            for book in selected_books:
                if book in book_list:
                    book_idx = book_list.index(book)
                    book_color = get_book_color(self.books, book)
                    
                    # Convert hex to RGB
                    r = int(book_color[1:3], 16)
                    g = int(book_color[3:5], 16)
                    b = int(book_color[5:7], 16)
                    
                    # Add edges for this book from binned edges
                    for bin_idx in range(10):
                        bin_data = bins.get(bin_idx, {'edges': [], 'avg_w': 0})
                        edges_in_bin = bin_data['edges']
                        avg_w = bin_data['avg_w']
                        
                        if not edges_in_bin:
                            continue
                        
                        # Vectorize edge filtering
                        edges_array = np.array(edges_in_bin)
                        mask = (edges_array[:, 0] == book_idx) | (edges_array[:, 1] == book_idx)
                        matching_edges = edges_array[mask]
                        
                        if len(matching_edges) > 0:
                            edges_x = []
                            edges_y = []
                            for i, j in matching_edges:
                                edges_x.extend([umap_positions[i, 0], umap_positions[j, 0], None])
                                edges_y.extend([umap_positions[i, 1], umap_positions[j, 1], None])
                            
                            # Selected edges use avg_w directly for opacity (not affected by edge_opacity slider)
                            opacity = min(1.0, avg_w)
                            color = f'rgba({r},{g},{b},{opacity})'
                            patched['data'].append({
                                'type': 'scatter',
                                'x': edges_x,
                                'y': edges_y,
                                'mode': 'lines',
                                'line': {'width': 1, 'color': color},
                                'showlegend': False,
                                'customdata': [avg_w],
                                'name': f'selected_edge_{book}_bin{bin_idx}',
                                'hoverinfo': 'skip'
                            })
        
        return patched
    
    def get_available_letters_for_books(self, books: list, font_type: str) -> set:
        """Fast lookup: which letters exist across selected books for this font?"""
        available = set()
        for book in books:
            if font_type != "combined":
                available.update(self._letters_index.get((book, font_type), set()))
            else:
                available.update(self._letters_index.get((book, "roman"), set()))
                available.update(self._letters_index.get((book, "italic"), set()))
        return available
    
    def get_images_for_book_letter(self, book: str, letter: str, font_type: str) -> list:
        """Returns a flat list of ready-to-use Base64 data URIs."""
        glyph = glyph_filename(letter)
        
        if font_type != "combined":
            return self.image_cache.get((book, font_type, glyph), [])
        else:
            # Combine roman and italic. Use '+' to create a new flat list, 
            # preventing nested lists like [['data:...'], []]
            roman_imgs = self.image_cache.get((book, "roman", glyph), [])
            italic_imgs = self.image_cache.get((book, "italic", glyph), [])
            return roman_imgs + italic_imgs
