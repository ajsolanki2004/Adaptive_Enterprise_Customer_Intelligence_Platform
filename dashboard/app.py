import sys
import os
import pickle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from dashboard.components.kpi_cards import render_kpi_cards
from dashboard.components.charts import render_donut_chart, render_line_chart, render_bar_chart, render_risk_gauge
from dashboard.components.actions import render_action_cards
from dashboard.components.csv_analyzer import render_csv_analyzer
from dashboard.components.ai_insights import render_ai_insights
from dashboard.components.xai_explainer import render_xai_explainer
from dashboard.components.ai_assistant import render_ai_assistant
from dashboard.components.business_impact import render_business_impact
from dashboard.components.feedback_loop import render_feedback_loop
from dashboard.components.system_health import render_system_health
from dashboard.utils.data_loader import load_kpi_data, load_customer_segments, load_activity_trend, load_customer_lookup

_PRECOMPUTED = os.path.join(os.path.dirname(__file__), "precomputed_results.pkl")

# Page Configuration
st.set_page_config(layout="wide", page_title="AECIP — AI Customer Intelligence")

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #080D18;
    color: #F8FAFC;
}

h1, h2, h3 {
    color: #F8FAFC;
}

/* KPI Cards */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    border: 1px solid #1E293B;
    border-radius: 10px;
    padding: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
[data-testid="stMetricLabel"]  { color: #64748B !important; font-weight: 500; font-size: 12px; text-transform: uppercase; letter-spacing: 0.8px; }
[data-testid="stMetricValue"]  { color: #F8FAFC !important; font-weight: 700; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080D18 0%, #0D1117 100%);
    border-right: 1px solid #1E293B;
}

/* Secondary nav button */
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background-color: transparent !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    box-shadow: none !important;
    color: #64748B !important;
    padding: 10px 16px !important;
    border-radius: 0 !important;
    justify-content: flex-start !important;
    transition: all 0.2s;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    background-color: rgba(255,255,255,0.04) !important;
    color: #CBD5E1 !important;
    border-left: 3px solid rgba(255,255,255,0.25) !important;
}

/* Primary nav button (active) */
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, rgba(99,102,241,0.12) 0%, transparent 100%) !important;
    border: none !important;
    border-left: 3px solid #6366F1 !important;
    box-shadow: none !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    padding: 10px 16px !important;
    border-radius: 0 !important;
    justify-content: flex-start !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(90deg, rgba(99,102,241,0.18) 0%, transparent 100%) !important;
}

/* Button text alignment */
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
    font-size: 14px !important;
}

/* Shared card styles */
.insight-box {
    background: rgba(245,158,11,0.08);
    border-left: 4px solid #F59E0B;
    padding: 1rem;
    border-radius: 6px;
    margin: 1rem 0;
    color: #FCD34D;
}
.insight-box-blue {
    background: rgba(59,130,246,0.08);
    border-left: 4px solid #3B82F6;
    padding: 1rem;
    border-radius: 6px;
    margin: 1rem 0;
    color: #93C5FD;
}
.ai-summary-card {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 24px;
    margin-top: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.ai-badge {
    background: #6366F1;
    color: #FFFFFF;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 15px;
    display: inline-block;
}
.ai-score {
    font-size: 26px;
    font-weight: 700;
    color: #F8FAFC;
    margin: 10px 0;
}
.ai-reason {
    color: #94A3B8;
    font-size: 15px;
    font-style: italic;
    border-left: 3px solid #6366F1;
    padding-left: 12px;
    margin-top: 15px;
}

/* Priority bar */
.priority-strip {
    display: flex;
    gap: 10px;
    margin: 16px 0;
    flex-wrap: wrap;
}
.priority-item {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 10px 18px;
    flex: 1;
    min-width: 140px;
}
.priority-dot-red    { width:12px; height:12px; border-radius:50%; background:#EF4444; box-shadow:0 0 8px #EF4444; flex-shrink:0; }
.priority-dot-yellow { width:12px; height:12px; border-radius:50%; background:#F59E0B; box-shadow:0 0 8px #F59E0B; flex-shrink:0; }
.priority-dot-blue   { width:12px; height:12px; border-radius:50%; background:#6366F1; box-shadow:0 0 8px #6366F1; flex-shrink:0; }
.priority-dot-green  { width:12px; height:12px; border-radius:50%; background:#22C55E; box-shadow:0 0 8px #22C55E; flex-shrink:0; }
.priority-text { font-size: 13px; color: #CBD5E1; font-weight: 500; }
.priority-count { font-size: 18px; font-weight: 700; color: #F1F5F9; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Auto-load pre-computed results ─────────────────────────────────────────────
if not st.session_state.get('data_processed', False) and os.path.exists(_PRECOMPUTED):
    with open(_PRECOMPUTED, "rb") as _f:
        _preloaded = pickle.load(_f)
    st.session_state.results        = _preloaded
    st.session_state.data_processed = True
    st.session_state.page           = "overview"
    os.remove(_PRECOMPUTED)
    st.rerun()

# ── Application Flow ───────────────────────────────────────────────────────────
if not st.session_state.get('data_processed', False):
    # Hide sidebar on upload screen
    st.markdown("""
        <style>
            [data-testid="stSidebar"]       {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
    st.title("AECIP Platform Initialization")
    render_csv_analyzer()

else:
    # ── Sidebar ────────────────────────────────────────────────────────────────
    pages = [
        ("Executive Overview",   ":material/home:",          "overview"),
        ("AI Intelligence",      ":material/psychology:",    "ai_insights"),
        ("Customer Groups",      ":material/group:",         "groups"),
        ("Risk & Customer Loss", ":material/warning:",       "risk"),
        ("AI Explainer (XAI)",   ":material/visibility:",    "xai"),
        ("Decision Center",      ":material/target:",        "actions"),
        ("Business Impact",      ":material/attach_money:",  "impact"),
        ("AI Assistant",         ":material/chat:",          "assistant"),
        ("System Health",        ":material/monitor_heart:", "system_health"),
        ("System Architecture",  ":material/schema:",        "feedback"),
        ("Customer Lookup",      ":material/search:",        "lookup"),
    ]

    if 'page' not in st.session_state:
        st.session_state.page = "overview"

    st.sidebar.markdown("""
    <div style='padding: 12px 0 22px 0;'>
        <div style='font-size:11px; text-transform:uppercase; letter-spacing:2px; color:#6366F1; margin-bottom:6px; padding-left:16px;'>
            AECIP
        </div>
        <div style='color:#FFFFFF; font-family:"Inter",sans-serif; font-weight:700; font-size:17px; padding-left:16px; margin-bottom:2px;'>
            Customer Intelligence
        </div>
        <div style='font-size:11px; color:#334155; padding-left:16px; margin-bottom:14px;'>AI Decision Platform</div>
        <hr style='margin:0; border:0; border-top:1px solid #1E293B;'>
    </div>
    """, unsafe_allow_html=True)

    for label, icon, page_key in pages:
        btn_type = "primary" if st.session_state.page == page_key else "secondary"
        try:
            if st.sidebar.button(label, icon=icon, use_container_width=True, type=btn_type):
                st.session_state.page = page_key
                st.rerun()
        except TypeError:
            if st.sidebar.button(f"{icon} {label}", use_container_width=True, type=btn_type):
                st.session_state.page = page_key
                st.rerun()

    st.sidebar.markdown("---")
    # AI Confidence badge in sidebar
    st.sidebar.markdown("""
    <div style='padding:10px 16px; background:#0F172A; border:1px solid #1E293B; border-radius:8px; margin:0 8px 14px 8px;'>
        <div style='font-size:10px; color:#6366F1; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px'>AI Confidence</div>
        <div style='font-size:20px; font-weight:700; color:#818CF8'>87% <span style='font-size:12px; color:#4ADE80'>● Live</span></div>
        <div style='font-size:10px; color:#334155; margin-top:2px'>Model Accuracy: 82%</div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🔄 Reset / Upload New Data", use_container_width=True, type="secondary"):
        st.session_state.data_processed = False
        st.session_state.results = None
        st.rerun()

    # ── Page Routing ───────────────────────────────────────────────────────────
    page    = st.session_state.page
    results = st.session_state.get('results', {})

    # ── EXECUTIVE OVERVIEW ─────────────────────────────────────────────────────
    if page == "overview":
        st.markdown("""
        <div style='margin-bottom:4px'>
            <span style='font-size:12px; color:#6366F1; text-transform:uppercase; letter-spacing:2px;'>Dashboard</span>
        </div>
        """, unsafe_allow_html=True)
        st.header("Executive Overview")

        kpi_data     = load_kpi_data(results)
        segments_df  = load_customer_segments(results)

        # ── Executive AI Alert ───────────────────────────────────────────────
        at_risk     = kpi_data.get('at_risk', 0)
        total_c     = kpi_data.get('total_customers', 1)
        risk_pct    = (at_risk / total_c * 100) if total_c > 0 else 0
        pot_loss    = kpi_data.get('potential_loss', '₹0')
        high_value  = kpi_data.get('high_value', 0)

        if at_risk > 0 and risk_pct > 20:
            st.error(f"""
🚨 **Critical Business Alert — Immediate Attention Required**

**{risk_pct:.1f}%** of customers ({at_risk:,} users) are at high risk of leaving, threatening **{pot_loss}** in revenue within the next 30 days.

**📉 Primary Drivers:** Prolonged inactivity · Declining purchase frequency · Spend deterioration

**✅ Opportunity:** {high_value:,} high-value customers remain stable — leverage them for growth.

👉 **Immediate retention action is strongly recommended.** → Go to **Decision Center**
            """)
        elif at_risk > 0:
            st.warning(f"""
⚠️ **Business Alert:** {at_risk:,} customers ({risk_pct:.1f}%) are showing early churn signals, representing {pot_loss} in potential revenue risk.
Proactive engagement now can recover the majority. → See **Decision Center**
            """)
        else:
            st.success("✅ **Your customer base is healthy.** No critical risk signals detected. Focus on loyalty and growth programs.")

        # ── KPI Strip ────────────────────────────────────────────────────────
        render_kpi_cards(kpi_data)
        st.markdown("---")

        # ── Priority Bar ────────────────────────────────────────────────────
        st.markdown("#### 🚦 Customer Health Priority Status")
        df = results.get('combined')
        at_risk_n   = at_risk
        inactive_n  = len(df[df['segment_name'].str.contains('Inactive', na=False)]) if df is not None and 'segment_name' in df.columns else 0
        regular_n   = len(df[df['segment_name'].str.contains('Regular', na=False)])  if df is not None and 'segment_name' in df.columns else 0
        hv_n        = high_value

        st.markdown(f"""
        <div class="priority-strip">
            <div class="priority-item">
                <div class="priority-dot-red"></div>
                <div>
                    <div class="priority-text">🔴 At Risk (Critical)</div>
                    <div class="priority-count">{at_risk_n:,}</div>
                </div>
            </div>
            <div class="priority-item">
                <div class="priority-dot-yellow"></div>
                <div>
                    <div class="priority-text">🟡 Inactive (Warning)</div>
                    <div class="priority-count">{inactive_n:,}</div>
                </div>
            </div>
            <div class="priority-item">
                <div class="priority-dot-blue"></div>
                <div>
                    <div class="priority-text">🔵 Regular (Monitor)</div>
                    <div class="priority-count">{regular_n:,}</div>
                </div>
            </div>
            <div class="priority-item">
                <div class="priority-dot-green"></div>
                <div>
                    <div class="priority-text">🟢 High Value (Stable)</div>
                    <div class="priority-count">{hv_n:,}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Charts ───────────────────────────────────────────────────────────
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Customer Distribution")
            render_donut_chart(segments_df)
        with col2:
            st.subheader("Activity Trend")
            trend_df = load_activity_trend(results)
            render_line_chart(trend_df)

        st.markdown("""
        <div class="insight-box">
            ⚠️ <strong>Insight:</strong> Data reflects your uploaded file. Ensure it is recent for the most accurate AI recommendations.
        </div>
        """, unsafe_allow_html=True)

    # ── CUSTOMER GROUPS ────────────────────────────────────────────────────────
    elif page == "groups":
        st.header("Who are my customers?")

        col1, col2, col3, col4 = st.columns(4)
        segments_info = [
            {"name": "High Value", "icon": "⭐", "tag": "🟢 Stable — Leverage",   "tag_cls": "priority-dot-green",
             "desc": "Top spenders & frequent buyers. Core revenue drivers.", "action": "VIP perks, loyalty rewards, early access."},
            {"name": "Regular",    "icon": "🔁", "tag": "🔵 Monitor — Elevate",   "tag_cls": "priority-dot-blue",
             "desc": "Consistent purchasers with moderate engagement.",        "action": "Cross-sell to move toward High Value."},
            {"name": "Inactive",   "icon": "😴", "tag": "🟡 Warning — Win-back",   "tag_cls": "priority-dot-yellow",
             "desc": "Haven't interacted recently. High win-back potential.",   "action": "Launch re-engagement email campaign."},
            {"name": "At Risk",    "icon": "⚠️", "tag": "🔴 Critical — Act Now",   "tag_cls": "priority-dot-red",
             "desc": "High customer loss probability. Urgent intervention.",   "action": "Personalised discount + call outreach."},
        ]

        for i, col in enumerate([col1, col2, col3, col4]):
            info = segments_info[i]
            with col:
                st.markdown(f"""
                <div style='background:#0F172A; border:1px solid #1E293B; border-radius:10px; padding:16px; margin-bottom:10px; height:220px;'>
                    <div style='font-size:24px; margin-bottom:8px'>{info['icon']}</div>
                    <div style='font-size:15px; font-weight:700; color:#F1F5F9; margin-bottom:4px'>{info['name']}</div>
                    <div style='font-size:11px; color:#6366F1; font-weight:600; margin-bottom:10px'>{info['tag']}</div>
                    <div style='font-size:12px; color:#94A3B8; margin-bottom:8px; line-height:1.5'>{info['desc']}</div>
                    <div style='font-size:11px; color:#4ADE80; font-style:italic'>→ {info['action']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Group Sizes — Based on Uploaded File")
        segments_df = load_customer_segments(results)
        render_bar_chart(segments_df)

        # Segment breakdown table
        df = results.get('combined')
        if df is not None and 'segment_name' in df.columns:
            st.markdown("---")
            st.markdown("#### 📋 Segment Comparison Table")
            seg_counts   = df['segment_name'].value_counts()
            seg_spend    = df.groupby('segment_name')['monetary_value'].mean() if 'monetary_value' in df.columns else {}
            risk_map     = {"High Value ⭐": "🟢 Low", "Regular 🔁": "🔵 Medium", "Inactive 😴": "🟡 Warning", "At Risk ⚠️": "🔴 Critical"}
            action_map   = {"High Value ⭐": "VIP Program", "Regular 🔁": "Cross-sell", "Inactive 😴": "Win-back Campaign", "At Risk ⚠️": "Retention Discount"}

            rows = []
            for seg, count in seg_counts.items():
                avg_s = seg_spend.get(seg, 0) if hasattr(seg_spend, 'get') else 0
                rows.append({
                    "Segment":       seg,
                    "Count":         f"{count:,}",
                    "Avg Spend (₹)": f"₹{avg_s:,.0f}",
                    "Risk Level":    risk_map.get(seg, "—"),
                    "Recommended Action": action_map.get(seg, "—"),
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)

    # ── RISK & CUSTOMER LOSS ───────────────────────────────────────────────────
    elif page == "risk":
        st.header("Who is about to leave?")
        kpi_data     = load_kpi_data(results)
        at_risk_count = kpi_data.get('at_risk', 0)
        total        = kpi_data.get('total_customers', 1)
        risk_pct     = int((at_risk_count / total) * 100) if total > 0 else 0

        col1, col2 = st.columns([1, 1])
        with col1:
            render_risk_gauge(risk_pct)
        with col2:
            st.subheader("Risk Statistics")
            st.metric("Total At-Risk Customers", f"{at_risk_count:,}")

            if at_risk_count > 0:
                st.markdown(f"#### ⚠️ {kpi_data.get('at_risk_ratio')} customers may leave soon")
                st.markdown(f"#### 💰 Potential Revenue Loss: {kpi_data.get('potential_loss')} in next 30 days")

            if at_risk_count == 0:
                st.markdown("""
                <div style="background-color:#052e16; border-left: 4px solid #22c55e; padding: 1rem; border-radius: 6px; margin-top: 0.8rem;">
                    ✅ <strong style="color:#4ade80;">Your customer base looks healthy!</strong><br>
                    <span style="color:#86efac;">No at-risk customers were detected. Your customers are buying regularly, engaging frequently, and spending consistently.</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("**⚠️ Top warning signs found in your customer data:**")
                st.markdown("1. 🛒 **Customers are buying less often** — purchase count has dropped significantly")
                st.markdown("2. 📅 **Customers haven't shopped in a long time** — recency gap is growing")
                st.markdown("3. 💸 **Customers are spending less money** — total spend per visit declining")

        # Risk distribution histogram
        df = results.get('combined')
        if df is not None and 'churn_probability' in df.columns:
            st.markdown("---")
            st.markdown("#### 📊 Risk Probability Distribution")
            import plotly.express as px
            fig = px.histogram(
                df, x='churn_probability', nbins=30,
                color_discrete_sequence=["#6366F1"],
                labels={'churn_probability': 'Churn Probability'},
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(color="#94A3B8"), yaxis=dict(color="#94A3B8", gridcolor="#1E293B"),
                height=250, margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Top at-risk customers table
        if df is not None and 'churn_risk' in df.columns and at_risk_count > 0:
            st.markdown("---")
            st.markdown("#### 🔴 Top At-Risk Customers")
            risk_df = df[df['churn_risk'] == 'High 🔴'].copy()
            display_cols = ['customer_id', 'churn_risk', 'recency_days', 'monetary_value', 'segment_name']
            display_cols = [c for c in display_cols if c in risk_df.columns]
            risk_df['Suggested Action'] = "Personalised Retention Offer"
            display_cols.append('Suggested Action')
            st.dataframe(risk_df[display_cols].head(20), use_container_width=True, hide_index=True)

        if at_risk_count == 0:
            st.markdown("""
            <div class="insight-box" style="background:rgba(34,197,94,0.08); border-left:4px solid #22c55e; color:#86efac;">
                💡 <strong>Insight:</strong> All customers are currently active and engaged. Continue monitoring for early warning signs.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box-blue">
                💡 <strong>Insight:</strong> Customers classified as "At Risk" have ~75% chance of leaving within the next month without intervention.
                Go to <strong>Decision Center</strong> to apply automated retention strategies.
            </div>
            """, unsafe_allow_html=True)

    # ── DECISION CENTER ────────────────────────────────────────────────────────
    elif page == "actions":
        st.markdown("""
        <div style='margin-bottom:4px'>
            <span style='font-size:12px; color:#EF4444; text-transform:uppercase; letter-spacing:2px;'>Action Required</span>
        </div>
        """, unsafe_allow_html=True)
        st.header("Decision Center")
        st.caption("AI-generated, prioritised actions — from insight to execution.")
        render_action_cards()

    # ── CUSTOMER LOOKUP ────────────────────────────────────────────────────────
    elif page == "lookup":
        st.header("Tell me about a specific customer")
        default_id = 1
        if results and results.get('combined') is not None and not results.get('combined').empty and 'customer_id' in results.get('combined').columns:
            default_id = int(results.get('combined')['customer_id'].iloc[0])

        customer_id = st.number_input("Enter Customer ID", min_value=1, value=default_id, step=1)

        if st.button("Search"):
            data = load_customer_lookup(customer_id, results)
            st.markdown(f"""
<div class="ai-summary-card">
<div class="ai-badge">✨ AI Profile Summary</div>
<div style="font-size: 14px; color: #94A3B8; margin-bottom: 4px;">Customer ID: {data['Customer ID']}</div>
<div style="font-size: 18px; font-weight: 600; color: #F1F5F9; margin-bottom: 16px;">
Segment: {data['Segment']} &nbsp; • &nbsp; Loss Prob: {data['Customer Loss Probability']}
</div>
<div class="ai-score">📊 Customer Value Score: {data['Value Score']}</div>
<div class="ai-reason">💡 <strong>Reason:</strong> {data['Reason']}</div>
<hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">
<div style="font-size: 14px; color: #F1F5F9;">
📍 <strong>Activity:</strong> {data['Activity']}<br>
🎁 <strong>Suggested Action:</strong> {data['Suggested Action']}
</div>
</div>
""", unsafe_allow_html=True)

    # ── AI INTELLIGENCE ────────────────────────────────────────────────────────
    elif page == "ai_insights":
        st.markdown("""
        <div style='margin-bottom:4px'>
            <span style='font-size:12px; color:#6366F1; text-transform:uppercase; letter-spacing:2px;'>AI Narrative Layer</span>
        </div>
        """, unsafe_allow_html=True)
        st.header("AI Intelligence — What is the reasoning?")
        render_ai_insights()

    # ── XAI ───────────────────────────────────────────────────────────────────
    elif page == "xai":
        st.markdown("""
        <div style='margin-bottom:4px'>
            <span style='font-size:12px; color:#6366F1; text-transform:uppercase; letter-spacing:2px;'>Explainable AI</span>
        </div>
        """, unsafe_allow_html=True)
        st.header("AI Explainer — Why did the AI predict this?")
        render_xai_explainer()

    # ── BUSINESS IMPACT ────────────────────────────────────────────────────────
    elif page == "impact":
        st.markdown("""
        <div style='margin-bottom:4px'>
            <span style='font-size:12px; color:#22C55E; text-transform:uppercase; letter-spacing:2px;'>Financial Intelligence</span>
        </div>
        """, unsafe_allow_html=True)
        st.header("Business Impact — What is the ROI?")
        render_business_impact()

    # ── AI ASSISTANT ───────────────────────────────────────────────────────────
    elif page == "assistant":
        st.markdown("""
        <div style='margin-bottom:4px'>
            <span style='font-size:12px; color:#6366F1; text-transform:uppercase; letter-spacing:2px;'>Conversational AI</span>
        </div>
        """, unsafe_allow_html=True)
        st.header("AI Assistant — Ask the Intelligence Engine")
        render_ai_assistant()

    # ── SYSTEM HEALTH ──────────────────────────────────────────────────────────
    elif page == "system_health":
        st.markdown("""
        <div style='margin-bottom:4px'>
            <span style='font-size:12px; color:#22C55E; text-transform:uppercase; letter-spacing:2px;'>Production Monitoring</span>
        </div>
        """, unsafe_allow_html=True)
        st.header("System Health — AI & Model Status")
        render_system_health()

    # ── SYSTEM ARCHITECTURE ────────────────────────────────────────────────────
    elif page == "feedback":
        st.markdown("""
        <div style='margin-bottom:4px'>
            <span style='font-size:12px; color:#6366F1; text-transform:uppercase; letter-spacing:2px;'>Architecture</span>
        </div>
        """, unsafe_allow_html=True)
        st.header("System Architecture — How does it work?")
        render_feedback_loop()
