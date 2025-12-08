"""
Data Loading Module
Fungsi untuk loading CSV files dan GeoJSON
"""

from pathlib import Path
from typing import List, Union
import warnings

import pandas as pd
import geopandas as gpd

warnings.filterwarnings("ignore")


def load_single_csv(filepath: Union[str, Path], year: int = None) -> pd.DataFrame:
    """
    Load single CSV file konsumsi listrik per provinsi

    Parameters
    ----------
    filepath : str or Path
        Path ke file CSV
    year : int, optional
        Tahun data (ditambahkan sebagai kolom)

    Returns
    -------
    pd.DataFrame
        Kolom: [Province, Electricity_GWh, Year]
    """
    filepath = Path(filepath)

    # ---- READ CSV (FORMAT PLN BPS STYLE) ----
    df = pd.read_csv(
        filepath,
        encoding="utf-8-sig",
        skiprows=2,               # buang header + sub-header
        skip_blank_lines=True
    )

    # Ambil hanya 2 kolom utama
    df = df.iloc[:, :2]
    df.columns = ["Province", "Electricity_GWh"]

    # 1. Drop baris tanpa nama provinsi
    df = df[df["Province"].notna()]

    # 2. Pastikan Province string
    df["Province"] = df["Province"].astype(str).str.strip()

    # 3. Drop baris kosong
    df = df[df["Province"] != ""]

    # 4. Drop baris yang mengandung tahun palsu
    df = df[~df["Province"].str.match(r"^\d{4}$")]
    df = df[~df["Electricity_GWh"].astype(str).str.match(r"^\d{4}$")]

    # 5. Convert Electricity ke numeric
    df["Electricity_GWh"] = pd.to_numeric(
        df["Electricity_GWh"], errors="coerce"
    )

    # 6. Drop nilai listrik NaN
    df = df[df["Electricity_GWh"].notna()]

    # ---- ADD YEAR ----
    df["Year"] = year

    df = df[["Province", "Year", "Electricity_GWh"]]
    df.reset_index(drop=True, inplace=True)

    return df

def load_multiple_csv(
    data_dir: Union[str, Path],
    years: List[int] = [2020, 2021, 2022, 2023],
) -> pd.DataFrame:
    """
    Load multiple CSV files dan gabungkan

    Parameters
    ----------
    data_dir : str or Path
        Directory berisi file electricity_YYYY.csv
    years : list of int
        Daftar tahun yang akan diload

    Returns
    -------
    pd.DataFrame
        Kolom: [Province, Year, Electricity_GWh]
    """
    data_dir = Path(data_dir)
    all_data = []

    for year in years:
        filepath = data_dir / f"electricity_{year}.csv"

        if not filepath.exists():
            print(f"⚠️  File tidak ditemukan: {filepath}")
            continue

        try:
            df = load_single_csv(filepath, year=year)
            all_data.append(df)
            print(f"✅ Loaded {filepath.name} ({len(df)} rows)")
        except Exception as e:
            print(f"❌ Gagal load {filepath.name}: {e}")

    if not all_data:
        raise ValueError("Tidak ada file CSV yang berhasil diload.")

    combined = pd.concat(all_data, ignore_index=True)
    combined = combined[["Province", "Year", "Electricity_GWh"]]

    print("\n📊 Summary")
    print(f"- Total rows      : {len(combined)}")
    print(f"- Years available : {sorted(combined['Year'].unique())}")
    print(f"- Provinces       : {combined['Province'].nunique()}")

    return combined


def load_geojson(filepath: Union[str, Path]) -> gpd.GeoDataFrame:
    """
    Load GeoJSON file peta provinsi Indonesia

    Parameters
    ----------
    filepath : str or Path
        Path ke file GeoJSON

    Returns
    -------
    geopandas.GeoDataFrame
    """
    filepath = Path(filepath)

    try:
        gdf = gpd.read_file(filepath)
        print(f"✅ GeoJSON loaded ({len(gdf)} features)")

        if "Propinsi" in gdf.columns:
            print("📍 Kolom nama provinsi: 'Propinsi'")

        return gdf

    except Exception as e:
        raise RuntimeError(f"Gagal load GeoJSON: {e}")


def save_interim_data(
    df: pd.DataFrame,
    output_dir: Union[str, Path],
    filename: str = "combined_raw.csv",
) -> None:
    """
    Simpan data interim hasil loading

    Parameters
    ----------
    df : pd.DataFrame
        Data yang akan disimpan
    output_dir : str or Path
        Directory output
    filename : str
        Nama file output
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename
    df.to_csv(filepath, index=False)

    print(f"💾 Data saved to {filepath}")
