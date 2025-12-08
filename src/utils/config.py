"""
Configuration Module
Centralized constants, paths, and settings
"""

from pathlib import Path
from typing import List

# ============================================
# PROJECT PATHS
# ============================================

# Root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
INTERIM_DATA_DIR = DATA_DIR / 'interim'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'

# Notebook directory
NOTEBOOKS_DIR = PROJECT_ROOT / 'notebooks'

# Streamlit app directory
STREAMLIT_DIR = PROJECT_ROOT / 'streamlit_app'

# Reports directory
REPORTS_DIR = PROJECT_ROOT / 'reports'
FIGURES_DIR = REPORTS_DIR / 'figures'

# 🗺️ GEOJSON: GeoJSON file path
GEOJSON_PATH = RAW_DATA_DIR / 'indonesia_provinces_std.geojson'


# ============================================
# DATA FILES
# ============================================

# CSV files
ELECTRICITY_FILES = {
    2020: RAW_DATA_DIR / 'electricity_2020.csv',
    2021: RAW_DATA_DIR / 'electricity_2021.csv',
    2022: RAW_DATA_DIR / 'electricity_2022.csv',
    2023: RAW_DATA_DIR / 'electricity_2023.csv',
}

# Processed data files
COMBINED_RAW = INTERIM_DATA_DIR / 'combined_raw.csv'
ELECTRICITY_CLEAN = PROCESSED_DATA_DIR / 'electricity_clean.csv'
ELECTRICITY_WITH_GEO = PROCESSED_DATA_DIR / 'electricity_with_geo.csv'

# 🗺️ GEOJSON: Processed GeoJSON with data
PROVINCES_2023_GEOJSON = PROCESSED_DATA_DIR / 'provinces_2023.geojson'


# ============================================
# DATA CONSTANTS
# ============================================

# Years available
AVAILABLE_YEARS: List[int] = [2020, 2021, 2022, 2023]
START_YEAR = 2020
END_YEAR = 2023

# Total provinces (before pemekaran Papua)
TOTAL_PROVINCES_BASE = 34

# Total provinces (including pemekaran Papua)
TOTAL_PROVINCES_FULL = 38

# Column names
COL_PROVINCE = 'Province'
COL_YEAR = 'Year'
COL_ELECTRICITY = 'Electricity_GWh'
COL_PROVINCE_GEO = 'Province_GeoJSON'

# 🗺️ GEOJSON: GeoJSON column name
COL_GEOJSON_PROVINCE = 'Province_std'


# ============================================
# REGIONAL GROUPING
# ============================================

REGION_MAPPING = {
    # Sumatera
    'ACEH': 'Sumatera',
    'SUMATERA UTARA': 'Sumatera',
    'SUMATERA BARAT': 'Sumatera',
    'RIAU': 'Sumatera',
    'JAMBI': 'Sumatera',
    'SUMATERA SELATAN': 'Sumatera',
    'BENGKULU': 'Sumatera',
    'LAMPUNG': 'Sumatera',
    'KEP. BANGKA BELITUNG': 'Sumatera',
    'KEP. RIAU': 'Sumatera',
    
    # Jawa
    'DKI JAKARTA': 'Jawa',
    'JAWA BARAT': 'Jawa',
    'JAWA TENGAH': 'Jawa',
    'DI YOGYAKARTA': 'Jawa',
    'JAWA TIMUR': 'Jawa',
    'BANTEN': 'Jawa',
    
    # Bali & Nusa Tenggara
    'BALI': 'Bali & Nusa Tenggara',
    'NUSA TENGGARA BARAT': 'Bali & Nusa Tenggara',
    'NUSA TENGGARA TIMUR': 'Bali & Nusa Tenggara',
    
    # Kalimantan
    'KALIMANTAN BARAT': 'Kalimantan',
    'KALIMANTAN TENGAH': 'Kalimantan',
    'KALIMANTAN SELATAN': 'Kalimantan',
    'KALIMANTAN TIMUR': 'Kalimantan',
    'KALIMANTAN UTARA': 'Kalimantan',
    
    # Sulawesi
    'SULAWESI UTARA': 'Sulawesi',
    'SULAWESI TENGAH': 'Sulawesi',
    'SULAWESI SELATAN': 'Sulawesi',
    'SULAWESI TENGGARA': 'Sulawesi',
    'GORONTALO': 'Sulawesi',
    'SULAWESI BARAT': 'Sulawesi',
    
    # Maluku
    'MALUKU': 'Maluku',
    'MALUKU UTARA': 'Maluku',
    
    # Papua
    'PAPUA': 'Papua',
    'PAPUA BARAT': 'Papua',
    'PAPUA BARAT DAYA': 'Papua',
    'PAPUA SELATAN': 'Papua',
    'PAPUA TENGAH': 'Papua',
    'PAPUA PEGUNUNGAN': 'Papua',
}

# Region list
REGIONS = [
    'Sumatera',
    'Jawa',
    'Bali & Nusa Tenggara',
    'Kalimantan',
    'Sulawesi',
    'Maluku',
    'Papua'
]


# ============================================
# ANALYSIS CONSTANTS
# ============================================

# Top N defaults
DEFAULT_TOP_N = 10
MAX_TOP_N = 38

# Growth rate calculation
BASE_YEAR = 2020
COMPARISON_YEAR = 2023

# Outlier detection (IQR method)
IQR_MULTIPLIER = 1.5

# Consumption thresholds (GWh) for categorization
CONSUMPTION_THRESHOLDS = {
    'very_low': 1000,      # < 1,000 GWh
    'low': 5000,           # 1,000 - 5,000 GWh
    'medium': 15000,       # 5,000 - 15,000 GWh
    'high': 30000,         # 15,000 - 30,000 GWh
    'very_high': float('inf')  # > 30,000 GWh
}

CONSUMPTION_LABELS = {
    'very_low': 'Sangat Rendah',
    'low': 'Rendah',
    'medium': 'Sedang',
    'high': 'Tinggi',
    'very_high': 'Sangat Tinggi'
}


# ============================================
# VISUALIZATION SETTINGS
# ============================================

# Default figure size
DEFAULT_FIGURE_SIZE = (1000, 600)

# Color schemes (imported from themes, but can be overridden)
PRIMARY_COLOR = '#1f77b4'
SECONDARY_COLOR = '#ff7f0e'

# 🗺️ GEOJSON: Map settings
MAP_CENTER = {"lat": -2.5, "lon": 118}  # Indonesia center
MAP_ZOOM = 3.5
MAP_STYLE = "carto-positron"


# ============================================
# EXPORT SETTINGS
# ============================================

# Figure export format
EXPORT_FORMAT = 'png'
EXPORT_DPI = 300

# CSV export encoding
CSV_ENCODING = 'utf-8'


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_region(province: str) -> str:
    """
    Get region for a given province
    
    Parameters:
    -----------
    province : str
        Province name
    
    Returns:
    --------
    str : Region name
    """
    return REGION_MAPPING.get(province.upper(), 'Unknown')


def is_java_province(province: str) -> bool:
    """
    Check if province is in Java island
    
    Parameters:
    -----------
    province : str
        Province name
    
    Returns:
    --------
    bool : True if in Java
    """
    return get_region(province) == 'Jawa'


def categorize_consumption(value: float) -> str:
    """
    Categorize consumption value
    
    Parameters:
    -----------
    value : float
        Consumption in GWh
    
    Returns:
    --------
    str : Category label
    """
    if value < CONSUMPTION_THRESHOLDS['very_low']:
        return CONSUMPTION_LABELS['very_low']
    elif value < CONSUMPTION_THRESHOLDS['low']:
        return CONSUMPTION_LABELS['low']
    elif value < CONSUMPTION_THRESHOLDS['medium']:
        return CONSUMPTION_LABELS['medium']
    elif value < CONSUMPTION_THRESHOLDS['high']:
        return CONSUMPTION_LABELS['high']
    else:
        return CONSUMPTION_LABELS['very_high']


def ensure_directories():
    """Create all necessary directories if they don't exist"""
    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        INTERIM_DATA_DIR,
        PROCESSED_DATA_DIR,
        NOTEBOOKS_DIR,
        STREAMLIT_DIR,
        REPORTS_DIR,
        FIGURES_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ All directories created/verified")


# ============================================
# MODULE INFO
# ============================================

__version__ = '1.0.0'
__author__ = 'Electricity Visualization Team'


# Testing
if __name__ == "__main__":
    print("=== Configuration Module ===\n")
    
    print(f"📁 Project Root: {PROJECT_ROOT}")
    print(f"📊 Data Directory: {DATA_DIR}")
    print(f"🗺️  GeoJSON Path: {GEOJSON_PATH}")
    
    print(f"\n📅 Available Years: {AVAILABLE_YEARS}")
    print(f"🗺️  Total Provinces: {TOTAL_PROVINCES_BASE} (base) / {TOTAL_PROVINCES_FULL} (with pemekaran)")
    
    print(f"\n🌏 Regions: {len(REGIONS)}")
    for region in REGIONS:
        count = sum(1 for r in REGION_MAPPING.values() if r == region)
        print(f"   • {region}: {count} provinces")
    
    print(f"\n🔧 Utility Functions:")
    print(f"   • get_region('JAWA BARAT'): {get_region('JAWA BARAT')}")
    print(f"   • is_java_province('DKI JAKARTA'): {is_java_province('DKI JAKARTA')}")
    print(f"   • categorize_consumption(25000): {categorize_consumption(25000)}")
    
    print("\n✅ Config module ready!")