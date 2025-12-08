"""
Debug script untuk cek provinsi yang hilang
"""

import pandas as pd
from pathlib import Path

def check_all_years():
    """Check provinsi yang ada di setiap tahun"""
    
    years = [2020, 2021, 2022, 2023]
    all_provinces = {}
    
    for year in years:
        filepath = Path(f'data/raw/electricity_{year}.csv')
        
        # Read dengan berbagai cara untuk debug
        print(f"\n{'='*60}")
        print(f"CHECKING: {filepath.name}")
        print(f"{'='*60}")
        
        # Method 1: skiprows=3 (current)
        df1 = pd.read_csv(filepath, skiprows=3, encoding='utf-8-sig')
        df1.columns = ['Province', 'Electricity_GWh']
        df1 = df1[df1['Province'].notna()].copy()
        
        print(f"\nMethod 1 (skiprows=3):")
        print(f"  Rows loaded: {len(df1)}")
        print(f"  Unique provinces: {df1['Province'].nunique()}")
        
        # Check for Kalimantan Selatan
        kalsel = df1[df1['Province'].str.contains('KALIMANTAN SELATAN', case=False, na=False)]
        if len(kalsel) > 0:
            print(f"  ✅ KALIMANTAN SELATAN found: {kalsel['Electricity_GWh'].values[0]}")
        else:
            print(f"  ❌ KALIMANTAN SELATAN NOT FOUND!")
        
        # Store provinces for this year
        all_provinces[year] = set(df1['Province'].str.upper().tolist())
    
    # Find provinces that appear in some years but not others
    print(f"\n{'='*60}")
    print("PROVINCE CONSISTENCY CHECK")
    print(f"{'='*60}")
    
    # Get union of all provinces
    all_prov_union = set()
    for provs in all_provinces.values():
        all_prov_union.update(provs)
    
    print(f"\nTotal unique provinces across all years: {len(all_prov_union)}")
    
    # Check which provinces are missing in which years
    print(f"\nProvinces missing by year:")
    for year in years:
        missing = all_prov_union - all_provinces[year]
        if missing:
            print(f"\n  {year}: {len(missing)} missing")
            for prov in sorted(missing):
                print(f"    - {prov}")
        else:
            print(f"\n  {year}: ✅ All provinces present ({len(all_provinces[year])})")
    
    # Check which provinces appear in ALL years
    common_provinces = all_provinces[2020]
    for year in [2021, 2022, 2023]:
        common_provinces = common_provinces.intersection(all_provinces[year])
    
    print(f"\n{'='*60}")
    print(f"Provinces present in ALL 4 years: {len(common_provinces)}")
    print(f"{'='*60}")
    
    # List provinces NOT in all years
    inconsistent = all_prov_union - common_provinces
    if inconsistent:
        print(f"\n⚠️  Provinces with inconsistent data:")
        for prov in sorted(inconsistent):
            years_present = [year for year in years if prov in all_provinces[year]]
            print(f"  • {prov:35s} → Present in: {years_present}")


def check_raw_file_2020():
    """Deep check pada file 2020"""
    
    print(f"\n{'='*60}")
    print("DEEP CHECK: electricity_2020.csv")
    print(f"{'='*60}")
    
    filepath = Path('data/raw/electricity_2020.csv')
    
    # Read ALL lines
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    print(f"\nTotal lines in file: {len(lines)}")
    
    # Check for KALIMANTAN SELATAN
    print(f"\nSearching for 'KALIMANTAN SELATAN'...")
    for i, line in enumerate(lines, 1):
        if 'KALIMANTAN SELATAN' in line.upper():
            print(f"  Line {i}: {line.strip()}")
    
    # Check for all Kalimantan provinces
    print(f"\nAll Kalimantan provinces in file:")
    for i, line in enumerate(lines, 1):
        if 'KALIMANTAN' in line.upper():
            print(f"  Line {i}: {line.strip()}")


if __name__ == "__main__":
    print("🔍 DEBUGGING MISSING PROVINCES\n")
    
    # Check all years
    check_all_years()
    
    # Deep check 2020
    check_raw_file_2020()
    
    print(f"\n{'='*60}")
    print("✅ DEBUG COMPLETED!")
    print(f"{'='*60}")