"""
Helper Functions Module
General utility functions untuk data processing dan analysis
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
import json

from .config import (
    COL_PROVINCE, COL_YEAR, COL_ELECTRICITY,
    REGION_MAPPING, AVAILABLE_YEARS
)


# ============================================
# DATA VALIDATION
# ============================================

def validate_dataframe(df: pd.DataFrame, required_cols: List[str]) -> bool:
    """
    Validate DataFrame has required columns
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to validate
    required_cols : list
        List of required column names
    
    Returns:
    --------
    bool : True if valid
    
    Raises:
    -------
    ValueError : If validation fails
    """
    missing_cols = set(required_cols) - set(df.columns)
    
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    return True


def check_data_quality(df: pd.DataFrame) -> Dict:
    """
    Generate data quality report
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to check
    
    Returns:
    --------
    dict : Quality metrics
    """
    report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'dtypes': df.dtypes.to_dict(),
        'memory_usage': df.memory_usage(deep=True).sum() / 1024**2,  # MB
    }
    
    return report


# ============================================
# DATA FILTERING
# ============================================

def filter_by_year(df: pd.DataFrame, years: Union[int, List[int]]) -> pd.DataFrame:
    """
    Filter DataFrame by year(s)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    years : int or list
        Year or list of years
    
    Returns:
    --------
    pd.DataFrame : Filtered DataFrame
    """
    if isinstance(years, int):
        years = [years]
    
    return df[df[COL_YEAR].isin(years)].copy()


def filter_by_province(df: pd.DataFrame, provinces: Union[str, List[str]]) -> pd.DataFrame:
    """
    Filter DataFrame by province(s)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    provinces : str or list
        Province name(s)
    
    Returns:
    --------
    pd.DataFrame : Filtered DataFrame
    """
    if isinstance(provinces, str):
        provinces = [provinces]
    
    return df[df[COL_PROVINCE].isin(provinces)].copy()


def filter_by_region(df: pd.DataFrame, region: str) -> pd.DataFrame:
    """
    Filter DataFrame by region
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    region : str
        Region name (e.g., 'Jawa', 'Sumatera')
    
    Returns:
    --------
    pd.DataFrame : Filtered DataFrame
    """
    provinces_in_region = [
        prov for prov, reg in REGION_MAPPING.items() 
        if reg == region
    ]
    
    return filter_by_province(df, provinces_in_region)


def filter_top_n(df: pd.DataFrame, 
                year: int, 
                n: int = 10,
                ascending: bool = False) -> pd.DataFrame:
    """
    Get top N provinces for specific year
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to filter
    n : int
        Number of top provinces
    ascending : bool
        If True, get bottom N instead
    
    Returns:
    --------
    pd.DataFrame : Top N provinces
    """
    df_year = filter_by_year(df, year)
    
    if ascending:
        return df_year.nsmallest(n, COL_ELECTRICITY)
    else:
        return df_year.nlargest(n, COL_ELECTRICITY)


# ============================================
# DATA AGGREGATION
# ============================================

def aggregate_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate consumption by region
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame with Province column
    
    Returns:
    --------
    pd.DataFrame : Aggregated by region
    """
    # Add region column
    df_with_region = df.copy()
    df_with_region['Region'] = df_with_region[COL_PROVINCE].map(REGION_MAPPING)
    
    # Aggregate
    agg_df = df_with_region.groupby(['Region', COL_YEAR]).agg({
        COL_ELECTRICITY: ['sum', 'mean', 'count']
    }).reset_index()
    
    # Flatten column names
    agg_df.columns = ['Region', 'Year', 'Total_GWh', 'Mean_GWh', 'Province_Count']
    
    return agg_df


def aggregate_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate total consumption by year
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    pd.DataFrame : Yearly totals
    """
    return df.groupby(COL_YEAR).agg({
        COL_ELECTRICITY: ['sum', 'mean', 'median', 'std', 'min', 'max', 'count']
    }).reset_index()


# ============================================
# GROWTH CALCULATIONS
# ============================================

def calculate_yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Year-over-Year growth rate per province
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    pd.DataFrame : DataFrame with YoY growth columns
    """
    # Pivot data
    pivot = df.pivot(index=COL_PROVINCE, columns=COL_YEAR, values=COL_ELECTRICITY)
    
    # Calculate YoY for each year pair
    result = pd.DataFrame()
    result[COL_PROVINCE] = pivot.index
    
    years = sorted(pivot.columns)
    for i in range(1, len(years)):
        prev_year = years[i-1]
        curr_year = years[i]
        col_name = f'Growth_{prev_year}_{curr_year}_%'
        
        result[col_name] = ((pivot[curr_year] - pivot[prev_year]) / pivot[prev_year]) * 100
    
    return result


def calculate_cagr(df: pd.DataFrame, 
                  start_year: int, 
                  end_year: int) -> pd.DataFrame:
    """
    Calculate Compound Annual Growth Rate (CAGR)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    start_year : int
        Start year
    end_year : int
        End year
    
    Returns:
    --------
    pd.DataFrame : DataFrame with CAGR
    """
    # Pivot data
    pivot = df.pivot(index=COL_PROVINCE, columns=COL_YEAR, values=COL_ELECTRICITY)
    
    # Calculate CAGR
    n_years = end_year - start_year
    cagr = ((pivot[end_year] / pivot[start_year]) ** (1/n_years) - 1) * 100
    
    result = pd.DataFrame({
        COL_PROVINCE: pivot.index,
        f'CAGR_{start_year}_{end_year}_%': cagr.values
    })
    
    return result


# ============================================
# STATISTICAL FUNCTIONS
# ============================================

def detect_outliers(df: pd.DataFrame, 
                   column: str = COL_ELECTRICITY,
                   method: str = 'iqr',
                   threshold: float = 1.5) -> pd.DataFrame:
    """
    Detect outliers using IQR or Z-score method
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    column : str
        Column to check for outliers
    method : str
        'iqr' or 'zscore'
    threshold : float
        IQR multiplier or Z-score threshold
    
    Returns:
    --------
    pd.DataFrame : Rows identified as outliers
    """
    if method == 'iqr':
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    
    elif method == 'zscore':
        z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
        outliers = df[z_scores > threshold]
    
    else:
        raise ValueError(f"Unknown method: {method}. Use 'iqr' or 'zscore'")
    
    return outliers


def calculate_percentile_rank(df: pd.DataFrame,
                              year: int,
                              column: str = COL_ELECTRICITY) -> pd.DataFrame:
    """
    Calculate percentile rank for each province
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    column : str
        Column for ranking
    
    Returns:
    --------
    pd.DataFrame : DataFrame with percentile ranks
    """
    df_year = filter_by_year(df, year).copy()
    
    df_year['Percentile'] = df_year[column].rank(pct=True) * 100
    df_year['Rank'] = df_year[column].rank(ascending=False, method='min')
    
    return df_year.sort_values('Rank')


# ============================================
# DATA EXPORT
# ============================================

def export_to_csv(df: pd.DataFrame, 
                 filepath: Union[str, Path],
                 **kwargs) -> None:
    """
    Export DataFrame to CSV with standard settings
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to export
    filepath : str or Path
        Output file path
    **kwargs : dict
        Additional pandas to_csv arguments
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(filepath, index=False, encoding='utf-8', **kwargs)
    print(f"💾 Exported to: {filepath}")


def export_to_json(data: Union[Dict, List], 
                  filepath: Union[str, Path],
                  indent: int = 2) -> None:
    """
    Export data to JSON
    
    Parameters:
    -----------
    data : dict or list
        Data to export
    filepath : str or Path
        Output file path
    indent : int
        JSON indentation
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    
    print(f"💾 Exported to: {filepath}")


# ============================================
# FORMATTING
# ============================================

def format_number(value: float, 
                 decimal_places: int = 2,
                 suffix: str = '') -> str:
    """
    Format number with thousand separator
    
    Parameters:
    -----------
    value : float
        Number to format
    decimal_places : int
        Number of decimal places
    suffix : str
        Suffix to add (e.g., 'GWh', '%')
    
    Returns:
    --------
    str : Formatted string
    """
    if pd.isna(value):
        return 'N/A'
    
    formatted = f"{value:,.{decimal_places}f}{suffix}"
    return formatted


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format as percentage
    
    Parameters:
    -----------
    value : float
        Value (as decimal, e.g., 0.15 for 15%)
    decimal_places : int
        Number of decimal places
    
    Returns:
    --------
    str : Formatted percentage
    """
    return f"{value * 100:.{decimal_places}f}%"


# ============================================
# LOGGING & DEBUGGING
# ============================================

def print_dataframe_info(df: pd.DataFrame, name: str = "DataFrame") -> None:
    """
    Print comprehensive DataFrame information
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to inspect
    name : str
        Name for display
    """
    print(f"\n{'='*60}")
    print(f"{name} Information")
    print(f"{'='*60}")
    
    print(f"\n📊 Shape: {df.shape}")
    print(f"   Rows: {df.shape[0]:,}")
    print(f"   Columns: {df.shape[1]}")
    
    print(f"\n📋 Columns:")
    for col in df.columns:
        dtype = df[col].dtype
        nulls = df[col].isna().sum()
        print(f"   • {col:30s} | {str(dtype):10s} | {nulls:>6,} nulls")
    
    print(f"\n💾 Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print(f"\n🔍 Sample (first 3 rows):")
    print(df.head(3))


# Testing
if __name__ == "__main__":
    print("=== Helpers Module Test ===\n")
    
    # Create sample data
    sample_data = pd.DataFrame({
        COL_PROVINCE: ['DKI JAKARTA', 'JAWA BARAT', 'JAWA TIMUR'] * 2,
        COL_YEAR: [2020] * 3 + [2021] * 3,
        COL_ELECTRICITY: [32000, 49500, 37600, 33000, 51000, 39000]
    })
    
    print("✅ Sample data created")
    print_dataframe_info(sample_data, "Sample Data")
    
    print("\n✅ Helpers module ready!")