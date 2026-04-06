import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dashboard.utils.helpers import get_color

def render_donut_chart(df):
    color_map = {
        'High Value': get_color('blue'),
        'Regular': get_color('green'),
        'Inactive': get_color('gray'),
        'At Risk': get_color('red')
    }
    fig = px.pie(df, values='Count', names='Segment', hole=0.6, color='Segment', color_discrete_map=color_map)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

def render_line_chart(df):
    fig = px.line(df, x='Month', y='Active Customers', markers=True)
    fig.update_traces(line_color=get_color('green'))
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

def render_bar_chart(df):
    color_map = {
        'High Value': get_color('blue'),
        'Regular': get_color('green'),
        'Inactive': get_color('gray'),
        'At Risk': get_color('red')
    }
    fig = px.bar(df, x='Count', y='Segment', color='Segment', orientation='h', color_discrete_map=color_map)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

def render_risk_gauge(risk_percentage):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_percentage,
        number = {'suffix': "%", 'font': {'color': '#F8FAFC', 'size': 48}},
        title = {'text': "Overall Portfolio Risk", 'font': {'color': '#F8FAFC', 'size': 16}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': '#9CA3AF', 'tickfont': {'color': '#F8FAFC'}},
            'bar': {'color': '#334155'},
            'steps' : [
                {'range': [0, 15], 'color': get_color('green')},
                {'range': [15, 30], 'color': get_color('amber')},
                {'range': [30, 100], 'color': get_color('red')}
            ]
        }
    ))
    fig.update_layout(
        margin=dict(t=60, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#F8FAFC'
    )
    st.plotly_chart(fig, use_container_width=True)
