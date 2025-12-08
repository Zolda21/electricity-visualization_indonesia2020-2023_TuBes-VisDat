"""
Page 2: Province Analytics (Interactive)
🗺️ Geospatial analysis with interactive maps and filters
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.viz.charts import create_line_chart, create_horizontal_bar_chart
from src.viz.maps import create_choropleth_map, create_growth_rate_map
from src.data.geo_processing import add_geojson_names, merge_with_geojson
from src.data.transform import add_region_column
from src.utils.config import GEOJSON_PATH, REGION_MAPPING, REGIONS

# Page config
st.set_page_config(page_title="Province Analytics", page_icon="🗺️", layout="wide")

# Custom CSS for interactivity
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #1f77b4;
        color: white;
    }
    .stButton>button:hover {
        background-color: #0d5a8f;
        color: white;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/electricity_clean.csv')
    return df

# 🗺️ GEOJSON: Load GeoJSON
@st.cache_data
def load_geojson():
    return gpd.read_file(GEOJSON_PATH)

# Main page
def main():
    st.title("🗺️ Province Analytics Dashboard")
    st.markdown("Interactive geospatial analysis dengan maps dan detailed insights")
    st.markdown("---")
    
    # Load data
    df = load_data()
    gdf_base = load_geojson()
    
    # ============================================
    # SIDEBAR FILTERS (SUPER INTERACTIVE)
    # ============================================
    st.sidebar.header("🎛️ Interactive Filters")
    
    # Year selection with slider
    years = sorted(df['Year'].unique())
    selected_year = st.sidebar.select_slider(
        "📅 Select Year",
        options=years,
        value=years[-1]
    )
    
    # Region filter (multi-select)
    st.sidebar.markdown("### 🌏 Filter by Region")
    all_regions = st.sidebar.checkbox("All Regions", value=True)
    
    if all_regions:
        selected_regions = REGIONS
    else:
        selected_regions = st.sidebar.multiselect(
            "Choose Region(s)",
            options=REGIONS,
            default=REGIONS[:2]
        )
    
    # Province filter (multi-select with search)
    st.sidebar.markdown("### 🗺️ Filter by Province")
    
    # Get provinces based on region filter
    df_with_region = add_region_column(df)
    available_provinces = df_with_region[
        df_with_region['Region'].isin(selected_regions)
    ]['Province'].unique()
    
    province_filter_type = st.sidebar.radio(
        "Province Selection",
        ["All Provinces", "Top N", "Custom Selection"]
    )
    
    if province_filter_type == "Top N":
        top_n = st.sidebar.slider("Number of Top Provinces", 5, 20, 10)
        df_filtered = df[df['Year'] == selected_year].nlargest(top_n, 'Electricity_GWh')
        selected_provinces = df_filtered['Province'].tolist()
    elif province_filter_type == "Custom Selection":
        selected_provinces = st.sidebar.multiselect(
            "Choose Province(s)",
            options=sorted(available_provinces),
            default=list(sorted(available_provinces)[:5])
        )
    else:
        selected_provinces = list(available_provinces)
    
    # Comparison mode
    st.sidebar.markdown("---")
    comparison_mode = st.sidebar.checkbox("🔄 Enable Comparison Mode")
    
    if comparison_mode:
        compare_year = st.sidebar.selectbox(
            "Compare with Year",
            options=[y for y in years if y != selected_year],
            index=0
        )
    
    # Apply filters button
    if st.sidebar.button("🔍 Apply Filters", type="primary"):
        st.rerun()
    
    # Reset filters
    if st.sidebar.button("🔄 Reset All Filters"):
        st.rerun()
    
    # ============================================
    # MAIN CONTENT - INTERACTIVE
    # ============================================
    
    # Filter data based on selections
    df_filtered = df[
        (df['Year'] == selected_year) &
        (df['Province'].isin(selected_provinces))
    ].copy()
    
    df_filtered = add_region_column(df_filtered)
    df_filtered = df_filtered[df_filtered['Region'].isin(selected_regions)]
    
    # KPI Cards
    st.markdown(f"### 📊 Overview - {selected_year}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = df_filtered['Electricity_GWh'].sum()
        st.metric(
            "🔌 Total Consumption",
            f"{total:,.0f} GWh",
            delta=f"{len(df_filtered)} provinces"
        )
    
    with col2:
        avg = df_filtered['Electricity_GWh'].mean()
        st.metric(
            "📊 Average",
            f"{avg:,.0f} GWh"
        )
    
    with col3:
        top_prov = df_filtered.nlargest(1, 'Electricity_GWh').iloc[0]
        st.metric(
            "🏆 Highest",
            top_prov['Province'][:15],
            f"{top_prov['Electricity_GWh']:,.0f} GWh"
        )
    
    with col4:
        regions_count = df_filtered['Region'].nunique() if 'Region' in df_filtered.columns else 0
        st.metric(
            "🌏 Regions",
            regions_count
        )
    
    st.markdown("---")
    
    # ============================================
    # 🗺️ INTERACTIVE CHOROPLETH MAP
    # ============================================
    st.markdown(f"### 🗺️ Interactive Map - {selected_year}")
    
    col_map, col_info = st.columns([3, 1])
    
    with col_map:
        # Prepare data for map
        df_map = df[df['Year'] == selected_year].copy()
        df_map_geo = add_geojson_names(df_map)
        
        # 🗺️ GEOJSON: Merge with GeoJSON
        gdf_map = merge_with_geojson(
            df=df_map_geo,
            gdf=gdf_base.copy(),
            csv_province_col='Province_GeoJSON',
            geo_province_col='Propinsi',
            how='left'
        )
        
        # 🗺️ GEOJSON: Create choropleth map
        fig_map = create_choropleth_map(
            gdf=gdf_map,
            value_col='Electricity_GWh',
            province_col='Province',
            title=f'Consumption Map {selected_year}',
            height=600
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
    
    with col_info:
        st.markdown("#### 🎯 Map Info")
        st.info("""
        **How to use:**
        - 🖱️ Hover untuk detail
        - 🔍 Zoom in/out
        - 🗺️ Drag untuk pan
        - 📍 Click provinsi (soon!)
        """)
        
        # Quick stats
        st.markdown("#### 📊 Quick Stats")
        st.write(f"**Provinces shown:** {len(df_filtered)}")
        st.write(f"**Regions:** {', '.join(selected_regions[:3])}")
        if len(selected_regions) > 3:
            st.write(f"*+ {len(selected_regions) - 3} more*")
    
    st.markdown("---")
    
    # ============================================
    # COMPARISON MODE
    # ============================================
    if comparison_mode:
        st.markdown(f"### 🔄 Comparison: {selected_year} vs {compare_year}")
        
        col1, col2 = st.columns(2)
        
        # Data for comparison
        df_compare1 = df[df['Year'] == selected_year].copy()
        df_compare2 = df[df['Year'] == compare_year].copy()
        
        merged_compare = df_compare1.merge(
            df_compare2[['Province', 'Electricity_GWh']],
            on='Province',
            suffixes=(f'_{selected_year}', f'_{compare_year}')
        )
        
        merged_compare['Change_%'] = (
            (merged_compare[f'Electricity_GWh_{selected_year}'] - 
             merged_compare[f'Electricity_GWh_{compare_year}']) /
            merged_compare[f'Electricity_GWh_{compare_year}']
        ) * 100
        
        with col1:
            st.markdown(f"#### 📊 Top 10 in {selected_year}")
            top_data = merged_compare.nlargest(10, f'Electricity_GWh_{selected_year}')
            st.dataframe(
                top_data[[
                    'Province',
                    f'Electricity_GWh_{selected_year}',
                    f'Electricity_GWh_{compare_year}',
                    'Change_%'
                ]].round(2),
                height=400,
                use_container_width=True
            )
        
        with col2:
            st.markdown(f"#### 📈 Biggest Growth")
            growth_data = merged_compare.nlargest(10, 'Change_%')
            st.dataframe(
                growth_data[[
                    'Province',
                    f'Electricity_GWh_{selected_year}',
                    'Change_%'
                ]].round(2),
                height=400,
                use_container_width=True
            )
        
        st.markdown("---")
    
    # ============================================
    # PROVINCE DETAIL ANALYSIS
    # ============================================
    st.markdown("### 📍 Province Detail Analysis")
    
    # Province selector for detail
    selected_province_detail = st.selectbox(
        "🔍 Select Province for Detailed Analysis",
        options=sorted(df_filtered['Province'].unique()),
        index=0
    )
    
    if selected_province_detail:
        # Get all years data for selected province
        df_province_all = df[df['Province'] == selected_province_detail].sort_values('Year')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Trend chart
            fig_trend = create_line_chart(
                df=df_province_all,
                x_col='Year',
                y_col='Electricity_GWh',
                title=f'{selected_province_detail} - Consumption Trend',
                subtitle='2020-2023',
                height=400,
                show_markers=True
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            st.markdown(f"#### 📊 {selected_province_detail} Stats")
            
            # Calculate stats
            current_value = df_province_all[df_province_all['Year'] == selected_year]['Electricity_GWh'].values[0]
            first_year = df_province_all.iloc[0]['Year']
            first_value = df_province_all.iloc[0]['Electricity_GWh']
            
            growth = ((current_value - first_value) / first_value) * 100
            
            st.metric(
                f"Consumption ({selected_year})",
                f"{current_value:,.2f} GWh"
            )
            
            st.metric(
                "Total Growth",
                f"{growth:+.2f}%",
                delta=f"from {first_year}"
            )
            
            # Rank
            rank = (df[df['Year'] == selected_year]['Electricity_GWh'] > current_value).sum() + 1
            st.metric("National Rank", f"#{rank}")
            
            # Region
            if 'Region' in df_province_all.columns:
                region = df_province_all.iloc[0]['Region']
                st.info(f"**Region:** {region}")
    
    st.markdown("---")
    
    # ============================================
    # REGIONAL COMPARISON
    # ============================================
    st.markdown("### 🌏 Regional Comparison")
    
    if len(selected_regions) > 1:
        # Aggregate by region
        df_regional = df_with_region[
            (df_with_region['Year'] == selected_year) &
            (df_with_region['Region'].isin(selected_regions))
        ].groupby('Region')['Electricity_GWh'].sum().reset_index()
        
        df_regional = df_regional.sort_values('Electricity_GWh', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            import plotly.express as px
            fig_regional = px.bar(
                df_regional,
                x='Region',
                y='Electricity_GWh',
                title=f'Regional Comparison - {selected_year}',
                text='Electricity_GWh',
                color='Electricity_GWh',
                color_continuous_scale='Blues'
            )
            fig_regional.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig_regional, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Regional Stats")
            for _, row in df_regional.iterrows():
                pct = (row['Electricity_GWh'] / df_regional['Electricity_GWh'].sum()) * 100
                st.metric(
                    row['Region'],
                    f"{row['Electricity_GWh']:,.0f} GWh",
                    f"{pct:.1f}%"
                )
    else:
        st.info("Select multiple regions to enable regional comparison")
    
    st.markdown("---")
    
    # ============================================
    # DOWNLOAD SECTION
    # ============================================
    st.markdown("### 💾 Download Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download filtered data
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"electricity_data_{selected_year}_filtered.csv",
            mime="text/csv"
        )
    
    with col2:
        # Download comparison data
        if comparison_mode:
            csv_compare = merged_compare.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Comparison (CSV)",
                data=csv_compare,
                file_name=f"comparison_{selected_year}_vs_{compare_year}.csv",
                mime="text/csv"
            )
    
    with col3:
        # Download regional summary
        if len(selected_regions) > 1:
            csv_regional = df_regional.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Regional Data (CSV)",
                data=csv_regional,
                file_name=f"regional_summary_{selected_year}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()