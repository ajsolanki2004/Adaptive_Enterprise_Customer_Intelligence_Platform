import streamlit as st

def render_kpi_cards(data):
    cols = st.columns(5)
    with cols[0]:
        st.metric(label="👥 Total Customers", value=f"{data['total_customers']:,}", delta=f"{data['total_customers_trend']}%", delta_color="normal")
    with cols[1]:
        st.metric(label="💰 Revenue Contribution", value=data['revenue'], delta=f"{data['revenue_trend']}%", delta_color="normal")
    with cols[2]:
        st.metric(label="⚠️ Customers at Risk", value=f"{data['at_risk']:,}", delta=f"{data['at_risk_trend']}%", delta_color="inverse")
    with cols[3]:
        st.metric(label="📈 Growth Trend", value=f"+{data['growth']}%", delta=f"{data['growth_trend']}%", delta_color="normal")
    with cols[4]:
        st.metric(label="⭐ High-Value", value=f"{data['high_value']:,}", delta=f"{data['high_value_trend']}%", delta_color="normal")
