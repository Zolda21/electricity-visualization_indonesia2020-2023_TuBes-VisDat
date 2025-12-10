"""
Page 4: Data Explorer (Interactive)
Advanced data exploration dengan filtering, sorting, dan search
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.express as px

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.transform import (
    add_region_column,
    add_consumption_category,
    add_growth_features,
    add_ranking_features,
    transform_complete
)
from src.utils.config import REGION_MAPPING, REGIONS
from src.eda.statistics import (
    calculate_descriptive_stats,
    calculate_percentiles,
    detect_outliers_iqr
)

# Page config
st.set_page_config(page_title="Data Explorer", page_icon="📋", layout="wide")

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
    st.title("📋 Data Explorer")
    st.markdown("Interactive data exploration dengan advanced filtering dan analysis tools")
    st.markdown("---")
    
    # Load data
    df_raw = load_data()
    
    # ============================================
    # SIDEBAR - ADVANCED FILTERS
    # ============================================
    st.sidebar.header("🔍 Advanced Filters")
    
    # Data transformation options
    st.sidebar.markdown("### 🔧 Data Enhancement")
    add_features = st.sidebar.multiselect(
        "Add Features",
        ["Region", "Category", "Growth Rate", "Rankings", "All Features"],
        default=["Region"]
    )
    
    # Apply transformations
    df = df_raw.copy()
    
    if "All Features" in add_features:
        df = transform_complete(df)
    else:
        if "Region" in add_features:
            df = add_region_column(df)
        if "Category" in add_features:
            df = add_consumption_category(df)
        if "Growth Rate" in add_features:
            df = add_growth_features(df)
        if "Rankings" in add_features:
            df = add_ranking_features(df)
    
    # Year filter
    st.sidebar.markdown("### 📅 Year Filter")
    year_filter_type = st.sidebar.radio(
        "Filter Type",
        ["All Years", "Single Year", "Year Range", "Multiple Years"]
    )
    
    years = sorted(df['Year'].unique())
    
    if year_filter_type == "Single Year":
        selected_years = [st.sidebar.selectbox("Select Year", years, index=len(years)-1)]
    elif year_filter_type == "Year Range":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_year = st.selectbox("From", years, index=0)
        with col2:
            end_year = st.selectbox("To", years, index=len(years)-1)
        selected_years = list(range(start_year, end_year + 1))
    elif year_filter_type == "Multiple Years":
        selected_years = st.sidebar.multiselect("Select Years", years, default=years)
    else:
        selected_years = years
    
    df = df[df['Year'].isin(selected_years)]
    
    # Province filter
    st.sidebar.markdown("### 🗺️ Province Filter")
    
    province_filter_type = st.sidebar.radio(
        "Filter Type",
        ["All Provinces", "By Region", "By Consumption Level", "Custom Selection", "Search"]
    )
    
    if province_filter_type == "By Region":
        selected_regions = st.sidebar.multiselect(
            "Select Regions",
            REGIONS,
            default=REGIONS
        )
        if 'Region' in df.columns:
            df = df[df['Region'].isin(selected_regions)]
    
    elif province_filter_type == "By Consumption Level":
        if 'Category' in df.columns:
            categories = df['Category'].unique()
            selected_categories = st.sidebar.multiselect(
                "Select Consumption Levels",
                categories,
                default=list(categories)
            )
            df = df[df['Category'].isin(selected_categories)]
        else:
            st.sidebar.warning("Enable 'Category' feature first")
    
    elif province_filter_type == "Custom Selection":
        available_provinces = sorted(df['Province'].unique())
        selected_provinces = st.sidebar.multiselect(
            "Select Provinces",
            available_provinces,
            default=available_provinces[:10]
        )
        df = df[df['Province'].isin(selected_provinces)]
    
    elif province_filter_type == "Search":
        search_term = st.sidebar.text_input("🔍 Search Province")
        if search_term:
            df = df[df['Province'].str.contains(search_term.upper(), case=False, na=False)]
    
    # Value range filter
    st.sidebar.markdown("### 📊 Value Range Filter")
    
    min_val = float(df['Electricity_GWh'].min())
    max_val = float(df['Electricity_GWh'].max())
    
    value_range = st.sidebar.slider(
        "Consumption Range (GWh)",
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val)
    )
    
    df = df[(df['Electricity_GWh'] >= value_range[0]) & 
            (df['Electricity_GWh'] <= value_range[1])]
    
    # Outlier filter
    st.sidebar.markdown("---")
    show_outliers_only = st.sidebar.checkbox("🔥 Show Outliers Only")
    
    if show_outliers_only and len(selected_years) == 1:
        outliers = detect_outliers_iqr(df, selected_years[0])
        if not outliers.empty:
            df = df[df['Province'].isin(outliers['Province'])]
    
    # Sort options
    st.sidebar.markdown("### 🔢 Sorting")
    sort_column = st.sidebar.selectbox(
        "Sort by",
        df.columns.tolist()
    )
    sort_order = st.sidebar.radio("Order", ["Ascending", "Descending"])
    
    df = df.sort_values(
        sort_column,
        ascending=(sort_order == "Ascending")
    )
    
    # Apply button
    if st.sidebar.button("🔄 Refresh Data", type="primary"):
        st.rerun()
    
    # ============================================
    # MAIN CONTENT
    # ============================================
    
    # Summary statistics
    st.markdown("### 📊 Data Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("Total Rows", f"{len(df):,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("Provinces", f"{df['Province'].nunique()}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("Years", f"{df['Year'].nunique()}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("Total GWh", f"{df['Electricity_GWh'].sum():,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("Avg GWh", f"{df['Electricity_GWh'].mean():,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Data Table",
        "📊 Statistics",
        "📈 Quick Viz",
        "🔍 Column Analysis"
    ])
    
    # ============================================
    # TAB 1: DATA TABLE
    # ============================================
    with tab1:
        st.markdown("### 📋 Interactive Data Table")
        
        # Column selector
        available_columns = df.columns.tolist()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_columns = st.multiselect(
                "Select Columns to Display",
                available_columns,
                default=available_columns[:6] if len(available_columns) > 6 else available_columns
            )
        
        with col2:
            page_size = st.selectbox(
                "Rows per page",
                [10, 25, 50, 100, 500],
                index=2
            )
        
        if selected_columns:
            df_display = df[selected_columns]
        else:
            df_display = df
        
        # Display dataframe with styling
        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
        
        # Add conditional formatting for numeric columns
        styled_df = df_display.head(page_size)
        
        # Format numeric columns
        format_dict = {}
        for col in styled_df.select_dtypes(include=['float64', 'int64']).columns:
            if 'GWh' in col:
                format_dict[col] = '{:,.2f}'
            elif '%' in col or 'Growth' in col:
                format_dict[col] = '{:+.2f}'
            else:
                format_dict[col] = '{:,.0f}'
        
        st.dataframe(
            styled_df.style.format(format_dict).background_gradient(
                subset=[c for c in styled_df.columns if c in ['Electricity_GWh', 'Growth_%', 'YoY_Growth_%']],
                cmap='YlOrRd'
            ),
            height=600,
            use_container_width=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Pagination info
        st.info(f"Showing {min(page_size, len(df))} of {len(df)} rows")
        
        # Download options
        st.markdown("---")
        st.markdown("### 💾 Download Filtered Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download as CSV",
                data=csv,
                file_name="filtered_data.csv",
                mime="text/csv"
            )
        
        with col2:
            # Download selected columns only
            if selected_columns:
                csv_selected = df[selected_columns].to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download Selected Columns",
                    data=csv_selected,
                    file_name="selected_columns.csv",
                    mime="text/csv"
                )
        
        with col3:
            # Download summary statistics
            summary = df.describe().to_csv().encode('utf-8')
            st.download_button(
                "📥 Download Statistics",
                data=summary,
                file_name="statistics.csv",
                mime="text/csv"
            )
    
    # ============================================
    # TAB 2: STATISTICS
    # ============================================
    with tab2:
        st.markdown("### 📊 Descriptive Statistics")
        
        # Overall statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Overall Statistics")
            
            stats_df = df['Electricity_GWh'].describe().to_frame()
            stats_df.columns = ['Value']
            stats_df['Value'] = stats_df['Value'].apply(lambda x: f"{x:,.2f}")
            
            st.dataframe(stats_df, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Percentiles")
            
            if len(selected_years) == 1:
                percentiles = calculate_percentiles(df, selected_years[0])
                
                perc_df = pd.DataFrame.from_dict(
                    percentiles,
                    orient='index',
                    columns=['Value (GWh)']
                )
                perc_df['Value (GWh)'] = perc_df['Value (GWh)'].apply(lambda x: f"{x:,.2f}")
                
                st.dataframe(perc_df, use_container_width=True)
            else:
                st.info("Select single year for percentile analysis")
        
        # Distribution chart
        st.markdown("---")
        st.markdown("#### 📊 Distribution Visualization")
        
        fig_hist = px.histogram(
            df,
            x='Electricity_GWh',
            nbins=30,
            title='Distribution of Electricity Consumption',
            labels={'Electricity_GWh': 'Consumption (GWh)'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_hist.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Box plot by year
        if df['Year'].nunique() > 1:
            st.markdown("#### 📦 Box Plot by Year")
            
            fig_box = px.box(
                df,
                x='Year',
                y='Electricity_GWh',
                title='Consumption Distribution by Year',
                labels={'Electricity_GWh': 'Consumption (GWh)'},
                color='Year'
            )
            fig_box.update_layout(height=400)
            st.plotly_chart(fig_box, use_container_width=True)
    
    # ============================================
    # TAB 3: QUICK VISUALIZATION
    # ============================================
    with tab3:
        st.markdown("### 📈 Quick Visualization")
        
        viz_type = st.selectbox(
            "Select Visualization Type",
            ["Bar Chart", "Scatter Plot", "Line Chart", "Pie Chart", "Treemap"]
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            x_axis = st.selectbox("X-Axis", df.columns.tolist(), index=1)
        
        with col2:
            y_axis = st.selectbox("Y-Axis", df.columns.tolist(), index=2)
        
        # Color option
        color_by = st.selectbox(
            "Color by (optional)",
            ["None"] + df.columns.tolist()
        )
        
        color_column = None if color_by == "None" else color_by
        
        # Create visualization
        if viz_type == "Bar Chart":
            # Aggregate if needed
            df_viz = df.groupby(x_axis)[y_axis].mean().reset_index()
            
            fig = px.bar(
                df_viz,
                x=x_axis,
                y=y_axis,
                title=f'{y_axis} by {x_axis}',
                color=color_column if color_column in df_viz.columns else None
            )
        
        elif viz_type == "Scatter Plot":
            fig = px.scatter(
                df,
                x=x_axis,
                y=y_axis,
                title=f'{y_axis} vs {x_axis}',
                color=color_column,
                hover_data=['Province'] if 'Province' in df.columns else None
            )
        
        elif viz_type == "Line Chart":
            fig = px.line(
                df,
                x=x_axis,
                y=y_axis,
                title=f'{y_axis} over {x_axis}',
                color=color_column,
                markers=True
            )
        
        elif viz_type == "Pie Chart":
            # Aggregate for pie
            df_pie = df.groupby(x_axis)[y_axis].sum().reset_index()
            
            fig = px.pie(
                df_pie,
                names=x_axis,
                values=y_axis,
                title=f'{y_axis} Distribution by {x_axis}'
            )
        
        else:  # Treemap
            if 'Region' in df.columns and 'Province' in df.columns:
                fig = px.treemap(
                    df,
                    path=['Region', 'Province'],
                    values='Electricity_GWh',
                    title='Hierarchical View: Region > Province',
                    color='Electricity_GWh',
                    color_continuous_scale='Reds'
                )
            else:
                st.warning("Treemap requires 'Region' and 'Province' columns")
                fig = None
        
        if fig:
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
    
    # ============================================
    # TAB 4: COLUMN ANALYSIS
    # ============================================
    with tab4:
        st.markdown("### 🔍 Column Analysis")
        
        selected_column = st.selectbox(
            "Select Column to Analyze",
            df.columns.tolist()
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### 📊 {selected_column} Statistics")
            
            if df[selected_column].dtype in ['float64', 'int64']:
                col_stats = {
                    'Count': df[selected_column].count(),
                    'Mean': df[selected_column].mean(),
                    'Median': df[selected_column].median(),
                    'Std Dev': df[selected_column].std(),
                    'Min': df[selected_column].min(),
                    'Max': df[selected_column].max(),
                    'Range': df[selected_column].max() - df[selected_column].min(),
                    'Unique': df[selected_column].nunique()
                }
                
                stats_display = pd.DataFrame.from_dict(
                    col_stats,
                    orient='index',
                    columns=['Value']
                )
                
                # Format numbers
                stats_display['Value'] = stats_display['Value'].apply(
                    lambda x: f"{x:,.2f}" if isinstance(x, float) else f"{x:,}"
                )
                
                st.dataframe(stats_display, use_container_width=True)
            
            else:
                # For categorical columns
                value_counts = df[selected_column].value_counts()
                
                st.markdown(f"**Unique Values:** {len(value_counts)}")
                st.markdown(f"**Most Common:** {value_counts.index[0]}")
                st.markdown(f"**Count:** {value_counts.values[0]}")
        
        with col2:
            st.markdown(f"#### 📈 {selected_column} Distribution")
            
            if df[selected_column].dtype in ['float64', 'int64']:
                # Histogram for numeric
                fig_dist = px.histogram(
                    df,
                    x=selected_column,
                    title=f'Distribution of {selected_column}',
                    nbins=20
                )
                st.plotly_chart(fig_dist, use_container_width=True)
            else:
                # Bar chart for categorical
                value_counts = df[selected_column].value_counts().head(10)
                
                fig_cat = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f'Top 10 {selected_column}',
                    labels={'x': selected_column, 'y': 'Count'}
                )
                st.plotly_chart(fig_cat, use_container_width=True)
        
        # Missing values
        st.markdown("---")
        st.markdown("#### 🔍 Missing Values Analysis")
        
        missing_df = pd.DataFrame({
            'Column': df.columns,
            'Missing': df.isnull().sum().values,
            'Percentage': (df.isnull().sum().values / len(df) * 100).round(2)
        })
        
        missing_df = missing_df[missing_df['Missing'] > 0].sort_values('Missing', ascending=False)
        
        if len(missing_df) > 0:
            st.dataframe(missing_df, use_container_width=True)
        else:
            st.success("✅ No missing values found!")

if __name__ == "__main__":
    main()