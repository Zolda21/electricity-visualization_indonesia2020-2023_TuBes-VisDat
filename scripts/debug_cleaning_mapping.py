"""
Debug script untuk cek cleaning dan mapping process
"""

import sys
sys.path.append('.')

import pandas as pd
import geopandas as gpd
from pathlib import Path

from src.data.load import load_multiple_csv
from src.data.clean import clean_electricity_data
from src.data.geo_processing import add_geojson_names
from src.utils.province_mapping import PROVINCE_MAPPING

def debug_full_pipeline():
    """Test full pipeline dan cek di mana provinsi hilang"""
    
    print("="*70)
    print("STEP 1: LOAD RAW DATA")
    print("="*70)
    
    df_raw = load_multiple_csv('data/raw/', years=[2020, 2021, 2022, 2023])
    print(f"\n📊 Raw data: {df_raw.shape}")
    print(f"   Unique provinces: {df_raw['Province'].nunique()}")
    
    # Check KALIMANTAN SELATAN
    kalsel_raw = df_raw[df_raw['Province'].str.upper() == 'KALIMANTAN SELATAN']
    print(f"\n🔍 KALIMANTAN SELATAN in raw data: {len(kalsel_raw)} rows")
    if len(kalsel_raw) > 0:
        print(kalsel_raw[['Province', 'Year', 'Electricity_GWh']])
    
    print("\n" + "="*70)
    print("STEP 2: CLEAN DATA")
    print("="*70)
    
    df_clean = clean_electricity_data(df_raw)
    print(f"\n📊 Clean data: {df_clean.shape}")
    print(f"   Unique provinces: {df_clean['Province'].nunique()}")
    
    # Check KALIMANTAN SELATAN after cleaning
    kalsel_clean = df_clean[df_clean['Province'] == 'KALIMANTAN SELATAN']
    print(f"\n🔍 KALIMANTAN SELATAN after cleaning: {len(kalsel_clean)} rows")
    if len(kalsel_clean) > 0:
        print(kalsel_clean[['Province', 'Year', 'Electricity_GWh']])
    else:
        print("   ❌ MISSING! Check why it was dropped...")
        
        # Check if it exists with different name
        print("\n   Checking similar names:")
        similar = df_clean[df_clean['Province'].str.contains('KALIMANTAN', na=False)]
        print(f"   Found {len(similar)} Kalimantan provinces:")
        for prov in sorted(similar['Province'].unique()):
            print(f"      • {prov}")
    
    print("\n" + "="*70)
    print("STEP 3: ADD GEOJSON MAPPING")
    print("="*70)
    
    df_mapped = add_geojson_names(df_clean, province_col='Province')
    print(f"\n📊 Mapped data: {df_mapped.shape}")
    
    # Check KALIMANTAN SELATAN mapping
    kalsel_mapped = df_mapped[df_mapped['Province'] == 'KALIMANTAN SELATAN']
    print(f"\n🔍 KALIMANTAN SELATAN mapping:")
    if len(kalsel_mapped) > 0:
        print(f"   CSV name: {kalsel_mapped.iloc[0]['Province']}")
        print(f"   GeoJSON name: {kalsel_mapped.iloc[0]['Province_GeoJSON']}")
        print(f"   Is mapped: {'✅' if pd.notna(kalsel_mapped.iloc[0]['Province_GeoJSON']) else '❌'}")
    else:
        print("   ❌ Province not found in cleaned data")
    
    # Check all unmapped provinces
    unmapped = df_mapped[df_mapped['Province_GeoJSON'].isna()]
    print(f"\n⚠️  Total unmapped rows: {len(unmapped)}")
    if len(unmapped) > 0:
        print(f"   Unmapped provinces:")
        for prov in sorted(unmapped['Province'].unique()):
            print(f"      • {prov}")
    
    print("\n" + "="*70)
    print("STEP 4: CHECK MAPPING DICTIONARY")
    print("="*70)
    
    print(f"\n📖 Total mappings in dictionary: {len(PROVINCE_MAPPING)}")
    
    # Check if KALIMANTAN SELATAN is in mapping
    if 'KALIMANTAN SELATAN' in PROVINCE_MAPPING:
        print(f"   ✅ KALIMANTAN SELATAN → {PROVINCE_MAPPING['KALIMANTAN SELATAN']}")
    else:
        print(f"   ❌ KALIMANTAN SELATAN not in mapping dictionary!")
        
        # Check what's in dictionary
        print(f"\n   Kalimantan provinces in mapping:")
        for key in sorted(PROVINCE_MAPPING.keys()):
            if 'KALIMANTAN' in key:
                print(f"      • {key} → {PROVINCE_MAPPING[key]}")
    
    print("\n" + "="*70)
    print("STEP 5: CHECK GEOJSON")
    print("="*70)
    
    gdf = gpd.read_file('data/raw/indonesia_provinces.geojson')
    print(f"\n📍 GeoJSON provinces: {len(gdf)}")
    
    # Check if KALIMANTANSELATAN exists in GeoJSON
    kalimantan_geo = gdf[gdf['Propinsi'].str.contains('KALIMANTAN', na=False)]
    print(f"\n   Kalimantan provinces in GeoJSON:")
    for prov in sorted(kalimantan_geo['Propinsi'].unique()):
        print(f"      • {prov}")
    
    if 'KALIMANTANSELATAN' in gdf['Propinsi'].values:
        print(f"\n   ✅ KALIMANTANSELATAN found in GeoJSON")
    else:
        print(f"\n   ❌ KALIMANTANSELATAN NOT in GeoJSON")
    
    print("\n" + "="*70)
    print("STEP 6: SAVE CLEAN DATA FOR INSPECTION")
    print("="*70)
    
    # Save for manual inspection
    output_file = Path('data/interim/debug_clean_with_mapping.csv')
    df_mapped.to_csv(output_file, index=False)
    print(f"\n💾 Saved to: {output_file}")
    print(f"   You can open this file to manually inspect the data")
    
    # Show provinces that ARE successfully mapped
    print(f"\n✅ Successfully mapped provinces ({df_mapped['Province_GeoJSON'].notna().sum()} rows):")
    mapped_provinces = df_mapped[df_mapped['Province_GeoJSON'].notna()]['Province'].unique()
    print(f"   Total: {len(mapped_provinces)} unique provinces")
    
    return df_raw, df_clean, df_mapped, gdf


if __name__ == "__main__":
    print("🔍 DEBUGGING FULL CLEANING & MAPPING PIPELINE\n")
    
    try:
        df_raw, df_clean, df_mapped, gdf = debug_full_pipeline()
        
        print("\n" + "="*70)
        print("✅ DEBUG COMPLETED!")
        print("="*70)
        
        print(f"\nSummary:")
        print(f"  • Raw data: {df_raw.shape[0]} rows, {df_raw['Province'].nunique()} provinces")
        print(f"  • Clean data: {df_clean.shape[0]} rows, {df_clean['Province'].nunique()} provinces")
        print(f"  • Mapped data: {df_mapped['Province_GeoJSON'].notna().sum()} rows successfully mapped")
        print(f"  • GeoJSON: {len(gdf)} geometries")
        
    except Exception as e:
        print(f"\n❌ ERROR during debug:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()