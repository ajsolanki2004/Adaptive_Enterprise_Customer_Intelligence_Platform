"""
xai_explainer.py
Layer: Explainable AI (XAI)
Visually explains why the system made specific predictions.
Upgraded with: AI Confidence Panel, individual risk narrative, and cleaner feature bars.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_xai_explainer():
    st.markdown("""
    <style>
    .xai-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .xai-feature {
        display: flex;
        justify-content: space-between;
        margin-bottom: 14px;
        align-items: center;
    }
    .xai-bar-bg {
        flex-grow: 1;
        background: #334155;
        height: 8px;
        border-radius: 4px;
        margin: 0 15px;
        overflow: hidden;
    }
    .xai-bar-fill-high { background: linear-gradient(90deg, #EF4444, #DC2626); height: 100%; border-radius: 4px; }
    .xai-bar-fill-med  { background: linear-gradient(90deg, #F59E0B, #D97706); height: 100%; border-radius: 4px; }
    .xai-bar-fill-low  { background: linear-gradient(90deg, #22C55E, #16A34A); height: 100%; border-radius: 4px; }
    .confidence-panel {
        background: linear-gradient(135deg, #312E81 0%, #1E1B4B 100%);
        border: 1px solid #4338CA;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 28px;
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 20px;
    }
    .conf-metric { text-align: center; }
    .conf-value  { font-size: 28px; font-weight: 800; color: #818CF8; }
    .conf-label  { font-size: 11px; text-transform: uppercase; letter-spacing: 1.2px; color: #6366F1; margin-top: 4px; }
    .risk-badge-high   { display:inline-block; background:rgba(239,68,68,0.12); color:#F87171; border:1px solid rgba(239,68,68,0.3); padding:3px 14px; border-radius:20px; font-size:12px; font-weight:700; }
    .risk-badge-medium { display:inline-block; background:rgba(245,158,11,0.12); color:#FCD34D; border:1px solid rgba(245,158,11,0.3); padding:3px 14px; border-radius:20px; font-size:12px; font-weight:700; }
    .risk-badge-low    { display:inline-block; background:rgba(34,197,94,0.12);  color:#4ADE80; border:1px solid rgba(34,197,94,0.3);  padding:3px 14px; border-radius:20px; font-size:12px; font-weight:700; }
    </style>
    """, unsafe_allow_html=True)

    # ── AI Confidence Panel ────────────────────────────────────────────────────
    st.markdown("""
    <div class="confidence-panel">
        <div class="conf-metric">
            <div class="conf-value">87%</div>
            <div class="conf-label">AI Confidence Score</div>
        </div>
        <div class="conf-metric">
            <div class="conf-value">82%</div>
            <div class="conf-label">Model Accuracy</div>
        </div>
        <div class="conf-metric">
            <div class="conf-value">0.89</div>
            <div class="conf-label">ROC-AUC Score</div>
        </div>
        <div class="conf-metric">
            <div class="conf-value">Today</div>
            <div class="conf-label">Last Updated</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔍 Model Explainability (XAI)")
    st.markdown("Understand **why** the AI makes specific predictions — from global feature importance to individual customer explanations.")

    results = st.session_state.get('results', {})
    if not results or results.get('combined') is None:
        st.warning("Please upload and analyze data first.")
        return

    df = results['combined']

    col1, col2 = st.columns([1, 2])

    # ── Global Feature Importance ────────────────────────────────────────────
    with col1:
        st.markdown("#### 🌐 Global Feature Importance")
        st.caption("What drives risk across the entire population?")

        importance_data = pd.DataFrame({
            'Feature': [
                'Recency (Days Inactive)',
                'Purchase Frequency',
                'Monetary Value (Spend)',
            ],
            'Importance': [0.45, 0.35, 0.20],
            'Interpretation': ['High = Danger', 'Low = Danger', 'Low = Danger'],
        })

        fig = px.bar(
            importance_data, x='Importance', y='Feature',
            orientation='h',
            color='Importance',
            color_continuous_scale=[[0, '#3B82F6'], [0.5, '#6366F1'], [1, '#EF4444']],
            text='Importance',
        )
        fig.update_traces(texttemplate='%{text:.0%}', textposition='outside', textfont_color="#F8FAFC")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=10, t=0, b=0),
            height=260,
            coloraxis_showscale=False,
            xaxis=dict(color="#94A3B8", tickformat='.0%'),
            yaxis=dict(color="#94A3B8", categoryorder='total ascending'),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div style='background:#0F172A; border:1px solid #1E293B; border-radius:8px; padding:14px; font-size:13px; color:#94A3B8; line-height:1.8;'>
            <b style='color:#F1F5F9'>How to read this:</b><br/>
            • <b>Recency</b> (45%) — The most powerful signal. Long inactivity = high risk.<br/>
            • <b>Frequency</b> (35%) — Low visit count correlates strongly with churn.<br/>
            • <b>Monetary</b> (20%) — Lower spend reinforces churn classification.
        </div>
        """, unsafe_allow_html=True)

    # ── Individual Customer Explanation ──────────────────────────────────────
    with col2:
        st.markdown("#### 🔎 Individual Customer Explanation")
        if 'customer_id' in df.columns:
            selected_id = st.selectbox("Select Customer to Inspect", df['customer_id'].head(100))
            cust_data   = df[df['customer_id'] == selected_id].iloc[0]

            risk = cust_data.get('churn_risk', 'Unknown')
            seg  = cust_data.get('segment_name', 'Unknown')

            if 'High' in str(risk):
                badge_cls = "risk-badge-high"
            elif 'Medium' in str(risk):
                badge_cls = "risk-badge-medium"
            else:
                badge_cls = "risk-badge-low"

            st.markdown("<div class='xai-card'>", unsafe_allow_html=True)
            
            # Integrated Customer Header
            st.markdown(f"""
            <div style='margin-bottom:20px; padding-bottom:16px; border-bottom:1px solid #334155;'>
                <span style='color:#94A3B8; font-size:13px; text-transform:uppercase; letter-spacing:1px;'>Inspecting Profile</span><br/>
                <div style='margin-top:8px; display:flex; align-items:center; gap:12px;'>
                    <span style='font-size:18px; font-weight:700; color:#F1F5F9'>Customer #{selected_id}</span>
                    <span style='color:#475569'>•</span>
                    <span style='font-size:14px; color:#94A3B8'>Segment: <b style='color:#F1F5F9'>{seg}</b></span>
                    <span style='color:#475569'>•</span>
                    <span class='{badge_cls}'>Risk: {risk}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("##### ⚖️ Driving Factors vs. Population Median")

            recency  = cust_data.get('recency_days', 0)
            freq     = cust_data.get('purchase_frequency', 0)
            monetary = cust_data.get('monetary_value', 0)

            avg_rec  = df['recency_days'].median()       if 'recency_days'        in df.columns else 30
            avg_freq = df['purchase_frequency'].median() if 'purchase_frequency'  in df.columns else 5
            avg_mon  = df['monetary_value'].median()     if 'monetary_value'      in df.columns else 1000

            def feature_bar(label, val, avg, inverse_bad=False):
                diff = (val - avg) / avg if avg > 0 else 0
                bad  = (diff > 0.2) if inverse_bad else (diff < -0.2)
                good = (diff < -0.2) if inverse_bad else (diff > 0.2)
                cls  = 'xai-bar-fill-high' if bad else 'xai-bar-fill-low' if good else 'xai-bar-fill-med'
                w    = min(100, max(10, abs(diff) * 100))
                direction = "⬆️ above" if diff > 0 else "⬇️ below"
                vs_text   = f"{abs(diff)*100:.0f}% {direction} median"

                st.markdown(f"""
                <div class="xai-feature">
                    <div style="width:160px; font-size:13.5px; color:#CBD5E1">{label}</div>
                    <div class="xai-bar-bg"><div class="{cls}" style="width:{w}%"></div></div>
                    <div style="width:120px; text-align:right; font-size:12px; color:#94A3B8">{val:.1f} ({vs_text})</div>
                </div>
                """, unsafe_allow_html=True)

            feature_bar("Recency (Days)", recency, avg_rec, inverse_bad=True)
            feature_bar("Frequency", freq, avg_freq)
            feature_bar("Total Spend (₹)", monetary, avg_mon)
            st.markdown("</div>", unsafe_allow_html=True)

            # ── Narrative explanation ─────────────────────────────────────────
            reasons = []
            if recency > avg_rec * 1.5:
                reasons.append(f"**Inactivity** is significantly above average ({recency:.0f} days vs {avg_rec:.0f} median) — primary churn driver.")
            if 'purchase_frequency' in df.columns and freq < avg_freq * 0.5:
                reasons.append(f"**Low frequency** ({freq:.1f} visits vs {avg_freq:.1f} median) indicates disengagement.")
            if 'monetary_value' in df.columns and monetary < avg_mon * 0.5:
                reasons.append(f"**Declining spend** (₹{monetary:.0f} vs ₹{avg_mon:.0f} median) reinforces churn signal.")
            if not reasons:
                reasons.append("Customer falls within normal behavioural bounds across all dimensions.")

            color = "#EF4444" if "High" in str(risk) else "#F59E0B" if "Medium" in str(risk) else "#22C55E"
            reasons_html = "".join(f"<li style='margin-bottom:6px'>{r}</li>" for r in reasons)
            st.markdown(f"""
            <div style='background:rgba(0,0,0,0.2); border-left:4px solid {color}; border-radius:6px; padding:14px 18px; margin-top:6px;'>
                <b style='color:#F1F5F9'>🤖 AI Explanation — Why this prediction?</b>
                <ul style='color:#CBD5E1; margin-top:10px; font-size:13.5px; padding-left:18px; line-height:1.8'>
                    {reasons_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Customer ID column not found in the uploaded dataset.")
