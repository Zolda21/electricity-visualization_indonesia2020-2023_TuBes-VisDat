"""
Reusable Metric Components
KPI cards and metric displays
"""

import streamlit as st
from typing import Optional


def kpi_metric(label: str, 
              value: str, 
              delta: Optional[str] = None,
              delta_color: str = "normal"):
    """
    Standard KPI metric card
    
    Parameters:
    -----------
    label : str
        Metric label
    value : str
        Metric value (formatted)
    delta : str, optional
        Delta value (e.g., "+5.2%")
    delta_color : str
        "normal", "inverse", or "off"
    """
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color
    )


def colored_metric_card(label: str,
                       value: str,
                       subtitle: str = "",
                       color: str = "blue"):
    """
    Colored metric card with gradient
    
    Parameters:
    -----------
    label : str
        Card title
    value : str
        Main value
    subtitle : str
        Subtitle text
    color : str
        Color theme: "blue", "green", "red", "purple"
    """
    color_gradients = {
        "blue": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "green": "linear-gradient(135deg, #56ab2f 0%, #a8e063 100%)",
        "red": "linear-gradient(135deg, #eb3349 0%, #f45c43 100%)",
        "purple": "linear-gradient(135deg, #8e2de2 0%, #4a00e0 100%)",
    }
    
    gradient = color_gradients.get(color, color_gradients["blue"])
    
    st.markdown(f"""
    <div style="
        background: {gradient};
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    ">
        <h3 style="color: white; margin: 0; font-size: 0.9rem;">{label}</h3>
        <h2 style="color: white; margin: 10px 0; font-size: 2rem;">{value}</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def kpi_row(metrics: list):
    """
    Row of KPI metrics
    
    Parameters:
    -----------
    metrics : list of dict
        List of metrics, each dict has: {label, value, delta}
    
    Example:
    --------
    kpi_row([
        {"label": "Total", "value": "1000 GWh", "delta": "+5%"},
        {"label": "Average", "value": "50 GWh"}
    ])
    """
    cols = st.columns(len(metrics))
    
    for col, metric in zip(cols, metrics):
        with col:
            st.metric(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                delta=metric.get("delta")
            )


def stat_box(title: str, 
            value: str,
            icon: str = "📊"):
    """
    Simple stat box with icon
    
    Parameters:
    -----------
    title : str
        Stat title
    value : str
        Stat value
    icon : str
        Emoji icon
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    ">
        <div style="font-size: 2rem;">{icon}</div>
        <h3 style="color: white; margin: 10px 0;">{title}</h3>
        <h2 style="color: white; font-size: 2rem;">{value}</h2>
    </div>
    """, unsafe_allow_html=True)


def comparison_metrics(metric1: dict, 
                      metric2: dict,
                      comparison_label: str = "Change"):
    """
    Side-by-side comparison metrics
    
    Parameters:
    -----------
    metric1 : dict
        First metric {label, value}
    metric2 : dict
        Second metric {label, value}
    comparison_label : str
        Label for comparison
    
    Example:
    --------
    comparison_metrics(
        {"label": "2020", "value": 1000},
        {"label": "2023", "value": 1200},
        "Growth"
    )
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=metric1["label"],
            value=f"{metric1['value']:,.0f}" if isinstance(metric1['value'], (int, float)) else metric1['value']
        )
    
    with col2:
        st.metric(
            label=metric2["label"],
            value=f"{metric2['value']:,.0f}" if isinstance(metric2['value'], (int, float)) else metric2['value']
        )
    
    with col3:
        # Calculate difference
        if isinstance(metric1['value'], (int, float)) and isinstance(metric2['value'], (int, float)):
            diff = metric2['value'] - metric1['value']
            pct = (diff / metric1['value']) * 100 if metric1['value'] != 0 else 0
            
            st.metric(
                label=comparison_label,
                value=f"{diff:+,.0f}",
                delta=f"{pct:+.1f}%"
            )


def trend_indicator(value: float, 
                   threshold: float = 0,
                   label: str = ""):
    """
    Show trend indicator (up/down/neutral)
    
    Parameters:
    -----------
    value : float
        Value to check
    threshold : float
        Threshold for neutral
    label : str
        Optional label
    """
    if value > threshold:
        color = "green"
        icon = "📈"
        trend = "Increasing"
    elif value < -threshold:
        color = "red"
        icon = "📉"
        trend = "Decreasing"
    else:
        color = "gray"
        icon = "➡️"
        trend = "Stable"
    
    st.markdown(f"""
    <div style="color: {color}; font-weight: bold;">
        {icon} {label} {trend}: {value:+.2f}%
    </div>
    """, unsafe_allow_html=True)


def info_card(title: str, 
             content: str,
             card_type: str = "info"):
    """
    Colored info card
    
    Parameters:
    -----------
    title : str
        Card title
    content : str
        Card content
    card_type : str
        "info", "success", "warning", "error"
    """
    colors = {
        "info": {"bg": "#e3f2fd", "border": "#1f77b4"},
        "success": {"bg": "#d4edda", "border": "#28a745"},
        "warning": {"bg": "#fff3cd", "border": "#ffc107"},
        "error": {"bg": "#f8d7da", "border": "#dc3545"},
    }
    
    style = colors.get(card_type, colors["info"])
    
    st.markdown(f"""
    <div style="
        background-color: {style['bg']};
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {style['border']};
        margin: 1rem 0;
    ">
        <h4 style="margin: 0 0 0.5rem 0;">{title}</h4>
        <p style="margin: 0;">{content}</p>
    </div>
    """, unsafe_allow_html=True)


# Example usage
if __name__ == "__main__":
    st.title("Metric Components Demo")
    
    # Standard metrics
    st.subheader("1. Standard KPI Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_metric("Total", "1,000 GWh", "+5.2%")
    with col2:
        kpi_metric("Average", "50 GWh", "-2.1%", "inverse")
    with col3:
        kpi_metric("Provinces", "38")
    
    # Colored cards
    st.subheader("2. Colored Metric Cards")
    col1, col2 = st.columns(2)
    with col1:
        colored_metric_card("Revenue", "$1.2M", "Last 30 days", "green")
    with col2:
        colored_metric_card("Users", "5,432", "Active now", "blue")
    
    # Stat boxes
    st.subheader("3. Stat Boxes")
    col1, col2, col3 = st.columns(3)
    with col1:
        stat_box("Total Sales", "1,234", "💰")
    with col2:
        stat_box("New Users", "567", "👥")
    with col3:
        stat_box("Growth Rate", "+12%", "📈")
    
    # Comparison
    st.subheader("4. Comparison Metrics")
    comparison_metrics(
        {"label": "2020", "value": 1000},
        {"label": "2023", "value": 1200},
        "Growth"
    )
    
    # Trend indicator
    st.subheader("5. Trend Indicators")
    trend_indicator(15.5, 5, "Sales Growth")
    trend_indicator(-3.2, 5, "Costs")
    trend_indicator(1.5, 5, "Margin")
    
    # Info cards
    st.subheader("6. Info Cards")
    info_card("Information", "This is an info card", "info")
    info_card("Success", "Operation completed!", "success")
    info_card("Warning", "Please review this", "warning")