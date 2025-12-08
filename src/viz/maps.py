"""
Map Visualization Module
Functions untuk choropleth maps dan geospatial visualization
"""

import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, Dict, Tuple
import json

from .themes import (
    CHOROPLETH_COLORSCALE, COLORS,
    get_title_format, FIGURE_SIZES, MARGINS,
    apply_theme, format_number
)


# ============================================
# CHOROPLETH MAP
# ============================================

def create_choropleth_map(
    gdf: gpd.GeoDataFrame,
    value_col: str,
    province_col: str = 'Propinsi',
    title: str = '',
    subtitle: str = None,
    colorscale: list = None,
    height: int = 800,
    show_colorbar: bool = True,
    center: Dict = None,
    zoom: float = 3.5
) -> go.Figure:
    """
    Create choropleth map menggunakan Plotly
    
    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame dengan geometri dan data
    value_col : str
        Column untuk color intensity
    province_col : str
        Column nama provinsi
    title : str
        Map title
    subtitle : str, optional
        Subtitle
    colorscale : list, optional
        Custom colorscale
    height : int
        Figure height
    show_colorbar : bool
        Show colorbar legend
    center : dict, optional
        Map center {'lat': x, 'lon': y}
    zoom : float
        Initial zoom level
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    # Use custom colorscale or default
    if colorscale is None:
        colorscale = CHOROPLETH_COLORSCALE
    
    # Convert GeoDataFrame to GeoJSON
    gdf_plot = gdf.copy()
    
    # Handle missing values
    if gdf_plot[value_col].isna().any():
        gdf_plot[value_col] = gdf_plot[value_col].fillna(0)
    
    # Create figure using Plotly Express (easier for choropleth)
    fig = px.choropleth_mapbox(
        gdf_plot,
        geojson=gdf_plot.geometry.__geo_interface__,
        locations=gdf_plot.index,
        color=value_col,
        color_continuous_scale=colorscale,
        mapbox_style="carto-positron",
        zoom=zoom,
        center=center or {"lat": -2.5, "lon": 118},
        opacity=0.7,
        labels={value_col: 'Konsumsi (GWh)'},
        hover_name=province_col,
        hover_data={
            value_col: ':,.2f',
        },
        height=height
    )
    
    # Update layout
    fig.update_layout(
        title=get_title_format(title, subtitle),
        margin=MARGINS['tight'],
        coloraxis_colorbar=dict(
            title="GWh",
            thickness=20,
            len=0.7
        ) if show_colorbar else None
    )
    
    return fig


def create_choropleth_map_plotly_geo(
    gdf: gpd.GeoDataFrame,
    value_col: str,
    province_col: str = 'Propinsi',
    title: str = '',
    subtitle: str = None,
    colorscale: list = None,
    height: int = 800,
    show_colorbar: bool = True
) -> go.Figure:
    """
    Create choropleth map menggunakan Plotly Graph Objects (alternative method)
    
    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame dengan geometri dan data
    value_col : str
        Column untuk color intensity
    province_col : str
        Column nama provinsi
    title : str
        Map title
    subtitle : str, optional
        Subtitle
    colorscale : list, optional
        Custom colorscale
    height : int
        Figure height
    show_colorbar : bool
        Show colorbar
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    # Use custom colorscale or default
    if colorscale is None:
        colorscale = [[0, '#ffffcc'], [0.5, '#feb24c'], [1, '#e31a1c']]
    
    # Prepare data
    gdf_plot = gdf.copy()
    gdf_plot[value_col] = gdf_plot[value_col].fillna(0)
    
    # Create choropleth trace
    fig = go.Figure(go.Choroplethmapbox(
        geojson=json.loads(gdf_plot.to_json()),
        locations=gdf_plot.index,
        z=gdf_plot[value_col],
        colorscale=colorscale,
        marker=dict(
            line=dict(width=0.5, color='white')
        ),
        colorbar=dict(
            title="GWh",
            thickness=20,
            len=0.7
        ) if show_colorbar else None,
        hovertemplate='<b>%{text}</b><br>Konsumsi: %{z:,.2f} GWh<extra></extra>',
        text=gdf_plot[province_col]
    ))
    
    # Update layout
    fig.update_layout(
        title=get_title_format(title, subtitle),
        mapbox=dict(
            style="carto-positron",
            zoom=3.5,
            center={"lat": -2.5, "lon": 118}
        ),
        height=height,
        margin=MARGINS['tight']
    )
    
    return fig


# ============================================
# BUBBLE MAP
# ============================================

def create_bubble_map(
    df: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    size_col: str,
    province_col: str,
    title: str = '',
    subtitle: str = None,
    height: int = 800,
    size_max: int = 50
) -> go.Figure:
    """
    Create bubble map (circles sized by value)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Data with lat/lon coordinates
    lat_col : str
        Latitude column
    lon_col : str
        Longitude column
    size_col : str
        Column untuk bubble size
    province_col : str
        Province name column
    title : str
        Map title
    subtitle : str, optional
        Subtitle
    height : int
        Figure height
    size_max : int
        Maximum bubble size
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    fig = px.scatter_mapbox(
        df,
        lat=lat_col,
        lon=lon_col,
        size=size_col,
        hover_name=province_col,
        hover_data={
            size_col: ':,.2f',
            lat_col: False,
            lon_col: False
        },
        color=size_col,
        color_continuous_scale='Reds',
        size_max=size_max,
        zoom=3.5,
        center={"lat": -2.5, "lon": 118},
        mapbox_style="carto-positron",
        height=height
    )
    
    fig.update_layout(
        title=get_title_format(title, subtitle),
        margin=MARGINS['tight']
    )
    
    return fig


# ============================================
# INTERACTIVE COMPARISON MAP
# ============================================

def create_comparison_map(
    gdf1: gpd.GeoDataFrame,
    gdf2: gpd.GeoDataFrame,
    value_col: str,
    province_col: str,
    year1: int,
    year2: int,
    title: str = '',
    height: int = 600
) -> go.Figure:
    """
    Create side-by-side comparison map untuk 2 tahun
    
    Parameters:
    -----------
    gdf1 : gpd.GeoDataFrame
        Data tahun pertama
    gdf2 : gpd.GeoDataFrame
        Data tahun kedua
    value_col : str
        Column untuk visualization
    province_col : str
        Province column name
    year1 : int
        First year
    year2 : int
        Second year
    title : str
        Map title
    height : int
        Figure height
    
    Returns:
    --------
    go.Figure : Plotly figure dengan 2 subplots
    """
    from plotly.subplots import make_subplots
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[f'Tahun {year1}', f'Tahun {year2}'],
        specs=[[{"type": "mapbox"}, {"type": "mapbox"}]],
        horizontal_spacing=0.01
    )
    
    # Determine color range untuk konsistensi
    vmin = min(gdf1[value_col].min(), gdf2[value_col].min())
    vmax = max(gdf1[value_col].max(), gdf2[value_col].max())
    
    # Add first map
    fig.add_trace(
        go.Choroplethmapbox(
            geojson=json.loads(gdf1.to_json()),
            locations=gdf1.index,
            z=gdf1[value_col],
            colorscale=CHOROPLETH_COLORSCALE,
            zmin=vmin,
            zmax=vmax,
            marker=dict(line=dict(width=0.5, color='white')),
            colorbar=dict(x=0.45, thickness=15, len=0.7, title='GWh'),
            hovertemplate='<b>%{text}</b><br>%{z:,.2f} GWh<extra></extra>',
            text=gdf1[province_col],
            showscale=True
        ),
        row=1, col=1
    )
    
    # Add second map
    fig.add_trace(
        go.Choroplethmapbox(
            geojson=json.loads(gdf2.to_json()),
            locations=gdf2.index,
            z=gdf2[value_col],
            colorscale=CHOROPLETH_COLORSCALE,
            zmin=vmin,
            zmax=vmax,
            marker=dict(line=dict(width=0.5, color='white')),
            colorbar=dict(x=1.02, thickness=15, len=0.7, title='GWh'),
            hovertemplate='<b>%{text}</b><br>%{z:,.2f} GWh<extra></extra>',
            text=gdf2[province_col],
            showscale=True
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        title=get_title_format(title),
        height=height,
        mapbox=dict(
            style="carto-positron",
            zoom=3.2,
            center={"lat": -2.5, "lon": 118}
        ),
        mapbox2=dict(
            style="carto-positron",
            zoom=3.2,
            center={"lat": -2.5, "lon": 118}
        ),
        margin=MARGINS['tight']
    )
    
    return fig


# ============================================
# GROWTH RATE MAP
# ============================================

def create_growth_rate_map(
    gdf: gpd.GeoDataFrame,
    value_col: str,
    province_col: str,
    title: str = '',
    subtitle: str = None,
    height: int = 800
) -> go.Figure:
    """
    Create map dengan diverging colorscale untuk growth rate
    (negative = merah, positive = hijau)
    
    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame dengan growth rate data
    value_col : str
        Column berisi growth rate (%)
    province_col : str
        Province column
    title : str
        Map title
    subtitle : str, optional
        Subtitle
    height : int
        Figure height
    
    Returns:
    --------
    go.Figure : Plotly figure
    """
    # Diverging colorscale (red-white-green)
    diverging_scale = [
        [0.0, '#d73027'],    # Red (negative)
        [0.5, '#ffffbf'],    # Yellow (neutral)
        [1.0, '#1a9850']     # Green (positive)
    ]
    
    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry.__geo_interface__,
        locations=gdf.index,
        color=value_col,
        color_continuous_scale=diverging_scale,
        color_continuous_midpoint=0,
        mapbox_style="carto-positron",
        zoom=3.5,
        center={"lat": -2.5, "lon": 118},
        opacity=0.7,
        labels={value_col: 'Growth (%)'},
        hover_name=province_col,
        hover_data={
            value_col: ':.2f%',
        },
        height=height
    )
    
    fig.update_layout(
        title=get_title_format(title, subtitle),
        margin=MARGINS['tight'],
        coloraxis_colorbar=dict(
            title="Growth %",
            thickness=20,
            len=0.7,
            ticksuffix='%'
        )
    )
    
    return fig


# ============================================
# UTILITY FUNCTIONS
# ============================================

def add_province_centroids(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Add centroid lat/lon columns to GeoDataFrame
    
    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        Input GeoDataFrame
    
    Returns:
    --------
    gpd.GeoDataFrame : GeoDataFrame dengan kolom lat/lon
    """
    gdf = gdf.copy()
    gdf['centroid'] = gdf.geometry.centroid
    gdf['lon'] = gdf.centroid.x
    gdf['lat'] = gdf.centroid.y
    return gdf


def calculate_bounds(gdf: gpd.GeoDataFrame) -> Dict:
    """
    Calculate geographic bounds dari GeoDataFrame
    
    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        Input GeoDataFrame
    
    Returns:
    --------
    dict : Bounds dictionary
    """
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    
    return {
        'minlon': bounds[0],
        'minlat': bounds[1],
        'maxlon': bounds[2],
        'maxlat': bounds[3],
        'center_lon': (bounds[0] + bounds[2]) / 2,
        'center_lat': (bounds[1] + bounds[3]) / 2
    }


def categorize_consumption(value: float, thresholds: list = None) -> str:
    """
    Categorize consumption value ke kategori
    
    Parameters:
    -----------
    value : float
        Consumption value
    thresholds : list, optional
        Custom thresholds [low, medium, high]
    
    Returns:
    --------
    str : Category label
    """
    if thresholds is None:
        thresholds = [5000, 15000, 30000]  # Default for Indonesia
    
    if value < thresholds[0]:
        return 'Sangat Rendah'
    elif value < thresholds[1]:
        return 'Rendah'
    elif value < thresholds[2]:
        return 'Sedang'
    else:
        return 'Tinggi'


# Testing
if __name__ == "__main__":
    print("=== Maps Module Test ===\n")
    
    print("📍 Available map functions:")
    print("  • create_choropleth_map() - Main choropleth")
    print("  • create_choropleth_map_plotly_geo() - Alternative method")
    print("  • create_bubble_map() - Bubble/circle map")
    print("  • create_comparison_map() - Side-by-side comparison")
    print("  • create_growth_rate_map() - Diverging colorscale")
    
    print("\n🛠️  Utility functions:")
    print("  • add_province_centroids() - Add lat/lon centroids")
    print("  • calculate_bounds() - Get geographic bounds")
    print("  • categorize_consumption() - Categorize values")
    
    print("\n✅ Maps module ready!")