"""
Page 3: Yearly Trends (Interactive)
Time series analysis dengan animated charts dan growth insights
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.express as px

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.viz.charts import (
    create_line_chart,
    create_heatmap,
    create_grouped_bar_chart,
    create_area_chart
)
from src.data.transform import (
    add_region_column,
    calculate_cagr,
    add_growth_features
)
from src.eda.explorations import (
    get_fastest_growing_provinces,
    analyze_national_trend
)

# Page config
st.set_page_config(page_title="Yearly Trends", page_icon="📈", layout="wide")

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
    st.title("📈 Yearly Trends Dashboard")
    st.markdown("Interactive time series analysis dan growth insights (2020-2023)")
    st.markdown("---")
    
    # Load data
    df = load_data()
    
    # ============================================
    # SIDEBAR CONTROLS
    # ============================================
    st.sidebar.header("⚙️ Trend Analysis Settings")
    
    # Analysis type
    analysis_type = st.sidebar.radio(
        "📊 Analysis Type",
        ["National Trend", "Provincial Trends", "Regional Trends", "Growth Analysis"]
    )
    
    # Year range selector
    st.sidebar.markdown("### 📅 Year Range")
    years = sorted(df['Year'].unique())
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_year = st.selectbox("From", years, index=0)
    with col2:
        end_year = st.selectbox("To", years, index=len(years)-1)
    
    # Province selection for comparison
    if analysis_type == "Provincial Trends":
        st.sidebar.markdown("### 🗺️ Select Provinces")
        
        selection_mode = st.sidebar.radio(
            "Selection Mode",
            ["Top N", "Custom", "Compare Specific"]
        )
        
        if selection_mode == "Top N":
            top_n = st.sidebar.slider("Number of Provinces", 3, 15, 5)
            df_latest = df[df['Year'] == end_year]
            selected_provinces = df_latest.nlargest(top_n, 'Electricity_GWh')['Province'].tolist()
        
        elif selection_mode == "Custom":
            all_provinces = sorted(df['Province'].unique())
            selected_provinces = st.sidebar.multiselect(
                "Choose Provinces",
                options=all_provinces,
                default=all_provinces[:5]
            )
        
        else:  # Compare Specific
            all_provinces = sorted(df['Province'].unique())
            col1, col2 = st.sidebar.columns(2)
            with col1:
                prov1 = st.selectbox("Province 1", all_provinces, index=0)
            with col2:
                prov2 = st.selectbox("Province 2", all_provinces, index=1)
            selected_provinces = [prov1, prov2]
    
    # Visualization options
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎨 Visualization Options")
    
    show_markers = st.sidebar.checkbox("Show Data Points", value=True)
    show_trend_line = st.sidebar.checkbox("Show Trend Line", value=False)
    animate_charts = st.sidebar.checkbox("Animate Transitions", value=True)
    
    # ============================================
    # MAIN CONTENT - TABS
    # ============================================
    
    # Filter data by year range
    df_filtered = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)].copy()

    # Pre-calculate untuk insights
    fastest = get_fastest_growing_provinces(df, start_year, end_year, n=10)
    national_trend = analyze_national_trend(df_filtered)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "📈 Detailed Analysis", 
        "🔥 Heatmap", 
        "💡 Insights"
    ])
    
    # ============================================
    # TAB 1: OVERVIEW
    # ============================================
    with tab1:
        st.markdown("### 📊 National Overview")
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_start = national_trend.iloc[0]['Total_GWh']
            total_end = national_trend.iloc[-1]['Total_GWh']
            st.metric(
                f"Total ({start_year})",
                f"{total_start:,.0f} GWh"
            )
        
        with col2:
            st.metric(
                f"Total ({end_year})",
                f"{total_end:,.0f} GWh",
                delta=f"{((total_end/total_start - 1) * 100):+.1f}%"
            )
        
        with col3:
            avg_growth = national_trend['YoY_Growth_%'].mean()
            st.metric(
                "Avg. YoY Growth",
                f"{avg_growth:+.2f}%"
            )
        
        with col4:
            total_change = total_end - total_start
            st.metric(
                "Total Change",
                f"{total_change:+,.0f} GWh"
            )
        
        st.markdown("---")
        
        # National trend chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_national = create_line_chart(
                df=national_trend,
                x_col='Year',
                y_col='Total_GWh',
                title='National Consumption Trend',
                subtitle=f'{start_year}-{end_year}',
                height=500,
                show_markers=show_markers
            )
            st.plotly_chart(fig_national, use_container_width=True)
        
        with col2:
            st.markdown("#### 📈 Growth Breakdown")
            
            for _, row in national_trend.iterrows():
                year = int(row['Year'])
                total = row['Total_GWh']
                growth = row['YoY_Growth_%']
                
                if pd.notna(growth):
                    trend_class = "trend-up" if growth > 0 else "trend-down"
                    st.markdown(f"""
                    **{year}**  
                    {total:,.0f} GWh  
                    <span class="{trend_class}">{growth:+.2f}%</span>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    **{year}**  
                    {total:,.0f} GWh
                    """)
                st.markdown("---")
    
    # ============================================
    # TAB 2: DETAILED ANALYSIS
    # ============================================
    with tab2:
        if analysis_type == "National Trend":
            st.markdown("### 📊 National Detailed Analysis")
            
            # Multiple metrics
            col1, col2 = st.columns(2)
            
            with col1:
                # Total consumption by year
                yearly_data = df_filtered.groupby('Year').agg({
                    'Electricity_GWh': ['sum', 'mean', 'std']
                }).reset_index()
                yearly_data.columns = ['Year', 'Total', 'Mean', 'Std']
                
                st.markdown("#### 📊 Yearly Statistics")
                st.dataframe(
                    yearly_data.style.format({
                        'Total': '{:,.0f}',
                        'Mean': '{:,.2f}',
                        'Std': '{:,.2f}'
                    }),
                    use_container_width=True
                )
            
            with col2:
                # Growth rate analysis
                yearly_data['Growth_%'] = yearly_data['Total'].pct_change() * 100
                
                fig_growth = px.bar(
                    yearly_data,
                    x='Year',
                    y='Growth_%',
                    title='Year-over-Year Growth Rate',
                    text='Growth_%',
                    color='Growth_%',
                    color_continuous_scale=['red', 'yellow', 'green']
                )
                fig_growth.update_traces(texttemplate='%{text:.2f}%')
                st.plotly_chart(fig_growth, use_container_width=True)
        
        elif analysis_type == "Provincial Trends":
            st.markdown(f"### 📈 Provincial Trends Comparison")
            st.markdown(f"*Showing {len(selected_provinces)} provinces*")
            
            if len(selected_provinces) > 0:
                # Filter data
                df_provinces = df_filtered[df_filtered['Province'].isin(selected_provinces)]
                
                # Multi-line chart
                fig_multi = create_line_chart(
                    df=df_provinces,
                    x_col='Year',
                    y_col='Electricity_GWh',
                    group_col='Province',
                    title='Provincial Consumption Trends',
                    subtitle=f'{start_year}-{end_year}',
                    height=600,
                    show_markers=show_markers
                )
                st.plotly_chart(fig_multi, use_container_width=True)
                
                # Growth comparison
                st.markdown("#### 📊 Growth Comparison")
                
                growth_data = []
                for prov in selected_provinces:
                    df_prov = df_provinces[df_provinces['Province'] == prov]
                    if len(df_prov) >= 2:
                        first = df_prov.iloc[0]['Electricity_GWh']
                        last = df_prov.iloc[-1]['Electricity_GWh']
                        growth = ((last - first) / first) * 100
                        
                        growth_data.append({
                            'Province': prov,
                            f'{start_year}': first,
                            f'{end_year}': last,
                            'Growth_%': growth
                        })
                
                df_growth = pd.DataFrame(growth_data)
                df_growth = df_growth.sort_values('Growth_%', ascending=False)
                
                st.dataframe(
                    df_growth.style.format({
                        f'{start_year}': '{:,.2f}',
                        f'{end_year}': '{:,.2f}',
                        'Growth_%': '{:+.2f}%'
                    }).background_gradient(subset=['Growth_%'], cmap='RdYlGn'),
                    use_container_width=True
                )
        
        elif analysis_type == "Regional Trends":
            st.markdown("### 🌏 Regional Trends Analysis")
            
            # Add region column
            df_regional = add_region_column(df_filtered)
            
            # Aggregate by region and year
            regional_data = df_regional.groupby(['Region', 'Year'])['Electricity_GWh'].sum().reset_index()
            
            # Area chart (stacked)
            fig_area = create_area_chart(
                df=regional_data,
                x_col='Year',
                y_col='Electricity_GWh',
                group_col='Region',
                title='Regional Consumption Trends (Stacked)',
                subtitle=f'{start_year}-{end_year}',
                height=600
            )
            st.plotly_chart(fig_area, use_container_width=True)
            
            # Regional comparison table
            st.markdown("#### 📊 Regional Growth Rates")
            
            pivot = regional_data.pivot(index='Region', columns='Year', values='Electricity_GWh')
            pivot['Growth_%'] = ((pivot[end_year] - pivot[start_year]) / pivot[start_year]) * 100
            pivot = pivot.sort_values('Growth_%', ascending=False)
            
            st.dataframe(
                pivot.style.format('{:,.0f}').format({'Growth_%': '{:+.2f}%'}).background_gradient(
                    subset=['Growth_%'], cmap='RdYlGn'
                ),
                use_container_width=True
            )
        
        else:  # Growth Analysis
            st.markdown("### 🚀 Growth Analysis")
            
            # Fastest growing
            fastest = get_fastest_growing_provinces(df, start_year, end_year, n=10)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔥 Top 10 Fastest Growing")
                
                fig_fastest = px.bar(
                    fastest,
                    x='CAGR_%',
                    y='Province',
                    orientation='h',
                    title='Fastest Growing Provinces',
                    text='CAGR_%',
                    color='CAGR_%',
                    color_continuous_scale='Greens'
                )
                fig_fastest.update_traces(texttemplate='%{text:.2f}%')
                fig_fastest.update_layout(height=500)
                st.plotly_chart(fig_fastest, use_container_width=True)
            
            with col2:
                st.markdown("#### 📉 Bottom 10 Slowest Growing")
                
                slowest = df.copy()
                # Calculate CAGR for all
                df_start = slowest[slowest['Year'] == start_year][['Province', 'Electricity_GWh']]
                df_end = slowest[slowest['Year'] == end_year][['Province', 'Electricity_GWh']]
                
                merged = df_start.merge(df_end, on='Province', suffixes=('_start', '_end'))
                n_years = end_year - start_year
                merged['CAGR_%'] = ((merged['Electricity_GWh_end'] / merged['Electricity_GWh_start']) ** (1/n_years) - 1) * 100
                
                slowest_data = merged.nsmallest(10, 'CAGR_%')[['Province', 'CAGR_%']]
                
                fig_slowest = px.bar(
                    slowest_data,
                    x='CAGR_%',
                    y='Province',
                    orientation='h',
                    title='Slowest Growing Provinces',
                    text='CAGR_%',
                    color='CAGR_%',
                    color_continuous_scale='Reds_r'
                )
                fig_slowest.update_traces(texttemplate='%{text:.2f}%')
                fig_slowest.update_layout(height=500)
                st.plotly_chart(fig_slowest, use_container_width=True)
    
    # ============================================
    # TAB 3: HEATMAP
    # ============================================
    with tab3:
        st.markdown("### 🔥 Consumption Heatmap")
        st.markdown("*All provinces across all years*")
        
        # Heatmap options
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            show_values_heatmap = st.checkbox("Show Values", value=False)
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Alphabetical", f"Total ({end_year})", "Average"]
            )
        
        # Prepare data for heatmap
        df_heatmap = df_filtered.copy()
        
        if sort_by == f"Total ({end_year})":
            order = df_heatmap[df_heatmap['Year'] == end_year].sort_values(
                'Electricity_GWh', ascending=False
            )['Province'].tolist()
            df_heatmap['Province'] = pd.Categorical(df_heatmap['Province'], categories=order, ordered=True)
            df_heatmap = df_heatmap.sort_values('Province')
        elif sort_by == "Average":
            avg_order = df_heatmap.groupby('Province')['Electricity_GWh'].mean().sort_values(ascending=False).index
            df_heatmap['Province'] = pd.Categorical(df_heatmap['Province'], categories=avg_order, ordered=True)
            df_heatmap = df_heatmap.sort_values('Province')
        
        # Create heatmap
        fig_heatmap = create_heatmap(
            df=df_heatmap,
            x_col='Year',
            y_col='Province',
            value_col='Electricity_GWh',
            title='Electricity Consumption Heatmap',
            subtitle=f'All Provinces ({start_year}-{end_year})',
            height=1200,
            show_values=show_values_heatmap
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # ============================================
    # TAB 4: INSIGHTS
    # ============================================
    with tab4:
        st.markdown("### 💡 Key Insights & Findings")
        
        # Calculate insights
        total_start = df[df['Year'] == start_year]['Electricity_GWh'].sum()
        total_end = df[df['Year'] == end_year]['Electricity_GWh'].sum()
        overall_growth = ((total_end - total_start) / total_start) * 100
        
        # Top growers
        fastest_3 = get_fastest_growing_provinces(df, start_year, end_year, n=3)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"""
            ### 📊 National Trends
            
            **Period:** {start_year}-{end_year}
            
            **Key Findings:**
            - Total growth: **{overall_growth:+.2f}%**
            - Start total: **{total_start:,.0f} GWh**
            - End total: **{total_end:,.0f} GWh**
            - Absolute change: **{total_end - total_start:+,.0f} GWh**
            
            **Trend:** {'📈 Increasing' if overall_growth > 0 else '📉 Decreasing'}
            """)
        
        with col2:
            st.info(f"""
            ### 🚀 Top Performers
            
            **Fastest Growing Provinces:**
            
            1. **{fastest_3.iloc[0]['Province']}**  
               CAGR: {fastest_3.iloc[0]['CAGR_%']:.2f}%
            
            2. **{fastest_3.iloc[1]['Province']}**  
               CAGR: {fastest_3.iloc[1]['CAGR_%']:.2f}%
            
            3. **{fastest_3.iloc[2]['Province']}**  
               CAGR: {fastest_3.iloc[2]['CAGR_%']:.2f}%
            """)
        
        st.markdown("---")
        
        # Additional insights
        st.markdown("### 🎯 Actionable Insights")
        
        insights = f"""
        1. **Growth Momentum**: National electricity consumption grew by **{overall_growth:.1f}%** from {start_year} to {end_year}
        
        2. **Regional Leaders**: {fastest_3.iloc[0]['Province']} leads with **{fastest_3.iloc[0]['CAGR_%']:.2f}%** CAGR
        
        3. **Investment Opportunities**: Focus on provinces with high growth rates for infrastructure expansion
        
        4. **Demand Forecasting**: Current trend suggests continued growth in major urban centers
        
        5. **Policy Implications**: Regional disparities indicate need for targeted energy policies
        """
        
        st.markdown(insights)
        
        # Download insights
        st.markdown("---")
        st.markdown("### 💾 Export Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export growth data
            csv_growth = fastest.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Growth Analysis",
                data=csv_growth,
                file_name=f"growth_analysis_{start_year}_{end_year}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Export national trend
            csv_national = national_trend.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download National Trend",
                data=csv_national,
                file_name=f"national_trend_{start_year}_{end_year}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()