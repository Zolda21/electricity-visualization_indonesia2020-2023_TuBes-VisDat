"""
Geospatial Processing Module
Fungsi untuk merge data CSV dengan GeoJSON
"""

import pandas as pd
import geopandas as gpd
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


# Import mapping dictionary
from src.utils.province_mapping import (
    PROVINCE_MAPPING, 
    PROVINSI_PEMEKARAN,
    get_geojson_name,
    get_unmapped_provinces
)


def prepare_geojson(gdf: gpd.GeoDataFrame, 
                   province_col: str = 'Propinsi') -> gpd.GeoDataFrame:
    """
    Prepare GeoJSON data untuk merge
    
    Parameters:
    -----------
    gdf : gpd.GeoDataFrame
        Raw GeoDataFrame dari file GeoJSON
    province_col : str
        Nama kolom yang berisi nama provinsi
    
    Returns:
    --------
    gpd.GeoDataFrame : GeoDataFrame yang sudah diproses
    """
    gdf = gdf.copy()
    
    # Normalize kolom provinsi
    if province_col in gdf.columns:
        gdf[province_col] = gdf[province_col].str.strip().str.upper()
        print(f"✅ Normalized {len(gdf)} provinces in GeoJSON")
    else:
        raise ValueError(f"Column '{province_col}' not found in GeoDataFrame!")
    
    return gdf


def add_geojson_names(df: pd.DataFrame, 
                     province_col: str = 'Province') -> pd.DataFrame:
    """
    Tambahkan kolom dengan nama provinsi format GeoJSON
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame dengan data listrik
    province_col : str
        Nama kolom provinsi
    
    Returns:
    --------
    pd.DataFrame : DataFrame dengan kolom tambahan 'Province_GeoJSON'
    """
    df = df.copy()
    
    # Map CSV names ke GeoJSON names
    df['Province_GeoJSON'] = df[province_col].apply(get_geojson_name)
    
    # Check unmapped provinces
    unmapped = df[df['Province_GeoJSON'].isna()][province_col].unique()
    
    if len(unmapped) > 0:
        print(f"⚠️  {len(unmapped)} province(s) tidak ter-mapping:")
        for prov in unmapped:
            if prov in PROVINSI_PEMEKARAN:
                print(f"   - {prov} (Provinsi pemekaran - belum ada di GeoJSON)")
            else:
                print(f"   - {prov}")
    
    mapped_count = df['Province_GeoJSON'].notna().sum()
    print(f"✅ Mapped {mapped_count}/{len(df)} rows to GeoJSON format")
    
    return df


def merge_with_geojson(df: pd.DataFrame, 
                      gdf: gpd.GeoDataFrame,
                      csv_province_col: str = 'Province_GeoJSON',
                      geo_province_col: str = 'Propinsi',
                      how: str = 'left') -> gpd.GeoDataFrame:
    """
    Merge data listrik dengan GeoJSON
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame dengan data listrik (sudah ada kolom Province_GeoJSON)
    gdf : gpd.GeoDataFrame
        GeoDataFrame dengan geometri provinsi
    csv_province_col : str
        Nama kolom provinsi di CSV
    geo_province_col : str
        Nama kolom provinsi di GeoJSON
    how : str
        Tipe merge ('left', 'right', 'inner', 'outer')
    
    Returns:
    --------
    gpd.GeoDataFrame : Merged GeoDataFrame dengan data + geometri
    """
    # Prepare GeoJSON
    gdf = prepare_geojson(gdf, province_col=geo_province_col)
    
    # Merge
    merged = gdf.merge(
        df,
        left_on=geo_province_col,
        right_on=csv_province_col,
        how=how
    )
    
    print(f"\n📍 Merge completed:")
    print(f"   • Original CSV rows: {len(df)}")
    print(f"   • GeoJSON features: {len(gdf)}")
    print(f"   • Merged rows: {len(merged)}")
    
    # Check unmatched
    if how == 'left':
        unmatched = merged[merged[csv_province_col].isna()]
        if len(unmatched) > 0:
            print(f"   ⚠️  {len(unmatched)} geometri tanpa data CSV")
    
    return merged


def create_province_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Buat summary konsumsi per provinsi (untuk single year atau agregat)
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame dengan data listrik
    
    Returns:
    --------
    pd.DataFrame : Summary per provinsi
    """
    if 'Year' in df.columns:
        # Kalau ada multi-year, group by province dan year
        summary = df.groupby(['Province', 'Year']).agg({
            'Electricity_GWh': 'sum'
        }).reset_index()
    else:
        # Single year
        summary = df.groupby('Province').agg({
            'Electricity_GWh': 'sum'
        }).reset_index()
    
    return summary


def filter_valid_provinces(df: pd.DataFrame, 
                          province_col: str = 'Province') -> pd.DataFrame:
    """
    Filter hanya provinsi yang ada di GeoJSON
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame dengan data listrik
    province_col : str
        Nama kolom provinsi
    
    Returns:
    --------
    pd.DataFrame : DataFrame hanya dengan provinsi valid
    """
    df = df.copy()
    
    # Add GeoJSON names
    df = add_geojson_names(df, province_col=province_col)
    
    # Filter hanya yang mapped
    df_valid = df[df['Province_GeoJSON'].notna()].copy()
    
    removed = len(df) - len(df_valid)
    if removed > 0:
        print(f"🗑️  Removed {removed} rows dengan provinsi tidak valid")
    
    return df_valid


def get_merge_statistics(df: pd.DataFrame, 
                        gdf: gpd.GeoDataFrame) -> Dict:
    """
    Dapatkan statistik matching antara CSV dan GeoJSON
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame dengan data listrik
    gdf : gpd.GeoDataFrame
        GeoDataFrame dengan geometri
    
    Returns:
    --------
    dict : Dictionary berisi statistik matching
    """
    # Get unique provinces
    csv_provinces = set(df['Province'].unique())
    geo_provinces = set(gdf['Propinsi'].unique())
    
    # Add mapping
    df_mapped = add_geojson_names(df)
    mapped_provinces = set(df_mapped['Province_GeoJSON'].dropna().unique())
    
    stats = {
        'csv_provinces_count': len(csv_provinces),
        'geojson_provinces_count': len(geo_provinces),
        'mapped_provinces_count': len(mapped_provinces),
        'unmapped_csv': csv_provinces - set(PROVINCE_MAPPING.keys()),
        'unmatched_geojson': geo_provinces - set(PROVINCE_MAPPING.values()),
    }
    
    print("\n📊 Merge Statistics:")
    print(f"   • CSV provinces: {stats['csv_provinces_count']}")
    print(f"   • GeoJSON provinces: {stats['geojson_provinces_count']}")
    print(f"   • Successfully mapped: {stats['mapped_provinces_count']}")
    
    if stats['unmapped_csv']:
        print(f"\n   ⚠️  Unmapped in CSV ({len(stats['unmapped_csv'])}):")
        for prov in sorted(stats['unmapped_csv']):
            print(f"      - {prov}")
    
    return stats


# Testing
if __name__ == "__main__":
    print("=== Testing Geo Processing Module ===\n")
    
    # Example would require actual files
    # gdf = gpd.read_file('data/raw/indonesia_provinces.geojson')
    # df = pd.read_csv('data/interim/combined_clean.csv')
    # df_mapped = add_geojson_names(df)
    # merged = merge_with_geojson(df_mapped, gdf)