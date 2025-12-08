"""
Test script untuk verify load module fix
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from src.data.load import load_single_csv, load_multiple_csv

def test_single_file():
    """Test loading single file"""
    print("="*70)
    print("TEST 1: Load Single CSV (2020)")
    print("="*70 + "\n")
    
    filepath = Path('data/raw/electricity_2020.csv')
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return
    
    df = load_single_csv(filepath, year=2020)
    
    print(f"✅ Loaded successfully!")
    print(f"\n📊 Shape: {df.shape}")
    print(f"\n🔍 Data types:")
    print(df.dtypes)
    
    print(f"\n📋 First 10 rows:")
    print(df.head(10))
    
    print(f"\n📋 Last 5 rows:")
    print(df.tail(5))
    
    # Check for NaN in Province
    nan_count = df['Province'].isna().sum()
    print(f"\n⚠️  NaN values in Province: {nan_count}")
    
    if nan_count > 0:
        print(f"   Rows with NaN Province:")
        print(df[df['Province'].isna()])
    
    # Check data types in Province column
    print(f"\n🔍 Province column value types:")
    type_counts = df['Province'].apply(type).value_counts()
    print(type_counts)
    
    # Check for numeric strings (year)
    numeric_provinces = df[df['Province'].astype(str).str.match(r'^\d{4}$', na=False)]
    if len(numeric_provinces) > 0:
        print(f"\n⚠️  Found year values in Province column:")
        print(numeric_provinces)
    else:
        print(f"\n✅ No year values in Province column")
    
    return df


def test_multiple_files():
    """Test loading multiple files"""
    print("\n\n" + "="*70)
    print("TEST 2: Load Multiple CSVs (2020-2023)")
    print("="*70 + "\n")
    
    try:
        df = load_multiple_csv('data/raw/', years=[2020, 2021, 2022, 2023])
        
        print(f"\n✅ All files loaded!")
        print(f"\n📊 Combined shape: {df.shape}")
        print(f"\n📅 Years: {sorted(df['Year'].unique())}")
        print(f"🗺️  Total unique provinces: {df['Province'].nunique()}")
        
        print(f"\n📊 Records per year:")
        print(df.groupby('Year').size())
        
        print(f"\n🔍 Sample data (first 15 rows):")
        print(df.head(15))
        
        # Check for NaN
        print(f"\n⚠️  NaN check:")
        print(df.isna().sum())
        
        # Check for 'INDONESIA' row
        indonesia_rows = df[df['Province'].str.upper().str.contains('INDONESIA', na=False)]
        print(f"\n🔍 'INDONESIA' rows found: {len(indonesia_rows)}")
        if len(indonesia_rows) > 0:
            print(indonesia_rows)
        
        return df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_province_values():
    """Test specific province values"""
    print("\n\n" + "="*70)
    print("TEST 3: Check Province Values Quality")
    print("="*70 + "\n")
    
    df = load_multiple_csv('data/raw/', years=[2020, 2021, 2022, 2023])
    
    if df is None:
        return
    
    print("🔍 Unique provinces found:")
    provinces = sorted(df['Province'].unique())
    for i, prov in enumerate(provinces, 1):
        print(f"   {i:2d}. {prov}")
    
    print(f"\n✅ Total unique: {len(provinces)}")
    
    # Check for suspicious values
    print(f"\n⚠️  Checking for suspicious values...")
    
    # Check for year values
    year_pattern = df[df['Province'].astype(str).str.match(r'^\d{4}$', na=False)]
    if len(year_pattern) > 0:
        print(f"   ❌ Found year values: {len(year_pattern)}")
        print(year_pattern[['Province', 'Year']])
    else:
        print(f"   ✅ No year values")
    
    # Check for very short names (< 3 chars)
    short_names = df[df['Province'].str.len() < 3]
    if len(short_names) > 0:
        print(f"   ❌ Found very short names: {len(short_names)}")
        print(short_names[['Province', 'Year']])
    else:
        print(f"   ✅ No suspiciously short names")
    
    # Check for numeric types
    non_string = df[~df['Province'].apply(lambda x: isinstance(x, str))]
    if len(non_string) > 0:
        print(f"   ❌ Found non-string values: {len(non_string)}")
        print(non_string[['Province', 'Year']])
    else:
        print(f"   ✅ All values are strings")


if __name__ == "__main__":
    print("\n🧪 TESTING LOAD MODULE FIX\n")
    
    # Run tests
    df1 = test_single_file()
    df2 = test_multiple_files()
    test_province_values()
    
    print("\n\n" + "="*70)
    print("✅ ALL TESTS COMPLETED!")
    print("="*70)