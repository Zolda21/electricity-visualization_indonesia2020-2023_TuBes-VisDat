"""
Streamlit Dashboard - Main App
Visualisasi Dinamika Konsumsi Listrik Indonesia 2020-2023
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Page config
st.set_page_config(
    page_title="Electricity Dashboard Indonesia",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load global CSS
def load_css():
    """Load custom CSS from assets folder"""
    css_file = Path(__file__).parent / "assets" / "style.css"
    
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        # Fallback inline CSS if file not found
        st.markdown("""
            <style>
            .main-header {
                font-size: 3rem;
                font-weight: bold;
                color: #1f77b4;
                text-align: center;
                padding: 2rem 0;
            }
            .sub-header {
                font-size: 1.5rem;
                color: #555;
                text-align: center;
                padding-bottom: 2rem;
            }
            </style>
        """, unsafe_allow_html=True)

# Apply CSS
load_css()

# Main page
def main():
    # Header
    st.markdown('<h1 class="main-header">⚡ Dashboard Konsumsi Listrik Indonesia</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Visualisasi Dinamika 38 Provinsi Tahun 2020-2023</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Introduction
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📖 Tentang Dashboard
        
        Dashboard ini menyajikan analisis komprehensif tentang distribusi dan pola konsumsi listrik 
        di 38 provinsi Indonesia selama periode 2020-2023. Data bersumber dari **Badan Pusat Statistik (BPS)** 
        dan divisualisasikan untuk membantu pemahaman tren energi nasional.
        
        #### 🎯 Fitur Utama:
        - **Overview Dashboard**: Ringkasan konsumsi nasional, KPI, dan ranking provinsi
        - **Province Analytics**: Analisis detail per provinsi dengan peta interaktif
        - **Yearly Trends**: Tren multi-tahun, growth rate, dan perbandingan temporal
        - **Interactive Filters**: Filter berdasarkan tahun, provinsi, dan metrik
        
        #### 📊 Dataset:
        - **Periode**: 2020-2023 (4 tahun)
        - **Cakupan**: 38 Provinsi Indonesia (34 provinsi lama + 4 pemekaran Papua)
        - **Satuan**: GigaWatt-hour (GWh)
        - **Sumber**: BPS - Electricity Distributed by Province
        """)
    
    with col2:
        st.markdown("""
        <div class="info-box">
        <h4>ℹ️ Navigasi</h4>
        <p>Gunakan <b>sidebar</b> di sebelah kiri untuk mengakses halaman-halaman berikut:</p>
        <ul>
            <li>📊 <b>Overview</b></li>
            <li>🗺️ <b>Province Analytics</b></li>
            <li>📈 <b>Yearly Trends</b></li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("""
        **💡 Tips Penggunaan:**
        - Gunakan filter di sidebar untuk customize view
        - Hover pada grafik untuk detail data
        - Download grafik dengan klik tombol kamera
        - Gunakan zoom pada peta interaktif
        """)
    
    st.markdown("---")
    
    # Quick stats preview (placeholder - akan diisi dengan data real)
    st.markdown("### 📈 Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0;">🔌 Total Konsumsi 2023</h3>
            <h2 style="margin: 10px 0;">~270K GWh</h2>
            <p style="margin: 0;">Naik dari 241K (2020)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0;">🏆 Provinsi Tertinggi</h3>
            <h2 style="margin: 10px 0;">Jawa Barat</h2>
            <p style="margin: 0;">58,564 GWh (2023)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0;">📊 Growth Rate</h3>
            <h2 style="margin: 10px 0;">+12.0%</h2>
            <p style="margin: 0;">CAGR 2020-2023</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0;">🗺️ Cakupan</h3>
            <h2 style="margin: 10px 0;">38 Provinsi</h2>
            <p style="margin: 0;">Seluruh Indonesia</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    ### 👥 Tim Pengembang
    
    **Kelompok Visualisasi Data - Teknik Informatika UMB**
    - Agung Nur Hakim Somantri (220102008)
    - Arkaan Zachary Hermawan (220102018)
    - Muhamad Hilman Nur Hakim (220102050)
    - Marshal Yanda Saputra (220102044)
    
    **Dosen Pembimbing:** Taufik Rahmat Kurniawan, S.kom.,M.T.
    
    ---
    
    *Dashboard ini dibuat sebagai bagian dari tugas Mata Kuliah Visualisasi Data*  
    *© 2025 Universitas Muhammadiyah Bandung*
    """)

if __name__ == "__main__":
    main()