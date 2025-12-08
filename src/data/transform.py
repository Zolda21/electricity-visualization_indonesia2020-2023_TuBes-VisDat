"""
Data Transformation Module
Feature engineering, agregasi, dan transformasi data
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple

from ..utils.config import (
    COL_PROVINCE, COL_YEAR, COL_ELECTRICITY,
    REGION_MAPPING, AVAILABLE_YEARS
)


# ============================================
# FEATURE ENGINEERING
# ============================================

def add_region_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add region column based on province
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame with Province column
    
    Returns:
    --------
    pd.DataFrame : DataFrame with Region column
    """
    df = df.copy()
    df['Region'] = df[COL_PROVINCE].map(REGION_MAPPING)
    return df


def add_consumption_category(df: pd.DataFrame,
                            thresholds: Dict[str, float] = None) -> pd.DataFrame:
    """
    Add consumption category (Very Low, Low, Medium, High, Very High)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    thresholds : dict, optional
        Custom thresholds for categorization
    
    Returns:
    --------
    pd.DataFrame : DataFrame with Category column
    """
    if thresholds is None:
        thresholds = {
            'very_low': 1000,
            'low': 5000,
            'medium': 15000,
            'high': 30000
        }
    
    df = df.copy()
    
    def categorize(value):
        if value < thresholds['very_low']:
            return 'Sangat Rendah'
        elif value < thresholds['low']:
            return 'Rendah'
        elif value < thresholds['medium']:
            return 'Sedang'
        elif value < thresholds['high']:
            return 'Tinggi'
        else:
            return 'Sangat Tinggi'
    
    df['Category'] = df[COL_ELECTRICITY].apply(categorize)
    
    return df


def add_growth_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Year-over-Year (YoY) growth rate features
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame with Province, Year, Electricity_GWh
    
    Returns:
    --------
    pd.DataFrame : DataFrame with growth columns
    """
    df = df.copy()
    
    # Sort by province and year
    df = df.sort_values([COL_PROVINCE, COL_YEAR])
    
    # Calculate YoY growth per province
    df['YoY_Growth_%'] = df.groupby(COL_PROVINCE)[COL_ELECTRICITY].pct_change() * 100
    
    # Calculate absolute change
    df['YoY_Change_GWh'] = df.groupby(COL_PROVINCE)[COL_ELECTRICITY].diff()
    
    return df


def add_ranking_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ranking features per year
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    pd.DataFrame : DataFrame with Rank and Percentile columns
    """
    df = df.copy()
    
    # Rank by consumption (within each year)
    df['Rank'] = df.groupby(COL_YEAR)[COL_ELECTRICITY].rank(
        ascending=False, method='min'
    ).astype(int)
    
    # Percentile rank
    df['Percentile'] = df.groupby(COL_YEAR)[COL_ELECTRICITY].rank(
        pct=True
    ) * 100
    
    return df


def add_moving_average(df: pd.DataFrame, 
                      window: int = 2) -> pd.DataFrame:
    """
    Add moving average feature (useful for smoothing trends)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    window : int
        Window size for moving average
    
    Returns:
    --------
    pd.DataFrame : DataFrame with MA column
    """
    df = df.copy()
    df = df.sort_values([COL_PROVINCE, COL_YEAR])
    
    df[f'MA_{window}Y'] = df.groupby(COL_PROVINCE)[COL_ELECTRICITY].transform(
        lambda x: x.rolling(window=window, min_periods=1).mean()
    )
    
    return df


def add_share_of_total(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add column showing province's share of national total per year
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    pd.DataFrame : DataFrame with Share_% column
    """
    df = df.copy()
    
    # Calculate national total per year
    yearly_totals = df.groupby(COL_YEAR)[COL_ELECTRICITY].transform('sum')
    
    # Calculate share
    df['Share_%'] = (df[COL_ELECTRICITY] / yearly_totals) * 100
    
    return df


def add_z_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Z-score (standardized consumption) per year
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    pd.DataFrame : DataFrame with Z_Score column
    """
    df = df.copy()
    
    # Calculate Z-score within each year
    df['Z_Score'] = df.groupby(COL_YEAR)[COL_ELECTRICITY].transform(
        lambda x: (x - x.mean()) / x.std()
    )
    
    return df


# ============================================
# AGGREGATION FUNCTIONS
# ============================================

def aggregate_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate consumption by region and year
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame (must have Region column)
    
    Returns:
    --------
    pd.DataFrame : Aggregated DataFrame
    """
    # Ensure region column exists
    if 'Region' not in df.columns:
        df = add_region_column(df)
    
    agg_df = df.groupby(['Region', COL_YEAR]).agg({
        COL_ELECTRICITY: ['sum', 'mean', 'median', 'std', 'count'],
        COL_PROVINCE: 'nunique'
    }).reset_index()
    
    # Flatten column names
    agg_df.columns = [
        'Region', 'Year', 
        'Total_GWh', 'Mean_GWh', 'Median_GWh', 'Std_GWh', 
        'Data_Points', 'Province_Count'
    ]
    
    return agg_df


def pivot_for_heatmap(df: pd.DataFrame,
                     index_col: str = COL_PROVINCE,
                     column_col: str = COL_YEAR,
                     value_col: str = COL_ELECTRICITY) -> pd.DataFrame:
    """
    Pivot data untuk heatmap visualization
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    index_col : str
        Column untuk index (rows)
    column_col : str
        Column untuk columns
    value_col : str
        Column untuk values
    
    Returns:
    --------
    pd.DataFrame : Pivoted DataFrame
    """
    pivot_df = df.pivot(
        index=index_col,
        columns=column_col,
        values=value_col
    )
    
    return pivot_df


def create_comparison_table(df: pd.DataFrame,
                           years: List[int]) -> pd.DataFrame:
    """
    Create side-by-side comparison table for multiple years
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    years : list
        List of years to compare
    
    Returns:
    --------
    pd.DataFrame : Comparison table
    """
    comparison = pd.DataFrame()
    comparison[COL_PROVINCE] = df[df[COL_YEAR] == years[0]][COL_PROVINCE]
    
    for year in years:
        df_year = df[df[COL_YEAR] == year][[COL_PROVINCE, COL_ELECTRICITY]]
        df_year = df_year.rename(columns={COL_ELECTRICITY: f'{year}_GWh'})
        
        if comparison.empty:
            comparison = df_year
        else:
            comparison = comparison.merge(df_year, on=COL_PROVINCE, how='left')
    
    # Calculate total change
    if len(years) >= 2:
        first_year = f'{years[0]}_GWh'
        last_year = f'{years[-1]}_GWh'
        comparison['Change_GWh'] = comparison[last_year] - comparison[first_year]
        comparison['Change_%'] = (comparison['Change_GWh'] / comparison[first_year]) * 100
    
    return comparison


# ============================================
# TIME SERIES FEATURES
# ============================================

def calculate_cagr(df: pd.DataFrame,
                  start_year: int,
                  end_year: int) -> pd.DataFrame:
    """
    Calculate Compound Annual Growth Rate (CAGR) per province
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    start_year : int
        Starting year
    end_year : int
        Ending year
    
    Returns:
    --------
    pd.DataFrame : DataFrame with CAGR column
    """
    # Get data for start and end years
    df_start = df[df[COL_YEAR] == start_year][[COL_PROVINCE, COL_ELECTRICITY]]
    df_end = df[df[COL_YEAR] == end_year][[COL_PROVINCE, COL_ELECTRICITY]]
    
    # Merge
    merged = df_start.merge(
        df_end,
        on=COL_PROVINCE,
        suffixes=('_start', '_end')
    )
    
    # Calculate CAGR
    n_years = end_year - start_year
    merged[f'CAGR_{start_year}_{end_year}_%'] = (
        ((merged[f'{COL_ELECTRICITY}_end'] / merged[f'{COL_ELECTRICITY}_start']) ** (1/n_years) - 1) * 100
    )
    
    # Keep only Province and CAGR
    result = merged[[COL_PROVINCE, f'CAGR_{start_year}_{end_year}_%']]
    
    return result


def create_trend_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create comprehensive trend summary per province
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    pd.DataFrame : Trend summary
    """
    summary = pd.DataFrame()
    
    provinces = df[COL_PROVINCE].unique()
    
    for province in provinces:
        df_prov = df[df[COL_PROVINCE] == province].sort_values(COL_YEAR)
        
        row = {
            COL_PROVINCE: province,
            'Start_Value': df_prov.iloc[0][COL_ELECTRICITY],
            'End_Value': df_prov.iloc[-1][COL_ELECTRICITY],
            'Total_Change': df_prov.iloc[-1][COL_ELECTRICITY] - df_prov.iloc[0][COL_ELECTRICITY],
            'Percent_Change': ((df_prov.iloc[-1][COL_ELECTRICITY] / df_prov.iloc[0][COL_ELECTRICITY]) - 1) * 100,
            'Mean_Value': df_prov[COL_ELECTRICITY].mean(),
            'Max_Value': df_prov[COL_ELECTRICITY].max(),
            'Min_Value': df_prov[COL_ELECTRICITY].min(),
            'Volatility_Std': df_prov[COL_ELECTRICITY].std(),
            'Trend': 'Increasing' if df_prov.iloc[-1][COL_ELECTRICITY] > df_prov.iloc[0][COL_ELECTRICITY] else 'Decreasing'
        }
        
        summary = pd.concat([summary, pd.DataFrame([row])], ignore_index=True)
    
    return summary


# ============================================
# DATA RESHAPING
# ============================================

def wide_to_long(df: pd.DataFrame,
                id_vars: List[str],
                value_vars: List[str],
                var_name: str = 'Year',
                value_name: str = COL_ELECTRICITY) -> pd.DataFrame:
    """
    Convert wide format to long format
    
    Parameters:
    -----------
    df : pd.DataFrame
        Wide format DataFrame
    id_vars : list
        Columns to keep as identifiers
    value_vars : list
        Columns to unpivot
    var_name : str
        Name for variable column
    value_name : str
        Name for value column
    
    Returns:
    --------
    pd.DataFrame : Long format DataFrame
    """
    long_df = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=value_vars,
        var_name=var_name,
        value_name=value_name
    )
    
    return long_df


def normalize_values(df: pd.DataFrame,
                    column: str = COL_ELECTRICITY,
                    method: str = 'minmax') -> pd.DataFrame:
    """
    Normalize values using MinMax or Z-score
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    column : str
        Column to normalize
    method : str
        'minmax' or 'zscore'
    
    Returns:
    --------
    pd.DataFrame : DataFrame with normalized column
    """
    df = df.copy()
    
    if method == 'minmax':
        # MinMax scaling (0-1)
        min_val = df[column].min()
        max_val = df[column].max()
        df[f'{column}_Normalized'] = (df[column] - min_val) / (max_val - min_val)
    
    elif method == 'zscore':
        # Z-score standardization
        mean_val = df[column].mean()
        std_val = df[column].std()
        df[f'{column}_Normalized'] = (df[column] - mean_val) / std_val
    
    else:
        raise ValueError(f"Unknown method: {method}. Use 'minmax' or 'zscore'")
    
    return df


# ============================================
# COMPLETE TRANSFORMATION PIPELINE
# ============================================

def transform_complete(df: pd.DataFrame,
                      include_growth: bool = True,
                      include_ranking: bool = True,
                      include_share: bool = True) -> pd.DataFrame:
    """
    Apply complete transformation pipeline
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw clean DataFrame
    include_growth : bool
        Add growth features
    include_ranking : bool
        Add ranking features
    include_share : bool
        Add share of total
    
    Returns:
    --------
    pd.DataFrame : Fully transformed DataFrame
    """
    df_transformed = df.copy()
    
    # Add region
    df_transformed = add_region_column(df_transformed)
    
    # Add category
    df_transformed = add_consumption_category(df_transformed)
    
    # Add growth features
    if include_growth:
        df_transformed = add_growth_features(df_transformed)
    
    # Add ranking
    if include_ranking:
        df_transformed = add_ranking_features(df_transformed)
    
    # Add share
    if include_share:
        df_transformed = add_share_of_total(df_transformed)
    
    print(f"✅ Transformation complete!")
    print(f"   Original columns: {len(df.columns)}")
    print(f"   Transformed columns: {len(df_transformed.columns)}")
    print(f"   New features: {list(set(df_transformed.columns) - set(df.columns))}")
    
    return df_transformed


# Testing
if __name__ == "__main__":
    print("=== Transform Module Test ===\n")
    
    # Create sample data
    sample_data = pd.DataFrame({
        COL_PROVINCE: ['DKI JAKARTA', 'JAWA BARAT', 'JAWA TIMUR'] * 4,
        COL_YEAR: [2020]*3 + [2021]*3 + [2022]*3 + [2023]*3,
        COL_ELECTRICITY: [
            32000, 49500, 37600,  # 2020
            33000, 51000, 39000,  # 2021
            34500, 53000, 40500,  # 2022
            36000, 55000, 42000   # 2023
        ]
    })
    
    print("📊 Sample data created")
    print(f"   Shape: {sample_data.shape}\n")
    
    # Test transformations
    print("🔄 Testing transformations...\n")
    
    df_transformed = transform_complete(sample_data)
    
    print(f"\n📋 Transformed data preview:")
    print(df_transformed.head())
    
    print("\n✅ Transform module ready!")