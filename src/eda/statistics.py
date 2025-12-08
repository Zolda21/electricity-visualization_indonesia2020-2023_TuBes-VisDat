"""
EDA Statistics Module
Statistical calculations and hypothesis testing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats

from ..utils.config import (
    COL_PROVINCE, COL_YEAR, COL_ELECTRICITY
)


# ============================================
# DESCRIPTIVE STATISTICS
# ============================================

def calculate_descriptive_stats(df: pd.DataFrame,
                                year: int = None,
                                by_province: bool = False) -> pd.DataFrame:
    """
    Calculate comprehensive descriptive statistics
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int, optional
        Specific year (None = all years)
    by_province : bool
        If True, calculate per province
    
    Returns:
    --------
    pd.DataFrame : Descriptive statistics
    """
    # Filter by year if specified
    if year:
        df = df[df[COL_YEAR] == year]
    
    if by_province:
        # Stats per province
        stats_df = df.groupby(COL_PROVINCE)[COL_ELECTRICITY].agg([
            'count', 'mean', 'median', 'std', 'var', 
            'min', 'max', 'sum',
            ('Q1', lambda x: x.quantile(0.25)),
            ('Q3', lambda x: x.quantile(0.75)),
            ('IQR', lambda x: x.quantile(0.75) - x.quantile(0.25)),
            ('CV', lambda x: (x.std() / x.mean()) * 100),
            ('skew', lambda x: x.skew()),
            ('kurt', lambda x: x.kurtosis())
        ]).reset_index()
    else:
        # Overall stats
        series = df[COL_ELECTRICITY]
        stats_dict = {
            'Count': series.count(),
            'Mean': series.mean(),
            'Median': series.median(),
            'Std': series.std(),
            'Variance': series.var(),
            'Min': series.min(),
            'Max': series.max(),
            'Range': series.max() - series.min(),
            'Q1': series.quantile(0.25),
            'Q3': series.quantile(0.75),
            'IQR': series.quantile(0.75) - series.quantile(0.25),
            'CV_%': (series.std() / series.mean()) * 100,
            'Skewness': series.skew(),
            'Kurtosis': series.kurtosis()
        }
        stats_df = pd.DataFrame([stats_dict])
    
    return stats_df


def calculate_percentiles(df: pd.DataFrame,
                         year: int,
                         percentiles: List[float] = [10, 25, 50, 75, 90]) -> Dict:
    """
    Calculate specific percentiles
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    percentiles : list
        List of percentiles (0-100)
    
    Returns:
    --------
    dict : Percentile values
    """
    df_year = df[df[COL_YEAR] == year]
    
    result = {}
    for p in percentiles:
        result[f'P{p}'] = df_year[COL_ELECTRICITY].quantile(p/100)
    
    return result


def calculate_mode(df: pd.DataFrame, year: int) -> float:
    """
    Calculate mode (most frequent value) - rounded to nearest 100
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    
    Returns:
    --------
    float : Mode value
    """
    df_year = df[df[COL_YEAR] == year]
    
    # Round to nearest 100 for mode calculation
    rounded = (df_year[COL_ELECTRICITY] / 100).round() * 100
    mode_val = rounded.mode().values[0] if len(rounded.mode()) > 0 else None
    
    return mode_val


# ============================================
# DISPERSION & VARIABILITY
# ============================================

def calculate_dispersion_metrics(df: pd.DataFrame, year: int) -> Dict:
    """
    Calculate various dispersion metrics
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    
    Returns:
    --------
    dict : Dispersion metrics
    """
    df_year = df[df[COL_YEAR] == year][COL_ELECTRICITY]
    
    metrics = {
        'Range': df_year.max() - df_year.min(),
        'Variance': df_year.var(),
        'Std_Deviation': df_year.std(),
        'MAD': np.mean(np.abs(df_year - df_year.mean())),  # Mean Absolute Deviation
        'IQR': df_year.quantile(0.75) - df_year.quantile(0.25),
        'Coefficient_of_Variation_%': (df_year.std() / df_year.mean()) * 100,
        'Relative_Std_%': (df_year.std() / df_year.mean()) * 100
    }
    
    return metrics


def calculate_gini_coefficient(df: pd.DataFrame, year: int) -> float:
    """
    Calculate Gini coefficient (inequality measure)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    
    Returns:
    --------
    float : Gini coefficient (0=perfect equality, 1=perfect inequality)
    """
    df_year = df[df[COL_YEAR] == year][COL_ELECTRICITY].values
    df_year = np.sort(df_year)
    
    n = len(df_year)
    index = np.arange(1, n + 1)
    
    gini = (2 * np.sum(index * df_year)) / (n * np.sum(df_year)) - (n + 1) / n
    
    return gini


def calculate_concentration_ratio(df: pd.DataFrame,
                                 year: int,
                                 top_n: int = 5) -> Dict:
    """
    Calculate concentration ratio (share of top N provinces)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    top_n : int
        Number of top provinces
    
    Returns:
    --------
    dict : Concentration metrics
    """
    df_year = df[df[COL_YEAR] == year]
    total = df_year[COL_ELECTRICITY].sum()
    
    top_n_sum = df_year.nlargest(top_n, COL_ELECTRICITY)[COL_ELECTRICITY].sum()
    concentration_ratio = (top_n_sum / total) * 100
    
    return {
        f'Top_{top_n}_Sum': top_n_sum,
        'Total': total,
        f'CR{top_n}_%': concentration_ratio
    }


# ============================================
# DISTRIBUTION SHAPE
# ============================================

def test_normality(df: pd.DataFrame, year: int) -> Dict:
    """
    Test for normal distribution using multiple tests
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    
    Returns:
    --------
    dict : Test results
    """
    df_year = df[df[COL_YEAR] == year][COL_ELECTRICITY]
    
    # Shapiro-Wilk test
    shapiro_stat, shapiro_p = stats.shapiro(df_year)
    
    # Kolmogorov-Smirnov test
    ks_stat, ks_p = stats.kstest(df_year, 'norm')
    
    # Anderson-Darling test
    anderson_result = stats.anderson(df_year)
    
    results = {
        'Shapiro_Wilk': {
            'statistic': shapiro_stat,
            'p_value': shapiro_p,
            'is_normal': shapiro_p > 0.05
        },
        'Kolmogorov_Smirnov': {
            'statistic': ks_stat,
            'p_value': ks_p,
            'is_normal': ks_p > 0.05
        },
        'Anderson_Darling': {
            'statistic': anderson_result.statistic,
            'critical_values': anderson_result.critical_values.tolist()
        },
        'Skewness': df_year.skew(),
        'Kurtosis': df_year.kurtosis()
    }
    
    return results


def classify_distribution(df: pd.DataFrame, year: int) -> str:
    """
    Classify distribution shape
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    
    Returns:
    --------
    str : Distribution classification
    """
    df_year = df[df[COL_YEAR] == year][COL_ELECTRICITY]
    
    skewness = df_year.skew()
    kurtosis = df_year.kurtosis()
    
    # Classify based on skewness
    if abs(skewness) < 0.5:
        skew_class = "Symmetric"
    elif skewness > 0:
        skew_class = "Right-skewed (Positive skew)"
    else:
        skew_class = "Left-skewed (Negative skew)"
    
    # Classify based on kurtosis
    if abs(kurtosis) < 0.5:
        kurt_class = "Mesokurtic (Normal)"
    elif kurtosis > 0:
        kurt_class = "Leptokurtic (Heavy tails)"
    else:
        kurt_class = "Platykurtic (Light tails)"
    
    return f"{skew_class}, {kurt_class}"


# ============================================
# CORRELATION & RELATIONSHIPS
# ============================================

def calculate_correlation_with_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlation between consumption and year per province
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    pd.DataFrame : Correlation coefficients
    """
    correlations = []
    
    for province in df[COL_PROVINCE].unique():
        df_prov = df[df[COL_PROVINCE] == province]
        
        if len(df_prov) > 2:  # Need at least 3 points
            corr = df_prov[COL_YEAR].corr(df_prov[COL_ELECTRICITY])
            correlations.append({
                COL_PROVINCE: province,
                'Correlation': corr,
                'Strength': 'Strong' if abs(corr) > 0.7 else 'Moderate' if abs(corr) > 0.4 else 'Weak',
                'Direction': 'Positive' if corr > 0 else 'Negative'
            })
    
    return pd.DataFrame(correlations)


def calculate_regional_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlation matrix between regions
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame (must have Region column)
    
    Returns:
    --------
    pd.DataFrame : Correlation matrix
    """
    from ..utils.config import REGION_MAPPING
    
    # Add region if not present
    if 'Region' not in df.columns:
        df = df.copy()
        df['Region'] = df[COL_PROVINCE].map(REGION_MAPPING)
    
    # Aggregate by region and year
    regional = df.groupby(['Region', COL_YEAR])[COL_ELECTRICITY].sum().reset_index()
    
    # Pivot for correlation
    pivot = regional.pivot(index=COL_YEAR, columns='Region', values=COL_ELECTRICITY)
    
    # Calculate correlation
    corr_matrix = pivot.corr()
    
    return corr_matrix


# ============================================
# HYPOTHESIS TESTING
# ============================================

def compare_two_years(df: pd.DataFrame,
                     year1: int,
                     year2: int,
                     paired: bool = True) -> Dict:
    """
    Statistical comparison between two years
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year1 : int
        First year
    year2 : int
        Second year
    paired : bool
        If True, use paired t-test (same provinces)
    
    Returns:
    --------
    dict : Test results
    """
    data1 = df[df[COL_YEAR] == year1][COL_ELECTRICITY]
    data2 = df[df[COL_YEAR] == year2][COL_ELECTRICITY]
    
    if paired:
        # Paired t-test
        t_stat, p_value = stats.ttest_rel(data1, data2)
        test_type = "Paired t-test"
    else:
        # Independent t-test
        t_stat, p_value = stats.ttest_ind(data1, data2)
        test_type = "Independent t-test"
    
    # Wilcoxon test (non-parametric alternative)
    w_stat, w_p_value = stats.wilcoxon(data1, data2) if paired else stats.mannwhitneyu(data1, data2)
    
    results = {
        'test_type': test_type,
        'year1': year1,
        'year2': year2,
        'mean_year1': data1.mean(),
        'mean_year2': data2.mean(),
        'difference': data2.mean() - data1.mean(),
        't_statistic': t_stat,
        'p_value': p_value,
        'is_significant': p_value < 0.05,
        'wilcoxon_statistic': w_stat,
        'wilcoxon_p_value': w_p_value
    }
    
    return results


def anova_across_years(df: pd.DataFrame) -> Dict:
    """
    ANOVA test to compare means across all years
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    
    Returns:
    --------
    dict : ANOVA results
    """
    # Group data by year
    groups = [df[df[COL_YEAR] == year][COL_ELECTRICITY].values 
              for year in sorted(df[COL_YEAR].unique())]
    
    # Perform ANOVA
    f_stat, p_value = stats.f_oneway(*groups)
    
    results = {
        'f_statistic': f_stat,
        'p_value': p_value,
        'is_significant': p_value < 0.05,
        'interpretation': 'Significant difference exists between years' if p_value < 0.05 
                         else 'No significant difference between years'
    }
    
    return results


# ============================================
# OUTLIER DETECTION
# ============================================

def detect_outliers_zscore(df: pd.DataFrame,
                          year: int,
                          threshold: float = 3.0) -> pd.DataFrame:
    """
    Detect outliers using Z-score method
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    threshold : float
        Z-score threshold (default: 3)
    
    Returns:
    --------
    pd.DataFrame : Outlier data
    """
    df_year = df[df[COL_YEAR] == year].copy()
    
    mean = df_year[COL_ELECTRICITY].mean()
    std = df_year[COL_ELECTRICITY].std()
    
    df_year['Z_Score'] = (df_year[COL_ELECTRICITY] - mean) / std
    df_year['Is_Outlier'] = abs(df_year['Z_Score']) > threshold
    
    outliers = df_year[df_year['Is_Outlier']]
    
    return outliers[[COL_PROVINCE, COL_ELECTRICITY, 'Z_Score']]


def detect_outliers_iqr(df: pd.DataFrame,
                       year: int,
                       multiplier: float = 1.5) -> pd.DataFrame:
    """
    Detect outliers using IQR method
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    multiplier : float
        IQR multiplier (default: 1.5)
    
    Returns:
    --------
    pd.DataFrame : Outlier data
    """
    df_year = df[df[COL_YEAR] == year].copy()
    
    Q1 = df_year[COL_ELECTRICITY].quantile(0.25)
    Q3 = df_year[COL_ELECTRICITY].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    df_year['Is_Outlier'] = (df_year[COL_ELECTRICITY] < lower_bound) | \
                           (df_year[COL_ELECTRICITY] > upper_bound)
    df_year['Outlier_Type'] = df_year.apply(
        lambda row: 'High' if row[COL_ELECTRICITY] > upper_bound 
                    else ('Low' if row[COL_ELECTRICITY] < lower_bound else 'Normal'),
        axis=1
    )
    
    outliers = df_year[df_year['Is_Outlier']]
    
    return outliers[[COL_PROVINCE, COL_ELECTRICITY, 'Outlier_Type']]


# ============================================
# SUMMARY REPORT GENERATION
# ============================================

def generate_statistical_report(df: pd.DataFrame, year: int) -> Dict:
    """
    Generate comprehensive statistical report
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    year : int
        Year to analyze
    
    Returns:
    --------
    dict : Complete statistical report
    """
    report = {
        'year': year,
        'descriptive': calculate_descriptive_stats(df, year, by_province=False).to_dict('records')[0],
        'dispersion': calculate_dispersion_metrics(df, year),
        'distribution': {
            'classification': classify_distribution(df, year),
            'normality_tests': test_normality(df, year)
        },
        'inequality': {
            'gini_coefficient': calculate_gini_coefficient(df, year),
            'concentration_ratio_top5': calculate_concentration_ratio(df, year, 5)
        },
        'outliers': {
            'iqr_method': len(detect_outliers_iqr(df, year)),
            'zscore_method': len(detect_outliers_zscore(df, year))
        }
    }
    
    return report


# Testing
if __name__ == "__main__":
    print("=== Statistics Module Test ===\n")
    
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
    
    # Test descriptive statistics
    print("📊 Descriptive Statistics (2023):")
    stats_2023 = calculate_descriptive_stats(sample_data, 2023)
    print(stats_2023)
    
    print("\n📈 Gini Coefficient (2023):")
    gini = calculate_gini_coefficient(sample_data, 2023)
    print(f"   {gini:.4f}")
    
    print("\n✅ Statistics module ready!")