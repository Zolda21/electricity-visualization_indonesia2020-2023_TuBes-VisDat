"""
Data Cleaning Module
Fungsi untuk cleaning dan normalisasi data
"""

import pandas as pd
import numpy as np
import re
from typing import Union
import warnings
warnings.filterwarnings('ignore')


def remove_indonesia_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    Hapus row 'INDONESIA' (total nasional) dari dataset
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame yang berisi data listrik
    
    Returns:
    --------
    pd.DataFrame : DataFrame tanpa row 'INDONESIA'
    """
    # Clean province names dulu
    df['Province'] = df['Province'].str.strip().str.upper()
    
    # Filter out INDONESIA
    df_clean = df[df['Province'] != 'INDONESIA'].copy()
    
    removed = len(df) - len(df_clean)
    if removed > 0:
        print(f"🗑️  Removed {removed} row(s) with 'INDONESIA'")
    
    return df_clean


def clean_numeric_column(series: pd.Series) -> pd.Series:
    """
    Bersihkan kolom numerik (handle koma, titik, dash)
    
    Parameters:
    -----------
    series : pd.Series
        Series yang akan dibersihkan
    
    Returns:
    --------
    pd.Series : Series dengan nilai numerik yang sudah clean
    """
    # Convert to string first
    series = series.astype(str)
    
    # Handle '-' as NaN
    series = series.replace('-', np.nan)
    
    # Remove whitespace
    series = series.str.strip()
    
    # Replace comma with nothing (assuming format: 1,234.56 atau 1.234,56)
    # Deteksi format: jika ada koma setelah titik, maka format Eropa (1.234,56)
    def parse_number(val):
        if pd.isna(val) or val == '':
            return np.nan
        
        val = str(val).strip()
        
        # Jika ada koma dan titik, deteksi mana yang desimal
        if ',' in val and '.' in val:
            # Format: 1,234.56 (US format)
            if val.rindex(',') < val.rindex('.'):
                val = val.replace(',', '')
            # Format: 1.234,56 (EU format)
            else:
                val = val.replace('.', '').replace(',', '.')
        # Hanya koma (assume ribuan jika >3 digit, desimal jika <=2 digit after comma)
        elif ',' in val:
            parts = val.split(',')
            if len(parts[-1]) <= 2 and len(parts[-1]) > 0:
                val = val.replace(',', '.')  # Desimal
            else:
                val = val.replace(',', '')  # Ribuan
        
        try:
            return float(val)
        except:
            return np.nan
    
    return series.apply(parse_number)


def normalize_province_names(df: pd.DataFrame, 
                            province_col: str = 'Province') -> pd.DataFrame:
    """
    Normalisasi nama provinsi (uppercase, trim, standardize)
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame yang berisi kolom provinsi
    province_col : str
        Nama kolom provinsi
    
    Returns:
    --------
    pd.DataFrame : DataFrame dengan nama provinsi yang sudah dinormalisasi
    """
    df = df.copy()
    
    # Uppercase dan trim
    df[province_col] = df[province_col].str.strip().str.upper()
    
    # Remove multiple spaces
    df[province_col] = df[province_col].str.replace(r'\s+', ' ', regex=True)
    
    # Standardize common variations
    replacements = {
        'D.I. YOGYAKARTA': 'DI YOGYAKARTA',
        'D I YOGYAKARTA': 'DI YOGYAKARTA',
        'YOGYAKARTA': 'DI YOGYAKARTA',
        'DAERAH ISTIMEWA YOGYAKARTA': 'DI YOGYAKARTA',
        
        'D.K.I. JAKARTA': 'DKI JAKARTA',
        'D K I JAKARTA': 'DKI JAKARTA',
        'JAKARTA': 'DKI JAKARTA',
        
        'KEP BANGKA BELITUNG': 'KEP. BANGKA BELITUNG',
        'KEPULAUAN BANGKA BELITUNG': 'KEP. BANGKA BELITUNG',
        'BANGKA BELITUNG': 'KEP. BANGKA BELITUNG',
        
        'KEP RIAU': 'KEP. RIAU',
        'KEPULAUAN RIAU': 'KEP. RIAU',
    }
    
    df[province_col] = df[province_col].replace(replacements)
    
    print(f"✅ Normalized {df[province_col].nunique()} unique provinces")
    
    return df


def handle_missing_values(df: pd.DataFrame, 
                         electricity_col: str = 'Electricity_GWh',
                         method: str = 'drop') -> pd.DataFrame:
    """
    Handle missing values di kolom electricity
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame yang akan diproses
    electricity_col : str
        Nama kolom electricity
    method : str
        Metode handling: 'drop', 'fill_zero', 'fill_mean'
    
    Returns:
    --------
    pd.DataFrame : DataFrame setelah handling missing values
    """
    df = df.copy()
    
    missing_count = df[electricity_col].isna().sum()
    
    if missing_count > 0:
        print(f"⚠️  Found {missing_count} missing values in '{electricity_col}'")
        
        if method == 'drop':
            df = df.dropna(subset=[electricity_col])
            print(f"   → Dropped rows with missing values")
        
        elif method == 'fill_zero':
            df[electricity_col] = df[electricity_col].fillna(0)
            print(f"   → Filled missing values with 0")
        
        elif method == 'fill_mean':
            mean_val = df[electricity_col].mean()
            df[electricity_col] = df[electricity_col].fillna(mean_val)
            print(f"   → Filled missing values with mean: {mean_val:.2f}")
    
    return df


def validate_data_quality(df: pd.DataFrame) -> dict:
    """
    Validasi kualitas data dan return summary
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame yang akan divalidasi
    
    Returns:
    --------
    dict : Dictionary berisi info validasi
    """
    report = {
        'total_rows': len(df),
        'total_provinces': df['Province'].nunique(),
        'total_years': df['Year'].nunique() if 'Year' in df.columns else 1,
        'missing_values': df.isnull().sum().to_dict(),
        'duplicates': df.duplicated().sum(),
        'negative_values': (df['Electricity_GWh'] < 0).sum(),
        'zero_values': (df['Electricity_GWh'] == 0).sum(),
    }
    
    print("\n📋 Data Quality Report:")
    print(f"  • Total rows: {report['total_rows']}")
    print(f"  • Unique provinces: {report['total_provinces']}")
    print(f"  • Years covered: {report['total_years']}")
    print(f"  • Duplicate rows: {report['duplicates']}")
    print(f"  • Negative values: {report['negative_values']}")
    print(f"  • Zero values: {report['zero_values']}")
    print(f"  • Missing values:")
    for col, count in report['missing_values'].items():
        if count > 0:
            print(f"    - {col}: {count}")
    
    return report


def clean_electricity_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline lengkap untuk cleaning data
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw data dari load module
    
    Returns:
    --------
    pd.DataFrame : Clean data ready for analysis
    """
    print("🧹 Starting data cleaning pipeline...\n")
    
    # Step 0: Remove rows with empty/NaN province names
    df = df[df['Province'].notna()].copy()
    df = df[df['Province'].astype(str).str.strip() != ''].copy()
    
    # Step 1: Remove INDONESIA row
    df = remove_indonesia_row(df)
    
    # Step 2: Normalize province names
    df = normalize_province_names(df)
    
    # Step 3: Clean numeric column
    df['Electricity_GWh'] = clean_numeric_column(df['Electricity_GWh'])
    
    # Step 4: Handle missing values
    df = handle_missing_values(df, method='drop')
    
    # Step 5: Remove duplicates
    df = df.drop_duplicates()
    
    # Step 6: Sort data
    if 'Year' in df.columns:
        df = df.sort_values(['Year', 'Province']).reset_index(drop=True)
    else:
        df = df.sort_values('Province').reset_index(drop=True)
    
    # Step 7: Validate
    validate_data_quality(df)
    
    print("\n✅ Data cleaning completed!")
    
    return df


# Testing
if __name__ == "__main__":
    print("=== Testing Clean Module ===\n")
    
    # Example test data
    test_data = {
        'Province': ['ACEH', 'DKI JAKARTA', 'JAWA BARAT', 'INDONESIA', 'PAPUA'],
        'Year': [2020, 2020, 2020, 2020, 2020],
        'Electricity_GWh': ['2,937.99', '32166.72', '49542.25', '241405.61', '-']
    }
    df_test = pd.DataFrame(test_data)
    
    print("Before cleaning:")
    print(df_test)
    
    print("\n" + "="*50 + "\n")
    
    df_clean = clean_electricity_data(df_test)
    
    print("\nAfter cleaning:")
    print(df_clean)