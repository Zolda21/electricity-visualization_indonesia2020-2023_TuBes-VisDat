"""
EDA Explorations Module
Reusable functions untuk exploratory data analysis
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional

from ..utils.config import (
    COL_PROVINCE, COL_YEAR, COL_ELECTRICITY,
    REGION_MAPPING, AVAILABLE_YEARS
)


# ============================================
# TOP/BOTTOM ANALYSIS
# ============================================

def get_top_provinces(df: pd.DataFrame,
                     year: int,
                     n: int = 10,
                     return_values: bool = False) -> List[str]:
    """
    Get top N provinces by consumption for specific year
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    n : int
        Number of provinces
    return_values : bool
        If True, return DataFrame with values
    
    Returns:
    --------
    list or pd.DataFrame : Province names or full data
    """
    df_year = df[df[COL_YEAR] == year].nlargest(n, COL_ELECTRICITY)
    
    if return_values:
        return df_year
    else:
        return df_year[COL_PROVINCE].tolist()


def get_bottom_provinces(df: pd.DataFrame,
                        year: int,
                        n: int = 10,
                        return_values: bool = False) -> List[str]:
    """
    Get bottom N provinces by consumption for specific year
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    n : int
        Number of provinces
    return_values : bool
        If True, return DataFrame with values
    
    Returns:
    --------
    list or pd.DataFrame : Province names or full data
    """
    df_year = df[df[COL_YEAR] == year].nsmallest(n, COL_ELECTRICITY)
    
    if return_values:
        return df_year
    else:
        return df_year[COL_PROVINCE].tolist()


def compare_top_provinces_across_years(df: pd.DataFrame,
                                       n: int = 10) -> pd.DataFrame:
    """
    Compare if top N provinces remain consistent across years
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    n : int
        Number of top provinces
    
    Returns:
    --------
    pd.DataFrame : Comparison table
    """
    comparison = {}
    
    for year in sorted(df[COL_YEAR].unique()):
        top_provs = get_top_provinces(df, year, n)
        comparison[year] = top_provs
    
    # Convert to DataFrame
    max_len = max(len(v) for v in comparison.values())
    for key in comparison:
        comparison[key] = comparison[key] + [None] * (max_len - len(comparison[key]))
    
    result = pd.DataFrame(comparison)
    result.index.name = 'Rank'
    result.index += 1
    
    return result


# ============================================
# GROWTH ANALYSIS
# ============================================

def get_fastest_growing_provinces(df: pd.DataFrame,
                                 start_year: int,
                                 end_year: int,
                                 n: int = 10) -> pd.DataFrame:
    """
    Get provinces with highest growth rate
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    start_year : int
        Starting year
    end_year : int
        Ending year
    n : int
        Number of provinces
    
    Returns:
    --------
    pd.DataFrame : Top growing provinces
    """
    # Calculate CAGR
    df_start = df[df[COL_YEAR] == start_year][[COL_PROVINCE, COL_ELECTRICITY]]
    df_end = df[df[COL_YEAR] == end_year][[COL_PROVINCE, COL_ELECTRICITY]]
    
    merged = df_start.merge(df_end, on=COL_PROVINCE, suffixes=('_start', '_end'))
    
    n_years = end_year - start_year
    merged['CAGR_%'] = ((merged[f'{COL_ELECTRICITY}_end'] / merged[f'{COL_ELECTRICITY}_start']) ** (1/n_years) - 1) * 100
    
    result = merged.nlargest(n, 'CAGR_%')[[COL_PROVINCE, f'{COL_ELECTRICITY}_start', f'{COL_ELECTRICITY}_end', 'CAGR_%']]
    result.columns = [COL_PROVINCE, f'{start_year}_GWh', f'{end_year}_GWh', 'CAGR_%']
    
    return result


def get_slowest_growing_provinces(df: pd.DataFrame,
                                 start_year: int,
                                 end_year: int,
                                 n: int = 10) -> pd.DataFrame:
    """
    Get provinces with lowest growth rate (or declining)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    start_year : int
        Starting year
    end_year : int
        Ending year
    n : int
        Number of provinces
    
    Returns:
    --------
    pd.DataFrame : Slowest growing provinces
    """
    df_start = df[df[COL_YEAR] == start_year][[COL_PROVINCE, COL_ELECTRICITY]]
    df_end = df[df[COL_YEAR] == end_year][[COL_PROVINCE, COL_ELECTRICITY]]
    
    merged = df_start.merge(df_end, on=COL_PROVINCE, suffixes=('_start', '_end'))
    
    n_years = end_year - start_year
    merged['CAGR_%'] = ((merged[f'{COL_ELECTRICITY}_end'] / merged[f'{COL_ELECTRICITY}_start']) ** (1/n_years) - 1) * 100
    
    result = merged.nsmallest(n, 'CAGR_%')[[COL_PROVINCE, f'{COL_ELECTRICITY}_start', f'{COL_ELECTRICITY}_end', 'CAGR_%']]
    result.columns = [COL_PROVINCE, f'{start_year}_GWh', f'{end_year}_GWh', 'CAGR_%']
    
    return result


# ============================================
# REGIONAL ANALYSIS
# ============================================

def analyze_by_region(df: pd.DataFrame, year: int = None) -> pd.DataFrame:
    """
    Aggregate and analyze consumption by region
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int, optional
        Specific year to analyze (None = all years)
    
    Returns:
    --------
    pd.DataFrame : Regional analysis
    """
    # Add region if not present
    if 'Region' not in df.columns:
        df = df.copy()
        df['Region'] = df[COL_PROVINCE].map(REGION_MAPPING)
    
    # Filter by year if specified
    if year:
        df = df[df[COL_YEAR] == year]
    
    # Aggregate
    regional = df.groupby('Region').agg({
        COL_ELECTRICITY: ['sum', 'mean', 'median', 'std', 'min', 'max'],
        COL_PROVINCE: 'nunique'
    }).reset_index()
    
    # Flatten columns
    regional.columns = ['Region', 'Total_GWh', 'Mean_GWh', 'Median_GWh', 
                       'Std_GWh', 'Min_GWh', 'Max_GWh', 'Province_Count']
    
    # Sort by total
    regional = regional.sort_values('Total_GWh', ascending=False)
    
    return regional


def compare_java_vs_outer_islands(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare consumption between Java and outer islands
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    pd.DataFrame : Comparison by year
    """
    # Add region
    if 'Region' not in df.columns:
        df = df.copy()
        df['Region'] = df[COL_PROVINCE].map(REGION_MAPPING)
    
    # Create Java vs Non-Java category
    df['Island_Group'] = df['Region'].apply(lambda x: 'Jawa' if x == 'Jawa' else 'Luar Jawa')
    
    # Aggregate by year and group
    comparison = df.groupby([COL_YEAR, 'Island_Group']).agg({
        COL_ELECTRICITY: 'sum',
        COL_PROVINCE: 'nunique'
    }).reset_index()
    
    comparison.columns = ['Year', 'Island_Group', 'Total_GWh', 'Province_Count']
    
    # Pivot for easier comparison
    pivot = comparison.pivot(index='Year', columns='Island_Group', values='Total_GWh')
    pivot['Java_Share_%'] = (pivot['Jawa'] / (pivot['Jawa'] + pivot['Luar Jawa'])) * 100
    
    return pivot


# ============================================
# DISTRIBUTION ANALYSIS
# ============================================

def get_distribution_summary(df: pd.DataFrame, year: int) -> Dict:
    """
    Get comprehensive distribution statistics
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    
    Returns:
    --------
    dict : Distribution metrics
    """
    df_year = df[df[COL_YEAR] == year][COL_ELECTRICITY]
    
    Q1 = df_year.quantile(0.25)
    Q3 = df_year.quantile(0.75)
    IQR = Q3 - Q1
    
    summary = {
        'year': year,
        'count': len(df_year),
        'mean': df_year.mean(),
        'median': df_year.median(),
        'std': df_year.std(),
        'min': df_year.min(),
        'max': df_year.max(),
        'range': df_year.max() - df_year.min(),
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        'cv': (df_year.std() / df_year.mean()) * 100,  # Coefficient of variation
        'skewness': df_year.skew(),
        'kurtosis': df_year.kurtosis()
    }
    
    return summary


def identify_outliers(df: pd.DataFrame, year: int, method: str = 'iqr') -> pd.DataFrame:
    """
    Identify outlier provinces
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    method : str
        'iqr' or 'zscore'
    
    Returns:
    --------
    pd.DataFrame : Outlier provinces
    """
    df_year = df[df[COL_YEAR] == year].copy()
    
    if method == 'iqr':
        Q1 = df_year[COL_ELECTRICITY].quantile(0.25)
        Q3 = df_year[COL_ELECTRICITY].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df_year[(df_year[COL_ELECTRICITY] < lower_bound) | 
                          (df_year[COL_ELECTRICITY] > upper_bound)]
        outliers['Outlier_Type'] = outliers[COL_ELECTRICITY].apply(
            lambda x: 'High' if x > upper_bound else 'Low'
        )
    
    elif method == 'zscore':
        mean = df_year[COL_ELECTRICITY].mean()
        std = df_year[COL_ELECTRICITY].std()
        df_year['Z_Score'] = (df_year[COL_ELECTRICITY] - mean) / std
        
        outliers = df_year[abs(df_year['Z_Score']) > 2]
        outliers['Outlier_Type'] = outliers['Z_Score'].apply(
            lambda x: 'High' if x > 0 else 'Low'
        )
    
    return outliers


# ============================================
# TREND ANALYSIS
# ============================================

def analyze_national_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze national consumption trend over years
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    pd.DataFrame : National trend with growth rates
    """
    national = df.groupby(COL_YEAR).agg({
        COL_ELECTRICITY: ['sum', 'mean', 'median'],
        COL_PROVINCE: 'count'
    }).reset_index()
    
    national.columns = ['Year', 'Total_GWh', 'Mean_GWh', 'Median_GWh', 'Data_Points']
    
    # Calculate YoY growth
    national['YoY_Growth_%'] = national['Total_GWh'].pct_change() * 100
    national['YoY_Change_GWh'] = national['Total_GWh'].diff()
    
    return national


def identify_trend_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify trend patterns per province (increasing, decreasing, stable)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    pd.DataFrame : Trend classification per province
    """
    patterns = []
    
    for province in df[COL_PROVINCE].unique():
        df_prov = df[df[COL_PROVINCE] == province].sort_values(COL_YEAR)
        
        # Calculate overall trend
        first_value = df_prov.iloc[0][COL_ELECTRICITY]
        last_value = df_prov.iloc[-1][COL_ELECTRICITY]
        change_pct = ((last_value - first_value) / first_value) * 100
        
        # Calculate volatility
        volatility = df_prov[COL_ELECTRICITY].std() / df_prov[COL_ELECTRICITY].mean()
        
        # Classify trend
        if change_pct > 10:
            trend = 'Strong Increase'
        elif change_pct > 2:
            trend = 'Moderate Increase'
        elif change_pct > -2:
            trend = 'Stable'
        elif change_pct > -10:
            trend = 'Moderate Decrease'
        else:
            trend = 'Strong Decrease'
        
        patterns.append({
            COL_PROVINCE: province,
            'Start_Value': first_value,
            'End_Value': last_value,
            'Change_%': change_pct,
            'Volatility': volatility,
            'Trend': trend
        })
    
    return pd.DataFrame(patterns)


# ============================================
# COMPARATIVE ANALYSIS
# ============================================

def compare_provinces(df: pd.DataFrame, 
                     provinces: List[str]) -> pd.DataFrame:
    """
    Compare multiple provinces across all years
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    provinces : list
        List of province names to compare
    
    Returns:
    --------
    pd.DataFrame : Comparison table
    """
    df_compare = df[df[COL_PROVINCE].isin(provinces)].copy()
    
    # Pivot for comparison
    pivot = df_compare.pivot(
        index=COL_YEAR,
        columns=COL_PROVINCE,
        values=COL_ELECTRICITY
    )
    
    return pivot


def generate_insights_summary(df: pd.DataFrame) -> Dict:
    """
    Generate comprehensive insights summary
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    dict : Key insights
    """
    latest_year = df[COL_YEAR].max()
    earliest_year = df[COL_YEAR].min()
    
    # Top provinces
    top_province = get_top_provinces(df, latest_year, 1, return_values=True).iloc[0]
    
    # Fastest growing
    fastest = get_fastest_growing_provinces(df, earliest_year, latest_year, 1).iloc[0]
    
    # National total
    national_latest = df[df[COL_YEAR] == latest_year][COL_ELECTRICITY].sum()
    national_earliest = df[df[COL_YEAR] == earliest_year][COL_ELECTRICITY].sum()
    national_growth = ((national_latest - national_earliest) / national_earliest) * 100
    
    insights = {
        'latest_year': int(latest_year),
        'top_province': {
            'name': top_province[COL_PROVINCE],
            'consumption': float(top_province[COL_ELECTRICITY]),
        },
        'fastest_growing': {
            'name': fastest[COL_PROVINCE],
            'cagr': float(fastest['CAGR_%']),
        },
        'national_total': {
            'latest': float(national_latest),
            'earliest': float(national_earliest),
            'growth_%': float(national_growth)
        },
        'total_provinces': int(df[COL_PROVINCE].nunique())
    }
    
    return insights


# Testing
if __name__ == "__main__":
    print("=== EDA Explorations Module Test ===\n")
    
    # Create sample data
    sample_data = pd.DataFrame({
        COL_PROVINCE: ['DKI JAKARTA', 'JAWA BARAT', 'JAWA TIMUR', 'BALI', 'ACEH'] * 4,
        COL_YEAR: [2020]*5 + [2021]*5 + [2022]*5 + [2023]*5,
        COL_ELECTRICITY: [
            32000, 49500, 37600, 4900, 2900,  # 2020
            33000, 51000, 39000, 4700, 3000,  # 2021
            34500, 53000, 40500, 5400, 3100,  # 2022
            36000, 55000, 42000, 6300, 3400   # 2023
        ]
    })
    
    print("✅ Sample data created\n")
    
    # Test functions
    print("🔍 Top 3 provinces (2023):")
    top_3 = get_top_provinces(sample_data, 2023, 3)
    print(f"   {top_3}\n")
    
    print("📈 Fastest growing provinces:")
    fastest = get_fastest_growing_provinces(sample_data, 2020, 2023, 3)
    print(fastest)
    
    print("\n✅ EDA Explorations module ready!")