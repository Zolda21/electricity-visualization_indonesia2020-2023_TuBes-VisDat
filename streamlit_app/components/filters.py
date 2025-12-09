"""
Reusable Filter Components
Common filter widgets untuk sidebar
"""

import streamlit as st
from typing import List, Tuple


def year_filter(years: List[int], default_index: int = -1) -> int:
    """
    Single year selector
    
    Parameters:
    -----------
    years : list
        Available years
    default_index : int
        Default selection index
    
    Returns:
    --------
    int : Selected year
    """
    return st.sidebar.selectbox(
        "📅 Select Year",
        options=years,
        index=default_index
    )


def year_range_filter(years: List[int]) -> Tuple[int, int]:
    """
    Year range selector (from-to)
    
    Parameters:
    -----------
    years : list
        Available years
    
    Returns:
    --------
    tuple : (start_year, end_year)
    """
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        start_year = st.selectbox("From", years, index=0)
    with col2:
        end_year = st.selectbox("To", years, index=len(years)-1)
    
    return start_year, end_year


def year_slider(years: List[int], default: int = None) -> int:
    """
    Year slider selector
    
    Parameters:
    -----------
    years : list
        Available years
    default : int
        Default year
    
    Returns:
    --------
    int : Selected year
    """
    if default is None:
        default = years[-1]
    
    return st.sidebar.select_slider(
        "📅 Select Year",
        options=years,
        value=default
    )


def region_filter(regions: List[str], allow_all: bool = True) -> List[str]:
    """
    Region multi-selector
    
    Parameters:
    -----------
    regions : list
        Available regions
    allow_all : bool
        Show "All Regions" checkbox
    
    Returns:
    --------
    list : Selected regions
    """
    st.sidebar.markdown("### 🌏 Filter by Region")
    
    if allow_all:
        all_regions = st.sidebar.checkbox("All Regions", value=True)
        
        if all_regions:
            return regions
    
    selected = st.sidebar.multiselect(
        "Choose Region(s)",
        options=regions,
        default=regions[:2] if not allow_all else regions
    )
    
    return selected


def province_filter(provinces: List[str], 
                   filter_type: str = "multiselect") -> List[str]:
    """
    Province filter with multiple modes
    
    Parameters:
    -----------
    provinces : list
        Available provinces
    filter_type : str
        "multiselect", "search", or "top_n"
    
    Returns:
    --------
    list : Selected provinces
    """
    st.sidebar.markdown("### 🗺️ Filter by Province")
    
    if filter_type == "multiselect":
        selected = st.sidebar.multiselect(
            "Choose Province(s)",
            options=sorted(provinces),
            default=list(sorted(provinces)[:5])
        )
        return selected
    
    elif filter_type == "search":
        search_term = st.sidebar.text_input("🔍 Search Province")
        if search_term:
            return [p for p in provinces if search_term.upper() in p.upper()]
        return provinces
    
    elif filter_type == "top_n":
        n = st.sidebar.slider("Number of Provinces", 3, 20, 10)
        # Note: Requires dataframe to sort by consumption
        return provinces[:n]
    
    return provinces


def top_n_slider(min_val: int = 3, 
                max_val: int = 20, 
                default: int = 10) -> int:
    """
    Top N slider
    
    Parameters:
    -----------
    min_val : int
        Minimum value
    max_val : int
        Maximum value
    default : int
        Default value
    
    Returns:
    --------
    int : Selected N
    """
    return st.sidebar.slider(
        "Top N Provinces",
        min_value=min_val,
        max_value=max_val,
        value=default,
        step=1
    )


def value_range_filter(min_val: float, 
                      max_val: float,
                      label: str = "Value Range") -> Tuple[float, float]:
    """
    Range slider for numeric values
    
    Parameters:
    -----------
    min_val : float
        Minimum value
    max_val : float
        Maximum value
    label : str
        Slider label
    
    Returns:
    --------
    tuple : (min_selected, max_selected)
    """
    return st.sidebar.slider(
        label,
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val)
    )


def apply_reset_buttons():
    """
    Standard Apply & Reset buttons
    
    Returns:
    --------
    tuple : (apply_clicked, reset_clicked)
    """
    st.sidebar.markdown("---")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        apply = st.button("🔍 Apply", type="primary", use_container_width=True)
    
    with col2:
        reset = st.button("🔄 Reset", use_container_width=True)
    
    return apply, reset


# Example usage
if __name__ == "__main__":
    st.sidebar.header("🎛️ Filters")
    
    # Year filter
    selected_year = year_filter([2020, 2021, 2022, 2023])
    st.write(f"Selected year: {selected_year}")
    
    # Region filter
    regions = ["Jawa", "Sumatera", "Kalimantan"]
    selected_regions = region_filter(regions)
    st.write(f"Selected regions: {selected_regions}")
    
    # Apply/Reset
    apply, reset = apply_reset_buttons()
    if apply:
        st.success("Filters applied!")
    if reset:
        st.info("Filters reset!")