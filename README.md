# ⚡ Dashboard Konsumsi Listrik Indonesia

Visualisasi interaktif dinamika konsumsi listrik 38 provinsi Indonesia periode 2020-2023

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📖 Tentang Proyek

Dashboard ini menyajikan analisis komprehensif tentang distribusi dan pola konsumsi listrik di 38 provinsi Indonesia selama periode 2020-2023. Data bersumber dari **Badan Pusat Statistik (BPS)** dan divisualisasikan menggunakan Streamlit untuk memberikan insights interaktif.

### 🎯 Fitur Utama

- **📊 Overview Dashboard**: KPI panel, ringkasan nasional, ranking provinsi
- **🗺️ Province Analytics**: Analisis geografis dengan choropleth maps interaktif
- **📈 Yearly Trends**: Tren multi-tahun, growth analysis, CAGR calculation
- **📋 Data Explorer**: Interactive table dengan advanced filtering
- **🔍 Interactive Filters**: Filter real-time berdasarkan tahun, provinsi, region
- **💾 Export Capabilities**: Download data dan visualisasi

## 🚀 Quick Start

### Prerequisites

- Python 3.9 atau lebih tinggi
- pip (Python package manager)

### Instalasi

1. **Clone repository**
```bash
git clone https://github.com/yourusername/electricity-visualization.git
cd electricity-visualization
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Jalankan Streamlit dashboard**
```bash
streamlit run streamlit_app/app.py
```

4. **Buka browser** di `http://localhost:8501`

## 📁 Struktur Proyek

```
electricity-visualization/
│
├── data/
│   ├── raw/                    # Data CSV mentah (2020-2023)
│   │   ├── electricity_2020.csv
│   │   ├── electricity_2021.csv
│   │   ├── electricity_2022.csv
│   │   ├── electricity_2023.csv
│   │   └── indonesia_provinces.geojson  🗺️
│   ├── interim/                # Data hasil load
│   └── processed/              # Data clean siap analisis
│
├── notebooks/
│   ├── 01_preprocessing.ipynb         # Data cleaning & preprocessing
│   ├── 02_eda.ipynb                   # Exploratory Data Analysis
│   ├── 03_visual_design.ipynb         # Visual testing
│   └── 04_geospatial_analysis.ipynb   # 🗺️ Geospatial analysis
│
├── src/
│   ├── data/
│   │   ├── load.py            # Load CSV files
│   │   ├── clean.py           # Data cleaning
│   │   ├── transform.py       # Feature engineering
│   │   └── geo_processing.py  # 🗺️ GeoJSON processing
│   │
│   ├── eda/
│   │   ├── explorations.py    # EDA functions
│   │   └── statistics.py      # Statistical analysis
│   │
│   ├── viz/
│   │   ├── themes.py          # Color schemes & styling
│   │   ├── charts.py          # Chart functions (bar, line, heatmap)
│   │   └── maps.py            # 🗺️ Map visualizations
│   │
│   └── utils/
│       ├── config.py          # Configuration & constants
│       ├── helpers.py         # Utility functions
│       └── province_mapping.py # 🗺️ CSV to GeoJSON mapping
│
├── streamlit_app/
│   ├── app.py                 # Main landing page
│   └── pages/
│       ├── 01_📊_overview.py
│       ├── 02_🗺️_province_analytics.py  🗺️
│       ├── 03_📈_yearly_trends.py
│       └── 04_📋_data_explorer.py
│
├── scripts/                   # Testing & debugging scripts
├── reports/                   # Generated reports & figures
├── requirements.txt
└── README.md
```

## 📊 Dataset

**Sumber**: Badan Pusat Statistik (BPS)  
**Periode**: 2020-2023 (4 tahun)  
**Cakupan**: 38 Provinsi Indonesia  
**Satuan**: GigaWatt-hour (GWh)  

### Data Schema

| Column | Description |
|--------|-------------|
| Province | Nama provinsi |
| Year | Tahun (2020-2023) |
| Electricity_GWh | Konsumsi listrik dalam GWh |

## 🗺️ Geospatial Analysis

Dashboard ini menggunakan **GeoJSON** untuk visualisasi peta Indonesia:

- **Choropleth Maps**: Peta tematik konsumsi per provinsi
- **Growth Rate Maps**: Visualisasi pertumbuhan dengan diverging colors
- **Comparison Maps**: Side-by-side comparison antar tahun
- **Interactive Features**: Zoom, pan, hover tooltips

## 🛠️ Teknologi

- **Python 3.9+**: Backend processing
- **Streamlit 1.28+**: Dashboard framework
- **Pandas**: Data manipulation
- **GeoPandas**: Geospatial data processing 🗺️
- **Plotly**: Interactive visualizations
- **Folium**: Map rendering 🗺️

## 📈 Visualisasi yang Tersedia

### Charts
- ✅ Horizontal Bar Chart (ranking)
- ✅ Line Chart (trends)
- ✅ Heatmap (multi-year comparison)
- ✅ Histogram (distribution)
- ✅ Boxplot (outlier detection)
- ✅ Area Chart (regional composition)

### Maps 🗺️
- ✅ Choropleth Map (consumption by province)
- ✅ Growth Rate Map (CAGR visualization)
- ✅ Comparison Map (temporal comparison)

## 🎓 Tim Pengembang

**Kelompok Visualisasi Data - Teknik Informatika UMB**

- Agung Nur Hakim Somantri (220102008)
- Arkaan Zachary Hermawan (220102018)
- Muhamad Hilman Nur Hakim (220102050)
- Marshal Yanda Saputra (220102044)

**Dosen Pembimbing**: Taufik Rahmat Kurniawan, S.kom.,M.T.

## 📝 Usage Examples

### Run Preprocessing
```bash
jupyter notebook notebooks/01_preprocessing.ipynb
```

### Run EDA
```bash
jupyter notebook notebooks/02_eda.ipynb
```

### Launch Dashboard
```bash
streamlit run streamlit_app/app.py
```

## 📌 Key Insights
➡️ Detailed analysis: [Insights Report](reports/insights.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Badan Pusat Statistik (BPS) untuk data
- Universitas Muhammadiyah Bandung
- BAKOSURTANAL untuk data GeoJSON 🗺️

## 📞 Contact

Untuk pertanyaan dan feedback, silakan hubungi:
- Email: [your-email@example.com]
- GitHub: [github.com/yourusername]

---

**© 2025 Universitas Muhammadiyah Bandung**

*Dashboard ini dibuat sebagai bagian dari Tugas Mata Kuliah Visualisasi Data*