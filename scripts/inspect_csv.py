"""
CSV Inspector Script
Helper untuk inspect dan debug CSV files
"""

import pandas as pd
from pathlib import Path


def inspect_csv(filepath):
    """
    Inspect CSV file untuk debugging
    """
    print(f"\n{'='*70}")
    print(f"INSPECTING: {filepath}")
    print(f"{'='*70}\n")
    
    # Read raw
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 Total lines in file: {len(lines)}")
    print(f"\n🔍 First 10 lines (raw):")
    for i, line in enumerate(lines[:10], 1):
        print(f"   {i:2d}: {repr(line)}")
    
    # Try pandas
    print(f"\n📊 Pandas read_csv:")
    try:
        df = pd.read_csv(filepath)
        print(f"   ✅ Success! Shape: {df.shape}")
        print(f"\n   Columns: {df.columns.tolist()}")
        print(f"\n   First 5 rows:")
        print(df.head())
        
        print(f"\n   Data types:")
        print(df.dtypes)
        
        print(f"\n   Null values:")
        print(df.isnull().sum())
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Try with skiprows
    print(f"\n📊 Pandas read_csv (skiprows=1):")
    try:
        df = pd.read_csv(filepath, skiprows=1)
        print(f"   ✅ Success! Shape: {df.shape}")
        print(f"   Columns: {df.columns.tolist()}")
        print(f"\n   First 5 rows:")
        print(df.head())
        
        # Check for problematic values
        if df.shape[1] >= 2:
            col1 = df.iloc[:, 0]
            col2 = df.iloc[:, 1]
            
            print(f"\n   Column 1 (Province) check:")
            print(f"      • Type: {col1.dtype}")
            print(f"      • Null: {col1.isna().sum()}")
            print(f"      • Unique: {col1.nunique()}")
            
            print(f"\n   Column 2 (Electricity) check:")
            print(f"      • Type: {col2.dtype}")
            print(f"      • Null: {col2.isna().sum()}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    # Inspect all CSV files
    data_dir = Path('data/raw')
    
    csv_files = list(data_dir.glob('electricity_*.csv'))
    
    if not csv_files:
        print(f"❌ No CSV files found in {data_dir}")
    else:
        for csv_file in sorted(csv_files):
            inspect_csv(csv_file)
            print("\n" + "="*70 + "\n")