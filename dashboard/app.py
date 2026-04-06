import sys
import os
import pickle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from dashboard.components.kpi_cards import render_kpi_cards
from dashboard.components.charts import render_donut_chart, render_line_chart, render_bar_chart, render_risk_gauge
from dashboard.components.actions import render_action_cards
from dashboard.components.csv_analyzer import render_csv_analyzer
from dashboard.utils.data_loader import load_kpi_data, load_customer_segments, load_activity_trend, load_customer_lookup

_PRECOMPUTED = os.path.join(os.path.dirname(__file__), "precomputed_results.pkl")

# Page Configuration
st.set_page_config(layout="wide", page_title="AECIP Executive Dashboard")

# Custom CSS for Typography and Design System
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"]  {
   font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0E1117;
    color: #F8FAFC;
}

h1, h2, h3 { 
    color: #F8FAFC; 
}

/* Style the KPI cards as dark boards */
[data-testid="stMetric"] {
    background-color: #1E293B;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
[data-testid="stMetricLabel"] {
    color: #9CA3AF !important;
    font-weight: 500;
}
[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-weight: 600;
}

/* Sidebar Navigation using Buttons */
[data-testid="stSidebar"] {
    background-color: #0D0F1A; /* Deep navy-black, close to reference image */
}

/* Secondary Button (Inactive Menu Item) */
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background-color: transparent !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    box-shadow: none !important;
    color: #9CA3AF !important;
    padding: 10px 16px !important;
    border-radius: 0 !important;
    justify-content: flex-start !important;
    transition: all 0.2s;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    background-color: rgba(255, 255, 255, 0.06) !important;
    color: #FFFFFF !important;
    border-left: 3px solid rgba(255,255,255,0.4) !important;
}

/* Primary Button (Active Menu Item) */
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background-color: transparent !important;
    border: none !important;
    border-left: 3px solid #FFFFFF !important;
    box-shadow: none !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    padding: 10px 16px !important;
    border-radius: 0 !important;
    justify-content: flex-start !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {
    background-color: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
}

/* Align button text and icons */
[data-testid="stSidebar"] [data-testid^="stBaseButton"] div {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 10px !important;
    width: 100% !important;
}
[data-testid="stSidebar"] [data-testid^="stBaseButton"] div p {
    margin: 0 !important;
    text-align: left !important;
    font-size: 15px !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] span {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] span {
    color: #9CA3AF !important;
}

.insight-box {
    background-color: #FEF3C7;
    border-left: 4px solid #F59E0B;
    padding: 1rem;
    border-radius: 4px;
    margin-top: 1rem;
    margin-bottom: 1rem;
    color: #92400E;
}

.insight-box-blue {
    background-color: #E0F2FE;
    border-left: 4px solid #3B82F6;
    padding: 1rem;
    border-radius: 4px;
    margin-top: 1rem;
    margin-bottom: 1rem;
    color: #1E3A8A;
}
</style>
""", unsafe_allow_html=True)

# ── Auto-load pre-computed results (from run_analysis.py) ────────────────────
if not st.session_state.get('data_processed', False) and os.path.exists(_PRECOMPUTED):
    with open(_PRECOMPUTED, "rb") as _f:
        _preloaded = pickle.load(_f)
    st.session_state.results       = _preloaded
    st.session_state.data_processed = True
    st.session_state.page          = "overview"
    os.remove(_PRECOMPUTED)   # consume the file so it doesn't re-inject on reset
    st.rerun()

# Application Flow
if not st.session_state.get('data_processed', False):
    # Hide sidebar when on Input Dashboard
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
    st.title("AECIP Platform Initialization")
    render_csv_analyzer()
else:
    st.title("AECIP Executive Dashboard")
    
    # Sidebar Navigation for Output Dashboard
    pages = [
        ("Overview", ":material/home:", "overview"),
        ("Customer Groups", ":material/group:", "groups"),
        ("Risk & Customer Loss", ":material/warning:", "risk"),
        ("Recommended Actions", ":material/shopping_cart:", "actions"),
        ("Customer Lookup", ":material/search:", "lookup"),
    ]
    
    if 'page' not in st.session_state:
        st.session_state.page = "overview"
    
    st.sidebar.markdown("""
    <div style='padding: 10px 0 20px 0;'>
        <h1 style='color: #FFFFFF; font-family: "Inter", "Segoe UI", sans-serif; font-weight: 600; font-size: 20px; letter-spacing: 0.3px; margin: 0;'>Customer Intelligence</h1>
        <hr style='margin-top: 14px; margin-bottom: 5px; border: 0; border-top: 1px solid rgba(255,255,255,0.2);'>
    </div>
    """, unsafe_allow_html=True)
    
    for label, icon, page_key in pages:
        button_type = "primary" if st.session_state.page == page_key else "secondary"
        try:
            if st.sidebar.button(label, icon=icon, use_container_width=True, type=button_type):
                st.session_state.page = page_key
                st.rerun()
        except TypeError:
            if st.sidebar.button(f"{icon} {label}", use_container_width=True, type=button_type):
                 st.session_state.page = page_key
                 st.rerun()
                 
    # Reset button
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Reset / Upload New Data", use_container_width=True, type="secondary"):
        st.session_state.data_processed = False
        st.session_state.results = None
        st.rerun()
    
    page = st.session_state.page
    results = st.session_state.get('results', {})
    
    if page == "overview":
        st.header("What is happening right now?")
        
        kpi_data = load_kpi_data(results)
        render_kpi_cards(kpi_data)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Customer Distribution")
            segments_df = load_customer_segments(results)
            render_donut_chart(segments_df)
        with col2:
            st.subheader("Activity Trend")
            trend_df = load_activity_trend(results)
            render_line_chart(trend_df)
            
        st.markdown("""
        <div class="insight-box">
            ⚠️ <strong>Insight:</strong> This data relies purely on the file you just uploaded! Ensure data is recent for the best recommendations.
        </div>
        """, unsafe_allow_html=True)
    
    elif page == "groups":
        st.header("Who are my customers?")
        
        col1, col2, col3, col4 = st.columns(4)
        segments_info = [
            {"name": "High Value", "icon": "⭐", "desc": "Top spenders & frequent buyers"},
            {"name": "Regular", "icon": "🔁", "desc": "Consistent purchasers"},
            {"name": "Inactive", "icon": "😴", "desc": "Haven't interacted recently"},
            {"name": "At Risk", "icon": "⚠️", "desc": "High customer loss probability"}
        ]
        
        for i, col in enumerate([col1, col2, col3, col4]):
            info = segments_info[i]
            with col:
                st.markdown(f"### {info['icon']} {info['name']}")
                st.caption(info['desc'])
                
        st.markdown("---")
        st.subheader("Group Sizes Based on Uploaded File")
        segments_df = load_customer_segments(results)
        render_bar_chart(segments_df)
    
    elif page == "risk":
        st.header("Who is about to leave?")
        kpi_data = load_kpi_data(results)
        at_risk_count = kpi_data.get('at_risk', 0)
        total = kpi_data.get('total_customers', 1)
        risk_pct = int((at_risk_count / total) * 100) if total > 0 else 0
        
        col1, col2 = st.columns([1, 1])
        with col1:
            render_risk_gauge(risk_pct)
        with col2:
            st.subheader("Risk Statistics")
            st.metric("Total At-Risk Customers", f"{at_risk_count:,}")

            if at_risk_count == 0:
                st.markdown("""
                <div style="background-color:#052e16; border-left: 4px solid #22c55e; padding: 1rem; border-radius: 6px; margin-top: 0.8rem;">
                    ✅ <strong style="color:#4ade80;">Your customer base looks healthy!</strong><br>
                    <span style="color:#86efac;">No at-risk customers were detected. Your customers are buying regularly, engaging frequently, and spending consistently. Keep it up!</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("**⚠️ Top warning signs found in your customer data:**")
                st.markdown("1. 🛒 **Customers are buying less often** — their purchase count has dropped significantly compared to before")
                st.markdown("2. 📅 **Customers haven't shopped in a long time** — the gap since their last purchase is getting longer")
                st.markdown("3. 💸 **Customers are spending less money** — their total spend per visit has been declining over time")

        if at_risk_count == 0:
            st.markdown("""
            <div class="insight-box" style="background-color:#052e16; border-left: 4px solid #22c55e; color:#86efac;">
                💡 <strong>Insight:</strong> Great news — all your customers are currently active and engaged. Continue monitoring to catch any early warning signs.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box-blue">
                💡 <strong>Insight:</strong> Customers classified as "At Risk" have a ~75% chance of customer loss within the next month without intervention.
            </div>
            """, unsafe_allow_html=True)
    
    elif page == "actions":
        st.header("What should I do?")
        render_action_cards()
    
    elif page == "lookup":
        st.header("Tell me about a specific customer")
        default_id = 1
        if results and results.get('combined') is not None and not results.get('combined').empty and 'customer_id' in results.get('combined').columns:
            default_id = int(results.get('combined')['customer_id'].iloc[0])
            
        customer_id = st.number_input("Enter Customer ID", min_value=1, value=default_id, step=1)
        
        if st.button("Search"):
            data = load_customer_lookup(customer_id, results)
            st.markdown("### Profile")
            for k, v in data.items():
                st.markdown(f"**{k}:** {v}")
