"""
Province Name Mapping
Mapping nama provinsi dari CSV (BPS) ke GeoJSON (BAKOSURTANAL)
"""

# Mapping dictionary: CSV_name -> GeoJSON_name
PROVINCE_MAPPING = {
    # Sumatera
    'ACEH': 'DI.ACEH',
    'SUMATERA UTARA': 'SUMATERAUTARA',
    'SUMATERA BARAT': 'SUMATERABARAT',
    'RIAU': 'RIAU',
    'JAMBI': 'JAMBI',
    'SUMATERA SELATAN': 'SUMATERASELATAN',
    'BENGKULU': 'BENGKULU',
    'LAMPUNG': 'LAMPUNG',
    'KEP. BANGKA BELITUNG': 'BANGKABELITUNG',
    'KEP. RIAU': 'KEPULAUANRIAU',
    
    # Jawa
    'DKI JAKARTA': 'DKIJAKARTA',
    'JAWA BARAT': 'JAWABARAT',
    'JAWA TENGAH': 'JAWATENGAH',
    'DI YOGYAKARTA': 'DAERAHISTIMEWAYOGYAKARTA',
    'JAWA TIMUR': 'JAWATIMUR',
    'BANTEN': 'BANTEN',
    
    # Bali & Nusa Tenggara
    'BALI': 'BALI',
    'NUSA TENGGARA BARAT': 'NUSATENGGARABARAT',
    'NUSA TENGGARA TIMUR': 'NUSATENGGARATIMUR',
    
    # Kalimantan
    'KALIMANTAN BARAT': 'KALIMANTANBARAT',
    'KALIMANTAN TENGAH': 'KALIMANTANTENGAH',
    'KALIMANTAN SELATAN': 'KALIMANTANSELATAN',
    'KALIMANTAN TIMUR': 'KALIMANTANTIMUR',
    'KALIMANTAN UTARA': 'KALIMANTANUTARA',
    
    # Sulawesi
    'SULAWESI UTARA': 'SULAWESIUTARA',
    'SULAWESI TENGAH': 'SULAWESITENGAH',
    'SULAWESI SELATAN': 'SULAWESISELATAN',
    'SULAWESI TENGGARA': 'SULAWESITENGGARA',
    'GORONTALO': 'GORONTALO',
    'SULAWESI BARAT': 'SULAWESIBARAT',
    
    # Maluku
    'MALUKU': 'MALUKU',
    'MALUKU UTARA': 'MALUKUUTARA',
    
    # Papua (hanya yang ada di GeoJSON lama)
    'PAPUA BARAT': 'PAPUABARAT',
    'PAPUA': 'PAPUA',
}

# Provinsi baru hasil pemekaran (2022-2023) - BELUM ADA DI GEOJSON
PROVINSI_PEMEKARAN = [
    'PAPUA BARAT DAYA',
    'PAPUA SELATAN',
    'PAPUA TENGAH',
    'PAPUA PEGUNUNGAN'
]

# Reverse mapping (GeoJSON -> CSV)
GEOJSON_TO_CSV = {v: k for k, v in PROVINCE_MAPPING.items()}

# List provinsi yang valid untuk analisis (ada di GeoJSON)
VALID_PROVINCES = list(PROVINCE_MAPPING.keys())

def normalize_province_name(name: str, from_format: str = 'csv') -> str:
    """
    Normalize nama provinsi
    
    Parameters:
    -----------
    name : str
        Nama provinsi yang akan dinormalisasi
    from_format : str
        Format asal ('csv' atau 'geojson')
    
    Returns:
    --------
    str : Nama provinsi yang sudah dinormalisasi
    """
    # Clean whitespace
    name = name.strip().upper()
    
    if from_format == 'csv':
        # CSV -> standardized name
        return name
    elif from_format == 'geojson':
        # GeoJSON -> CSV format
        return GEOJSON_TO_CSV.get(name, name)
    
    return name

def get_geojson_name(csv_name: str) -> str:
    """
    Convert nama provinsi dari format CSV ke format GeoJSON
    
    Parameters:
    -----------
    csv_name : str
        Nama provinsi dalam format CSV (BPS)
    
    Returns:
    --------
    str : Nama provinsi dalam format GeoJSON, atau None jika tidak ditemukan
    """
    # Handle NaN, None, or non-string values
    if not isinstance(csv_name, str) or csv_name is None:
        return None
    
    csv_name = csv_name.strip().upper()
    return PROVINCE_MAPPING.get(csv_name, None)

def is_valid_province(name: str) -> bool:
    """
    Check apakah provinsi valid (ada di GeoJSON)
    
    Parameters:
    -----------
    name : str
        Nama provinsi yang akan dicek
    
    Returns:
    --------
    bool : True jika provinsi valid
    """
    name = name.strip().upper()
    return name in VALID_PROVINCES or name == 'INDONESIA'

def get_unmapped_provinces(province_list: list) -> list:
    """
    Get list provinsi yang belum ter-mapping
    
    Parameters:
    -----------
    province_list : list
        List nama provinsi yang akan dicek
    
    Returns:
    --------
    list : List provinsi yang belum ter-mapping
    """
    unmapped = []
    for prov in province_list:
        prov_clean = prov.strip().upper()
        if prov_clean not in VALID_PROVINCES and prov_clean != 'INDONESIA':
            unmapped.append(prov)
    return unmapped