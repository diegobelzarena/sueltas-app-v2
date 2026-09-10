import numpy as np
import plotly.graph_objects as go

def get_book_color(books, book_name):
        """Get color for a specific book from predefined color list"""
        colors = ["#C93232", "#34B5AC", "#1D4C57", "#21754E", "#755D11", "#772777", "#DFB13D", "#C9459F", "#F09D55", "#487BA0", "#6A3A3A", "#5AAE54", "#B15928"]
        book_list = list(books)
        if book_name in book_list:
            book_idx = book_list.index(book_name)
            return colors[book_idx % len(colors)]
        return colors[0]  # Default to first color

def get_printer_colors(printers):
        """Get color mapping for printers - matching heatmap colors/markers"""
        unique_prnts = [prnt for prnt in np.unique(printers) 
                       if prnt not in ['n. nan', 'm. missing', 'Unknown', 'unknown']]
        
        # Use SAME colors and markers as heatmap diagonal markers
        markers = ['circle', 'square', 'triangle-up']
        colors = ["#C93232", "#34B5AC", "#1D4C57", "#21754E", "#755D11", "#772777", "#DFB13D", "#C9459F", "#F09D55", "#487BA0", "#6A3A3A", "#5AAE54", "#B15928"]
        
        prnt_to_color = {}
        prnt_to_marker = {}
        for i, prnt in enumerate(unique_prnts):
            prnt_to_color[prnt] = colors[i % len(colors)]
            prnt_to_marker[prnt] = markers[i % len(markers)]
        
        # Gray for unknown/missing with 0.5 alpha
        prnt_to_color['n. nan'] = 'rgba(128, 128, 128, 0.5)'
        prnt_to_color['m. missing'] = 'rgba(128, 128, 128, 0.5)'
        prnt_to_color['Unknown'] = 'rgba(128, 128, 128, 0.5)'
        prnt_to_color['unknown'] = 'rgba(128, 128, 128, 0.5)'
        prnt_to_marker['n. nan'] = 'x'
        prnt_to_marker['m. missing'] = 'x'
        prnt_to_marker['Unknown'] = 'x'
        prnt_to_marker['unknown'] = 'x'

        return {
                    'colors': prnt_to_color,
                    'markers': prnt_to_marker,
                    'unique_printers': unique_prnts
                }


# Heatmap 

def build_printer_marker_traces(similarity, books, printers, printer_markers):
    """Build printer marker traces on-demand for heatmap."""
    traces = []
    types_diag = np.diagonal(similarity)
    
    for prnt in printer_markers['unique_printers']:
        mask = printers == prnt
        if not np.any(mask):
            continue
        
        trace = go.Scatter(
            x=books[mask],
            y=books[mask],
            mode='markers',
            marker=dict(
                symbol=printer_markers['markers'][prnt],
                size=6,
                color=printer_markers['colors'][prnt],
                line=dict(color='white', width=1)
            ),
            showlegend=True,
            legendgroup=prnt,
            name=prnt,
            customdata=types_diag[mask][:, None],
            hovertemplate=f'Printer: {prnt}<br>Book: %{{x}}<br>Types: %{{customdata[0]}}<extra></extra>'
        )
        traces.append(trace)
    return traces

def glyph_filename(char: str) -> str:
    if char.isupper():
        return f"upper-{char}"
    else:
        return f"lower-{char}"