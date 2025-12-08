"""
Chart Visualization Module
Reusable functions untuk berbagai jenis charts
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, List, Tuple
import numpy as np

from .themes import (
    COLORS, HEATMAP_COLORS, CHOROPLETH_COLORSCALE,
    get_plotly_template, apply_theme, get_color_by_rank,
    FIGURE_SIZES, MARGINS, format_number, get_title_format
)


# ============================================
# BAR CHARTS
# ============================================

def create_horizontal_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    subtitle: str = None,
    top_n: int = None,
    color_by_rank: bool = True,
    show_values: bool = True,
    height: int = 800
) -> go.Figure:
    """
    Create horizontal bar chart (untuk ranking provinsi)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data source
    x_col : str
        Column untuk x-axis (values)
    y_col : str
        Column untuk y-axis (categories)
    title : str
        Chart title
    subtitle : str, optional
        Subtitle
    top_n : int, optional
        Show only top N rows
    color_by_rank : bool
        Use different colors for top 3
    show_values : bool
        Show value labels
    height : int
        Figure height
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    # Filter top N if specified
    df_plot = df.copy()
    if top_n:
        df_plot = df_plot.nlargest(top_n, x_col)
    
    # Sort by value (ascending for horizontal bar)
    df_plot = df_plot.sort_values(x_col, ascending=True)
    
    # Assign colors
    if color_by_rank:
        n = len(df_plot)
        colors = [get_color_by_rank(n - i, n) for i in range(n)]
    else:
        colors = COLORS['primary']
    
    # Create figure
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_plot[x_col],
        y=df_plot[y_col],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(width=1, color='white')
        ),
        text=df_plot[x_col].apply(lambda x: format_number(x, ' GWh')) if show_values else None,
        textposition='outside',
        textfont=dict(size=10),
        hovertemplate='<b>%{y}</b><br>%{x:,.2f} GWh<extra></extra>'
    ))
    
    # Layout
    fig.update_layout(
        title=get_title_format(title, subtitle),
        xaxis_title='Konsumsi Listrik (GWh)',
        yaxis_title='',
        height=height,
        margin=MARGINS['normal'],
        showlegend=False,
        plot_bgcolor='white',
        hovermode='closest'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
    
    return apply_theme(fig)


def create_grouped_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    group_col: str,
    title: str,
    subtitle: str = None,
    height: int = 600
) -> go.Figure:
    """
    Create grouped bar chart (untuk perbandingan multi-tahun)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data source
    x_col : str
        X-axis column (categories)
    y_col : str
        Y-axis column (values)
    group_col : str
        Column untuk grouping (e.g., 'Year')
    title : str
        Chart title
    subtitle : str, optional
        Subtitle
    height : int
        Figure height
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=group_col,
        barmode='group',
        title=get_title_format(title, subtitle),
        labels={y_col: 'Konsumsi Listrik (GWh)'},
        height=height
    )
    
    fig.update_layout(
        margin=MARGINS['normal'],
        plot_bgcolor='white',
        hovermode='x unified'
    )
    
    return apply_theme(fig)


# ============================================
# LINE CHARTS
# ============================================

def create_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    group_col: str = None,
    title: str = '',
    subtitle: str = None,
    height: int = 600,
    show_markers: bool = True
) -> go.Figure:
    """
    Create line chart (untuk tren time series)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data source
    x_col : str
        X-axis column (usually 'Year')
    y_col : str
        Y-axis column (values)
    group_col : str, optional
        Column untuk multiple lines (e.g., 'Province')
    title : str
        Chart title
    subtitle : str, optional
        Subtitle
    height : int
        Figure height
    show_markers : bool
        Show markers on lines
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        color=group_col,
        markers=show_markers,
        title=get_title_format(title, subtitle),
        labels={y_col: 'Konsumsi Listrik (GWh)'},
        height=height
    )
    
    fig.update_traces(
        mode='lines+markers' if show_markers else 'lines',
        line=dict(width=2),
        marker=dict(size=8)
    )
    
    fig.update_layout(
        margin=MARGINS['normal'],
        plot_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='left',
            x=1.02
        )
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')
    
    return apply_theme(fig)


def create_area_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    group_col: str = None,
    title: str = '',
    subtitle: str = None,
    height: int = 600
) -> go.Figure:
    """
    Create area chart (stacked area untuk komposisi)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data source
    x_col : str
        X-axis column
    y_col : str
        Y-axis column
    group_col : str, optional
        Column untuk stacking
    title : str
        Chart title
    subtitle : str, optional
        Subtitle
    height : int
        Figure height
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    fig = px.area(
        df,
        x=x_col,
        y=y_col,
        color=group_col,
        title=get_title_format(title, subtitle),
        labels={y_col: 'Konsumsi Listrik (GWh)'},
        height=height
    )
    
    fig.update_layout(
        margin=MARGINS['normal'],
        plot_bgcolor='white',
        hovermode='x unified'
    )
    
    return apply_theme(fig)


# ============================================
# HEATMAP
# ============================================

def create_heatmap(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    value_col: str,
    title: str = '',
    subtitle: str = None,
    colorscale: List = None,
    height: int = 800,
    show_values: bool = True
) -> go.Figure:
    """
    Create heatmap (untuk tren multi-tahun per provinsi)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data source
    x_col : str
        X-axis column (e.g., 'Year')
    y_col : str
        Y-axis column (e.g., 'Province')
    value_col : str
        Value column untuk color intensity
    title : str
        Chart title
    subtitle : str, optional
        Subtitle
    colorscale : list, optional
        Custom colorscale
    height : int
        Figure height
    show_values : bool
        Show values in cells
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    # Pivot data untuk heatmap
    pivot_df = df.pivot(index=y_col, columns=x_col, values=value_col)
    
    # Use custom colorscale or default
    if colorscale is None:
        colorscale = HEATMAP_COLORS
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale=colorscale,
        text=pivot_df.values.round(2) if show_values else None,
        texttemplate='%{text}' if show_values else None,
        textfont=dict(size=9),
        hovertemplate='<b>%{y}</b><br>Tahun: %{x}<br>Konsumsi: %{z:,.2f} GWh<extra></extra>',
        colorbar=dict(title='GWh')
    ))
    
    fig.update_layout(
        title=get_title_format(title, subtitle),
        xaxis_title='Tahun',
        yaxis_title='',
        height=height,
        margin=MARGINS['normal']
    )
    
    return apply_theme(fig)


# ============================================
# DISTRIBUTION CHARTS
# ============================================

def create_histogram(
    df: pd.DataFrame,
    column: str,
    title: str = '',
    subtitle: str = None,
    bins: int = 30,
    height: int = 500
) -> go.Figure:
    """
    Create histogram (untuk distribusi konsumsi)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data source
    column : str
        Column untuk histogram
    title : str
        Chart title
    subtitle : str, optional
        Subtitle
    bins : int
        Number of bins
    height : int
        Figure height
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    fig = px.histogram(
        df,
        x=column,
        nbins=bins,
        title=get_title_format(title, subtitle),
        labels={column: 'Konsumsi Listrik (GWh)'},
        height=height
    )
    
    fig.update_traces(
        marker=dict(color=COLORS['primary'], line=dict(width=1, color='white'))
    )
    
    fig.update_layout(
        margin=MARGINS['tight'],
        plot_bgcolor='white',
        showlegend=False,
        yaxis_title='Frekuensi'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')
    
    return apply_theme(fig)


def create_boxplot(
    df: pd.DataFrame,
    y_col: str,
    x_col: str = None,
    title: str = '',
    subtitle: str = None,
    height: int = 500
) -> go.Figure:
    """
    Create boxplot (untuk melihat outliers dan distribusi)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data source
    y_col : str
        Y-axis column (values)
    x_col : str, optional
        X-axis column (groups, e.g., 'Year')
    title : str
        Chart title
    subtitle : str, optional
        Subtitle
    height : int
        Figure height
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    fig = px.box(
        df,
        x=x_col,
        y=y_col,
        title=get_title_format(title, subtitle),
        labels={y_col: 'Konsumsi Listrik (GWh)'},
        height=height
    )
    
    fig.update_traces(
        marker=dict(color=COLORS['primary']),
        line=dict(width=2)
    )
    
    fig.update_layout(
        margin=MARGINS['tight'],
        plot_bgcolor='white',
        showlegend=False
    )
    
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')
    
    return apply_theme(fig)


# ============================================
# SMALL MULTIPLES
# ============================================

def create_small_multiples(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    facet_col: str,
    title: str = '',
    subtitle: str = None,
    height: int = 800,
    cols: int = 2
) -> go.Figure:
    """
    Create small multiples (untuk perbandingan banyak kategori)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data source
    x_col : str
        X-axis column
    y_col : str
        Y-axis column
    facet_col : str
        Column untuk faceting (e.g., 'Province')
    title : str
        Chart title
    subtitle : str, optional
        Subtitle
    height : int
        Figure height
    cols : int
        Number of columns
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        facet_col=facet_col,
        facet_col_wrap=cols,
        title=get_title_format(title, subtitle),
        labels={y_col: 'GWh'},
        height=height,
        markers=True
    )
    
    fig.update_traces(line=dict(width=2), marker=dict(size=6))
    
    fig.update_layout(
        margin=MARGINS['tight'],
        showlegend=False
    )
    
    return apply_theme(fig)


# Testing
if __name__ == "__main__":
    print("=== Charts Module Test ===\n")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'Province': ['DKI JAKARTA', 'JAWA BARAT', 'JAWA TIMUR', 'JAWA TENGAH', 'BANTEN'],
        'Electricity_GWh': [32000, 49500, 37600, 25000, 22200],
        'Year': [2023] * 5
    })
    
    print("✅ Sample data created")
    print(sample_data)
    
    print("\n📊 Available chart functions:")
    print("  • create_horizontal_bar_chart()")
    print("  • create_grouped_bar_chart()")
    print("  • create_line_chart()")
    print("  • create_area_chart()")
    print("  • create_heatmap()")
    print("  • create_histogram()")
    print("  • create_boxplot()")
    print("  • create_small_multiples()")
    
    print("\n✅ Charts module ready!")