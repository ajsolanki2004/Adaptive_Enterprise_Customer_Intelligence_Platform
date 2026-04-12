import streamlit as st

def render_kpi_cards(data):
    cols = st.columns(5)
    with cols[0]:
        st.metric(
            label="👥 Total Customers", 
            value=f"{data['total_customers']:,}", 
            delta=f"{data['total_customers_trend']}%", 
            delta_color="normal",
            help="Total number of unique customers identified in the dataset. Percentage shows growth since last period."
        )
    with cols[1]:
        st.metric(
            label="💰 Revenue Contribution", 
            value=data['revenue'], 
            delta=f"{data['revenue_trend']}%", 
            delta_color="normal",
            help="Total monetary value of the customer base. The percentage indicates growth compared to the previous period."
        )
    with cols[2]:
        st.metric(
            label="⚠️ Customers at Risk", 
            value=f"{data['at_risk']:,}", 
            delta=f"{data['at_risk_trend']}%", 
            delta_color="inverse",
            help="Number of customers flagged with high churn risk. Negative trend (red) indicates improving retention."
        )
    with cols[3]:
        st.metric(
            label="📈 Growth Trend", 
            value=f"+{data['growth']}%", 
            delta=f"{data['growth_trend']}%", 
            delta_color="normal",
            help="Current overall growth rate of the business vs. previous period trend."
        )
    with cols[4]:
        st.metric(
            label="⭐ High-Value", 
            value=f"{data['high_value']:,}", 
            delta=f"{data['high_value_trend']}%", 
            delta_color="normal",
            help="Customers in the top tier of spend and frequency. Shows expansion of your most valuable segment."
        )
