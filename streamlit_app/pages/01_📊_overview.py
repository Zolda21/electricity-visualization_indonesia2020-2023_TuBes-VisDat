"""
Page 1: Overview Dashboard
KPI Panel, National Summary, Top Rankings
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.viz.charts import (
    create_horizontal_bar_chart,
    create_line_chart,
    create_boxplot
)

# Page config
st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

# Load global CSS
def load_css():
    """Load custom CSS from assets folder"""
    css_file = Path(__file__).parent.parent / "assets" / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/electricity_clean.csv')
    return df

# Main page
def main():
    st.title("📊 Overview Dashboard")
    st.markdown("Ringkasan Konsumsi Listrik Nasional Indonesia")
    st.markdown("---")
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("⚙️ Filter Options")
    
    # Year filter
    available_years = sorted(df['Year'].unique())
    selected_year = st.sidebar.selectbox(
        "Pilih Tahun",
        options=available_years,
        index=len(available_years)-1  # Default to latest year
    )
    
    # Top N filter
    top_n = st.sidebar.slider(
        "Top N Provinsi",
        min_value=5,
        max_value=20,
        value=10,
        step=1
    )
    
    # Filter data
    df_year = df[df['Year'] == selected_year].copy()
    
    # ============================================
    # KPI PANEL
    # ============================================
    st.markdown(f"### 📈 Key Performance Indicators - {selected_year}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total consumption
    total_consumption = df_year['Electricity_GWh'].sum()
    
    # Previous year comparison
    if selected_year > df['Year'].min():
        prev_year = selected_year - 1
        df_prev = df[df['Year'] == prev_year]
        prev_total = df_prev['Electricity_GWh'].sum()
        yoy_growth = ((total_consumption - prev_total) / prev_total) * 100
    else:
        yoy_growth = 0
    
    with col1:
        st.metric(
            label="🔌 Total Konsumsi Nasional",
            value=f"{total_consumption:,.0f} GWh",
            delta=f"{yoy_growth:+.2f}% YoY" if yoy_growth != 0 else None
        )
    
    with col2:
        top_province = df_year.nlargest(1, 'Electricity_GWh').iloc[0]
        st.metric(
            label="🏆 Provinsi Tertinggi",
            value=top_province['Province'],
            delta=f"{top_province['Electricity_GWh']:,.0f} GWh"
        )
    
    with col3:
        mean_consumption = df_year['Electricity_GWh'].mean()
        st.metric(
            label="📊 Rata-rata per Provinsi",
            value=f"{mean_consumption:,.0f} GWh",
            delta=None
        )
    
    with col4:
        num_provinces = df_year['Province'].nunique()
        st.metric(
            label="🗺️ Jumlah Provinsi",
            value=f"{num_provinces}",
            delta=None
        )
    
    st.markdown("---")
    
    # ============================================
    # TOP PROVINCES RANKING
    # ============================================
    st.markdown(f"### 🏆 Top {top_n} Provinsi Konsumsi Tertinggi - {selected_year}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bar chart
        fig = create_horizontal_bar_chart(
            df=df_year,
            x_col='Electricity_GWh',
            y_col='Province',
            title=f'Top {top_n} Provinsi - {selected_year}',
            top_n=top_n,
            color_by_rank=True,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Table
        st.markdown("#### 📋 Detail Ranking")
        top_data = df_year.nlargest(top_n, 'Electricity_GWh')[['Province', 'Electricity_GWh']].copy()
        top_data.reset_index(drop=True, inplace=True)
        top_data.index += 1  # Start from 1
        top_data['Electricity_GWh'] = top_data['Electricity_GWh'].apply(lambda x: f"{x:,.2f}")
        top_data.columns = ['Provinsi', 'Konsumsi (GWh)']
        
        st.dataframe(
            top_data,
            height=550,
            use_container_width=True
        )
    
    st.markdown("---")
    
    # ============================================
    # NATIONAL TREND
    # ============================================
    st.markdown("### 📈 Tren Konsumsi Nasional (2020-2023)")
    
    # Calculate yearly totals
    yearly_total = df.groupby('Year')['Electricity_GWh'].sum().reset_index()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = create_line_chart(
            df=yearly_total,
            x_col='Year',
            y_col='Electricity_GWh',
            title='Total Konsumsi Listrik Nasional',
            subtitle='Gabungan 34 Provinsi',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Statistik Pertumbuhan")
        
        # Calculate growth rates
        for i in range(len(yearly_total)):
            year = yearly_total.iloc[i]['Year']
            consumption = yearly_total.iloc[i]['Electricity_GWh']
            
            if i > 0:
                prev_consumption = yearly_total.iloc[i-1]['Electricity_GWh']
                growth = ((consumption - prev_consumption) / prev_consumption) * 100
                st.metric(
                    label=f"{int(year)}",
                    value=f"{consumption:,.0f} GWh",
                    delta=f"{growth:+.2f}%"
                )
            else:
                st.metric(
                    label=f"{int(year)}",
                    value=f"{consumption:,.0f} GWh"
                )
    
    st.markdown("---")
    
    # ============================================
    # DISTRIBUTION ANALYSIS
    # ============================================
    st.markdown("### 📊 Distribusi Konsumsi Listrik")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Boxplot all years
        fig = create_boxplot(
            df=df,
            y_col='Electricity_GWh',
            x_col='Year',
            title='Distribusi Konsumsi per Tahun',
            subtitle='Boxplot showing median and outliers',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Statistics table
        st.markdown("#### 📈 Statistik Deskriptif")
        
        stats = df_year['Electricity_GWh'].describe()
        
        stats_df = pd.DataFrame({
            'Metrik': ['Count', 'Mean', 'Std', 'Min', '25%', '50% (Median)', '75%', 'Max'],
            'Nilai': [
                f"{stats['count']:.0f}",
                f"{stats['mean']:,.2f} GWh",
                f"{stats['std']:,.2f} GWh",
                f"{stats['min']:,.2f} GWh",
                f"{stats['25%']:,.2f} GWh",
                f"{stats['50%']:,.2f} GWh",
                f"{stats['75%']:,.2f} GWh",
                f"{stats['max']:,.2f} GWh"
            ]
        })
        
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        # Additional insights
        Q1 = stats['25%']
        Q3 = stats['75%']
        IQR = Q3 - Q1
        
        st.info(f"""
        **📊 Insight Distribusi:**
        - **IQR**: {IQR:,.2f} GWh
        - **Range**: {stats['max'] - stats['min']:,.2f} GWh
        - **Coefficient of Variation**: {(stats['std']/stats['mean'])*100:.1f}%
        """)
    
    st.markdown("---")
    
    # ============================================
    # KEY INSIGHTS
    # ============================================
    st.markdown("### 💡 Key Insights")
    
    # Calculate some insights
    top_3 = df_year.nlargest(3, 'Electricity_GWh')['Province'].tolist()
    bottom_3 = df_year.nsmallest(3, 'Electricity_GWh')['Province'].tolist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"""
        **🏆 Provinsi dengan Konsumsi Tertinggi ({selected_year}):**
        
        1. {top_3[0]}
        2. {top_3[1]}
        3. {top_3[2]}
        
        Ketiga provinsi ini menyumbang lebih dari 50% total konsumsi nasional.
        """)
    
    with col2:
        st.warning(f"""
        **📉 Provinsi dengan Konsumsi Terendah ({selected_year}):**
        
        1. {bottom_3[0]}
        2. {bottom_3[1]}
        3. {bottom_3[2]}
        
        Provinsi-provinsi ini memiliki konsumsi di bawah 1,000 GWh.
        """)

if __name__ == "__main__":
    main()