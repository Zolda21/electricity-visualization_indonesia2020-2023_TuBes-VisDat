# src/eda/explorations.py (REVISI FINAL)

import pandas as pd
from src.data.transform import summarize_national, pivot_province_year

def get_basic_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghasilkan ringkasan statistik deskriptif untuk data konsumsi listrik.
    """
    print("--- Ringkasan Statistik Konsumsi Listrik (GWh) ---")
    return df['electricity_gwh'].describe().to_frame("stats")

def get_top_n_yearly(df: pd.DataFrame, n: int = 5) -> dict:
    """
    Menemukan N provinsi dengan konsumsi tertinggi untuk setiap tahun.
    """
    yearly_top_n = {}
    for year in sorted(df['year'].unique()):
        df_year = df[df['year'] == year]
        top_n = df_year.sort_values(by='electricity_gwh', ascending=False).head(n)
        yearly_top_n[year] = top_n[['province', 'electricity_gwh']].reset_index(drop=True)
        
    return yearly_top_n

def calculate_yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghitung pertumbuhan konsumsi listrik Year-over-Year (YoY) per provinsi.
    """
    df_pivot = pivot_province_year(df)
    
    # Hitung pertumbuhan (Current Year / Previous Year - 1) * 100
    yoy_growth = pd.DataFrame(index=df_pivot.index)
    years = sorted(df_pivot.columns)
    
    for i in range(1, len(years)):
        current_year = years[i]
        previous_year = years[i-1]
        
        # Penanganan: Hindari pembagian dengan nol
        growth_col_name = f'YoY_{previous_year}_to_{current_year}'
        yoy_growth[growth_col_name] = (
            (df_pivot[current_year] / df_pivot[previous_year]) - 1
        ) * 100
        
    yoy_growth = yoy_growth.round(2)
    return yoy_growth