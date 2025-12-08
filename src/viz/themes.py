"""
Visualization Themes & Color Palettes
Centralized styling untuk konsistensi visual
"""

import plotly.graph_objects as go
from typing import List, Dict


# ============================================
# COLOR PALETTES
# ============================================

# Main color scheme - Modern & Professional
COLORS = {
    'primary': '#1f77b4',      # Blue
    'secondary': '#ff7f0e',    # Orange
    'success': '#2ca02c',      # Green
    'danger': '#d62728',       # Red
    'warning': '#ff9800',      # Amber
    'info': '#17a2b8',         # Cyan
    'dark': '#2c3e50',         # Dark blue-grey
    'light': '#ecf0f1',        # Light grey
}

# Gradient for heatmaps (Low to High consumption)
HEATMAP_COLORS = [
    '#f7fbff',  # Very light blue
    '#deebf7',  # Light blue
    '#c6dbef',  # Medium light blue
    '#9ecae1',  # Medium blue
    '#6baed6',  # Blue
    '#4292c6',  # Dark blue
    '#2171b5',  # Darker blue
    '#08519c',  # Very dark blue
    '#08306b',  # Deepest blue
]

# Diverging colorscale (for growth rate: negative to positive)
DIVERGING_COLORS = [
    '#d73027',  # Red (negative)
    '#f46d43',
    '#fdae61',
    '#fee090',
    '#ffffbf',  # Yellow (neutral)
    '#e0f3f8',
    '#abd9e9',
    '#74add1',
    '#4575b4',  # Blue (positive)
]

# Choropleth map colors (geographic visualization)
CHOROPLETH_COLORSCALE = [
    [0.0, '#ffffcc'],   # Very light yellow (low)
    [0.2, '#ffeda0'],   # Light yellow
    [0.4, '#fed976'],   # Yellow
    [0.6, '#feb24c'],   # Orange
    [0.8, '#fd8d3c'],   # Dark orange
    [1.0, '#e31a1c'],   # Red (high)
]

# Categorical colors for different regions
REGION_COLORS = {
    'Sumatera': '#1f77b4',
    'Jawa': '#ff7f0e', 
    'Bali & Nusa Tenggara': '#2ca02c',
    'Kalimantan': '#d62728',
    'Sulawesi': '#9467bd',
    'Maluku': '#8c564b',
    'Papua': '#e377c2',
}

# Top provinces highlight colors
TOP_N_COLORS = [
    '#e74c3c',  # Red - #1
    '#e67e22',  # Orange - #2
    '#f39c12',  # Yellow - #3
    '#3498db',  # Blue - #4-10
]


# ============================================
# PLOTLY TEMPLATES
# ============================================

def get_plotly_template() -> Dict:
    """
    Get custom Plotly template untuk konsistensi
    
    Returns:
    --------
    dict : Plotly template configuration
    """
    return {
        'layout': {
            'font': {
                'family': 'Arial, sans-serif',
                'size': 12,
                'color': COLORS['dark']
            },
            'title': {
                'font': {
                    'size': 18,
                    'color': COLORS['dark'],
                    'family': 'Arial Black, sans-serif'
                },
                'x': 0.5,
                'xanchor': 'center'
            },
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'hovermode': 'closest',
            'showlegend': True,
            'legend': {
                'bgcolor': 'rgba(255,255,255,0.8)',
                'bordercolor': COLORS['light'],
                'borderwidth': 1
            }
        }
    }


def apply_theme(fig: go.Figure, template: str = 'plotly_white') -> go.Figure:
    """
    Apply theme ke Plotly figure
    
    Parameters:
    -----------
    fig : go.Figure
        Plotly figure
    template : str
        Template name ('plotly_white', 'plotly', 'seaborn', etc)
    
    Returns:
    --------
    go.Figure : Figure dengan theme applied
    """
    fig.update_layout(
        template=template,
        font=dict(family='Arial, sans-serif', size=12),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    return fig


def get_color_by_rank(rank: int, total: int = 10) -> str:
    """
    Get color berdasarkan ranking (untuk highlight top provinces)
    
    Parameters:
    -----------
    rank : int
        Ranking (1-based)
    total : int
        Total items
    
    Returns:
    --------
    str : Hex color code
    """
    if rank == 1:
        return TOP_N_COLORS[0]  # Red
    elif rank == 2:
        return TOP_N_COLORS[1]  # Orange
    elif rank == 3:
        return TOP_N_COLORS[2]  # Yellow
    else:
        return TOP_N_COLORS[3]  # Blue


def get_gradient_colors(n: int, colorscale: str = 'Blues') -> List[str]:
    """
    Generate gradient colors
    
    Parameters:
    -----------
    n : int
        Number of colors needed
    colorscale : str
        Plotly colorscale name
    
    Returns:
    --------
    list : List of color hex codes
    """
    import plotly.express as px
    colors = px.colors.sample_colorscale(colorscale, [i/(n-1) for i in range(n)])
    return colors


# ============================================
# LAYOUT CONSTANTS
# ============================================

# Figure sizes
FIGURE_SIZES = {
    'small': (800, 400),
    'medium': (1000, 600),
    'large': (1200, 800),
    'wide': (1400, 600),
    'square': (800, 800),
}

# Margins
MARGINS = {
    'tight': dict(l=50, r=50, t=80, b=50),
    'normal': dict(l=80, r=80, t=100, b=80),
    'wide': dict(l=100, r=100, t=120, b=100),
}


# ============================================
# CHART-SPECIFIC CONFIGS
# ============================================

def get_bar_chart_config() -> Dict:
    """Config untuk bar charts"""
    return {
        'marker': {
            'line': {'width': 1, 'color': 'white'}
        },
        'textposition': 'outside',
        'textfont': {'size': 10}
    }


def get_line_chart_config() -> Dict:
    """Config untuk line charts"""
    return {
        'mode': 'lines+markers',
        'line': {'width': 2},
        'marker': {'size': 8}
    }


def get_heatmap_config() -> Dict:
    """Config untuk heatmap"""
    return {
        'colorscale': HEATMAP_COLORS,
        'showscale': True,
        'xgap': 2,
        'ygap': 2,
    }


def get_map_config() -> Dict:
    """Config untuk choropleth map"""
    return {
        'colorscale': CHOROPLETH_COLORSCALE,
        'marker_line_width': 0.5,
        'marker_line_color': 'white',
    }


# ============================================
# UTILITY FUNCTIONS
# ============================================

def format_number(value: float, suffix: str = '') -> str:
    """
    Format number untuk display (dengan koma separator)
    
    Parameters:
    -----------
    value : float
        Number to format
    suffix : str
        Suffix (e.g., 'GWh', '%')
    
    Returns:
    --------
    str : Formatted string
    """
    if value >= 1000:
        return f"{value:,.0f}{suffix}"
    else:
        return f"{value:.2f}{suffix}"


def get_title_format(title: str, subtitle: str = None) -> str:
    """
    Format title dengan subtitle
    
    Parameters:
    -----------
    title : str
        Main title
    subtitle : str, optional
        Subtitle text
    
    Returns:
    --------
    str : Formatted title HTML
    """
    if subtitle:
        return f"<b>{title}</b><br><sub>{subtitle}</sub>"
    return f"<b>{title}</b>"


# Testing
if __name__ == "__main__":
    print("=== Visualization Themes Module ===\n")
    
    print("📊 Available color palettes:")
    print(f"  • Primary colors: {len(COLORS)} colors")
    print(f"  • Heatmap gradient: {len(HEATMAP_COLORS)} steps")
    print(f"  • Region colors: {len(REGION_COLORS)} regions")
    
    print("\n🎨 Figure sizes:")
    for size_name, (width, height) in FIGURE_SIZES.items():
        print(f"  • {size_name}: {width}x{height}px")
    
    print("\n✅ Theme module ready!")