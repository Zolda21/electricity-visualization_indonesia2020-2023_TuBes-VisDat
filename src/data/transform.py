# src/data/transform.py

import pandas as pd
from typing import Dict, Any

# ============================================================
# BASIC TRANSFORMATIONS & AGGREGATIONS
# ============================================================

def pivot_province_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membuat pivot table dengan axis:
        index   = province
        columns = year
        values  = electricity_gwh
    Digunakan untuk heatmap, korelasi, dan visual lain.
    """
    return df.pivot(index="province", columns="year", values="electricity_gwh")


def summarize_national(df: pd.DataFrame) -> pd.DataFrame:
    """
    Total konsumsi listrik nasional per tahun.
    Supports line chart nasional dan dashboard.
    """
    return (
        df.groupby("year")["electricity_gwh"]
        .sum()
        .reset_index()
        .rename(columns={"electricity_gwh": "national_gwh"})
    )


def summarize_province_avg(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rata-rata konsumsi setiap provinsi (2020–2023).
    Dipakai untuk bar chart top-bottom dan pemeringkatan.
    """
    return (
        df.groupby("province")["electricity_gwh"]
        .mean()
        .reset_index()
        .rename(columns={"electricity_gwh": "avg_gwh"})
        .sort_values("avg_gwh", ascending=False)
    )


def top_n_provinces(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Ambil N provinsi dengan konsumsi rata-rata tertinggi.
    """
    summary = summarize_province_avg(df)
    return summary.head(n).reset_index(drop=True)


def bottom_n_provinces(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Ambil N provinsi dengan konsumsi rata-rata terendah.
    """
    summary = summarize_province_avg(df)
    return summary.tail(n).reset_index(drop=True)


# ============================================================
# KPI & DATA QUALITY CHECKS
# ============================================================

def calculate_kpi_metrics(df: pd.DataFrame, selected_year: int) -> Dict[str, Any]:
    """
    Menghitung metrik KPI utama untuk ringkasan dashboard,
    menggunakan data ringkasan nasional dan provinsi.
    """
    df_national = summarize_national(df)
    df_avg_province = summarize_province_avg(df)

    # 1. Total GWh Tahun Terpilih
    total_current = df_national[df_national['year'] == selected_year]['national_gwh'].iloc[0] if selected_year in df_national['year'].values else 0
    
    # 2. Perubahan YoY
    prev_year = selected_year - 1
    total_previous = df_national[df_national['year'] == prev_year]['national_gwh'].iloc[0] if prev_year in df_national['year'].values else 0
    
    yoy_change_percent = ((total_current - total_previous) / total_previous) * 100 if total_previous else 0
    
    # 3. Top Province (berdasarkan rata-rata 4 tahun untuk stabilitas)
    top_province_row = df_avg_province.iloc[0]
    
    return {
        'Total_GWh': total_current,
        'Top_Province': top_province_row['province'],
        'Top_Avg_GWh': top_province_row['avg_gwh'],
        'YoY_Change_Percent': yoy_change_percent
    }


def check_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Cek missing value tiap kolom."""
    return df.isna().sum().to_frame("missing_values")


def check_unique_provinces(df: pd.DataFrame) -> int:
    """Mengembalikan jumlah provinsi unik."""
    return df["province"].nunique()


def check_value_range(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mengembalikan min/max/mean per tahun untuk mengecek anomali.
    """
    return (
        df.groupby("year")["electricity_gwh"]
        .agg(["min", "max", "mean"])
        .reset_index()
    )