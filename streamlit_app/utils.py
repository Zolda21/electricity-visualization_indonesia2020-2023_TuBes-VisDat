"""
Streamlit Utilities
Shared helper functions untuk semua pages
"""

import streamlit as st
from pathlib import Path


def load_css():
    """
    Load custom CSS from assets folder
    Call this at the top of each page for consistent styling
    """
    # Get path relative to this file
    css_file = Path(__file__).parent / "assets" / "style.css"
    
    if css_file.exists():
        with open(css_file, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ CSS file not found at: {css_file}")


def set_page_config(title: str, icon: str = "⚡", layout: str = "wide"):
    """
    Standard page configuration
    
    Parameters:
    -----------
    title : str
        Page title
    icon : str
        Page icon (emoji)
    layout : str
        'wide' or 'centered'
    """
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout=layout,
        initial_sidebar_state="expanded"
    )


def add_footer():
    """Add standard footer to page"""
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>© 2025 Universitas Muhammadiyah Bandung</p>
        <p>Electricity Visualization Dashboard</p>
    </div>
    """, unsafe_allow_html=True)


# Example usage
if __name__ == "__main__":
    set_page_config("Test Page", "🧪")
    load_css()
    
    st.title("Utilities Test")
    st.success("✅ CSS and utilities loaded successfully!")
    
    add_footer()