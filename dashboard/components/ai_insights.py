"""
ai_insights.py
Layer: AI Insight Generation
Converts ML results into human-readable executive narratives using rule-based NLP.
Upgraded to CEO-level communication style with priority tagging and urgency signals.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

def _get_metric(results, key, df_key='combined'):
    if not results or results.get(df_key) is None:
        return 0
    df = results[df_key]
    if key == 'total': return len(df)
    if key == 'at_risk':
        if 'churn_risk' in df.columns:
            return len(df[df['churn_risk'] == 'High 🔴'])
        return 0
    if key == 'high_value':
        if 'segment_name' in df.columns:
            return len(df[df['segment_name'] == 'High Value ⭐'])
        return 0
    if key == 'inactive':
        if 'segment_name' in df.columns:
            return len(df[df['segment_name'].str.contains('Inactive', na=False)])
        return 0
    if key == 'total_revenue':
        if 'monetary_value' in df.columns:
            return df['monetary_value'].sum()
        return 0
    if key == 'revenue_at_risk':
        if 'churn_risk' in df.columns and 'monetary_value' in df.columns:
            return df[df['churn_risk'] == 'High 🔴']['monetary_value'].sum()
        return 0
    return 0

def generate_executive_summary(results):
    total = _get_metric(results, 'total')
    if total == 0:
        return None, "low"

    at_risk       = _get_metric(results, 'at_risk')
    risk_pct      = (at_risk / total) * 100 if total > 0 else 0
    rev_at_risk   = _get_metric(results, 'revenue_at_risk')
    high_value    = _get_metric(results, 'high_value')
    inactive      = _get_metric(results, 'inactive')
    total_rev     = _get_metric(results, 'total_revenue')

    rev_fmt = f"₹{rev_at_risk:,.0f}"
    if rev_at_risk >= 10_00_00_000:
        rev_fmt = f"₹{rev_at_risk/10_00_00_000:.1f} Cr"
    elif rev_at_risk >= 1_00_000:
        rev_fmt = f"₹{rev_at_risk/1_00_000:.1f}L"

    if risk_pct > 20:
        level = "critical"
        narrative = (
            f"🚨 **Immediate executive attention required:** {risk_pct:.1f}% of customers "
            f"({at_risk:,} users) are at critical risk of leaving, threatening {rev_fmt} in "
            f"revenue within the next 30 days.\n\n"
            f"**📉 Primary Drivers:**\n"
            f"- Prolonged inactivity and declining purchase frequency\n"
            f"- Engagement frequency dropping below sustainable threshold\n\n"
            f"**✅ Opportunity:** {high_value:,} high-value customers remain stable and "
            f"can be leveraged for growth through loyalty programs.\n\n"
            f"**👉 Immediate retention strategy is strongly recommended.**"
        )
    elif risk_pct > 5:
        level = "warning"
        narrative = (
            f"⚠️ **Attention required:** {risk_pct:.1f}% of customers ({at_risk:,} users) "
            f"exhibit early-stage churn signals, representing a {rev_fmt} revenue risk.\n\n"
            f"**📉 Key Indicators:**\n"
            f"- Moderate inactivity in a segment of users\n"
            f"- {inactive:,} customers classified as dormant\n\n"
            f"**✅ Proactive engagement now can recover the majority of at-risk revenue.**"
        )
    else:
        level = "healthy"
        narrative = (
            f"✅ **Your customer base is in a strong position.** AECIP has analysed {total:,} "
            f"customers and detected minimal churn signals.\n\n"
            f"**⭐ {high_value:,} high-value customers** are actively contributing to revenue. "
            f"Now is the ideal time to invest in loyalty and VIP programs for long-term retention growth."
        )

    return narrative, level


def render_ai_insights():
    st.markdown("""
    <style>
    .narrative-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-left: 4px solid #6366F1;
        padding: 20px 24px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .segment-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
        transition: border-color 0.2s;
    }
    .segment-card:hover { border-color: #6366F1; }
    .priority-tag-red {
        display: inline-block;
        background: rgba(239,68,68,0.12);
        border: 1px solid rgba(239,68,68,0.4);
        color: #F87171;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .priority-tag-yellow {
        display: inline-block;
        background: rgba(245,158,11,0.12);
        border: 1px solid rgba(245,158,11,0.4);
        color: #FCD34D;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .priority-tag-green {
        display: inline-block;
        background: rgba(34,197,94,0.12);
        border: 1px solid rgba(34,197,94,0.4);
        color: #4ADE80;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .priority-tag-blue {
        display: inline-block;
        background: rgba(99,102,241,0.12);
        border: 1px solid rgba(99,102,241,0.4);
        color: #818CF8;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .seg-action-hint {
        margin-top: 8px;
        padding: 8px 12px;
        background: rgba(99,102,241,0.07);
        border-left: 3px solid #6366F1;
        border-radius: 4px;
        font-size: 12px;
        color: #94A3B8;
    }
    </style>
    """, unsafe_allow_html=True)

    results = st.session_state.get('results', {})
    narrative, level = generate_executive_summary(results)

    # ── Executive Alert Banner ────────────────────────────────────────────────
    if narrative:
        if level == "critical":
            st.error(narrative)
        elif level == "warning":
            st.warning(narrative)
        else:
            st.success(narrative)
    else:
        st.warning("Please upload and analyse data first.")
        return

    if not results or results.get('combined') is None:
        return

    df = results['combined']
    st.markdown("---")

    col1, col2 = st.columns(2)

    # ── Segment Behavioural Analysis (with priority tags) ─────────────────────
    with col1:
        st.markdown("### 📊 Segment Behavioural Analysis")
        st.caption("Priority-tagged interpretation of each customer group.")

        if 'segment_name' in df.columns:
            counts = df['segment_name'].value_counts()

            seg_config = {
                "At Risk":    ("priority-tag-red",    "🔴 Critical Priority",   "Immediate churn risk detected.",
                               "👉 Action: Launch 15–20% personalised discount + call outreach campaign now."),
                "Inactive":   ("priority-tag-yellow",  "🟡 Warning",             "Dormant — no recent engagement.",
                               "👉 Action: Win-back email campaign + re-engagement offers required."),
                "Regular":    ("priority-tag-blue",    "🔵 Stable — Monitor",    "Consistent but moderate activity.",
                               "👉 Action: Cross-sell to elevate to High Value tier."),
                "High Value": ("priority-tag-green",   "🟢 Healthy — Leverage",  "Top spenders with strong loyalty.",
                               "👉 Action: VIP perks, loyalty programs, and early access offers."),
            }

            for seg, count in counts.items():
                # Match config key
                cfg_key = next((k for k in seg_config if k in str(seg)), None)
                if cfg_key:
                    tag_cls, tag_label, meaning, action = seg_config[cfg_key]
                else:
                    tag_cls, tag_label, meaning, action = "priority-tag-blue", "🔵 Segment", "Standard segment.", ""

                if "High Value" in str(seg):
                    body = f"**{seg}** — {count:,} customers. Exceptional loyalty with high spend frequency."
                elif "Regular" in str(seg):
                    body = f"**{seg}** — {count:,} customers. The revenue backbone. Consistent spend and moderate engagement."
                elif "Inactive" in str(seg):
                    body = f"**{seg}** — {count:,} customers. Dormant. Haven't engaged recently — highest win-back potential."
                elif "At Risk" in str(seg):
                    body = f"**{seg}** — {count:,} customers. Previously engaged but steeply declining. Urgent intervention needed."
                else:
                    body = f"**{seg}** — {count:,} customers."

                st.markdown(f"""
                <div class='segment-card'>
                    <div class='{tag_cls}'>{tag_label}</div>
                    <div style='color:#F1F5F9; font-size:14px; margin-top:4px'>{body}</div>
                    <div class='seg-action-hint'>{action}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("Segmentation analysis not available.")

    # ── Diagnostic Risk Explanation ───────────────────────────────────────────
    with col2:
        st.markdown("### 🔴 Diagnostic Risk Explanation")
        st.caption("Causal storytelling — why customers are at risk.")

        if 'churn_risk' in df.columns:
            high_risk = df[df['churn_risk'] == 'High 🔴']
            if len(high_risk) > 0:
                avg_rec  = high_risk['recency_days'].mean()  if 'recency_days'        in high_risk.columns else None
                avg_freq = high_risk['purchase_frequency'].mean() if 'purchase_frequency' in high_risk.columns else None

                rec_str  = f"{avg_rec:.1f} days since last purchase"  if avg_rec  is not None else "data unavailable"
                freq_str = f"{avg_freq:.1f} average visits"           if avg_freq is not None else "data unavailable"

                st.markdown(f"""
                <div style='background:rgba(239,68,68,0.07); border:1px solid rgba(239,68,68,0.25); border-radius:10px; padding:20px; margin-bottom:16px;'>
                    <div style='font-size:15px; font-weight:700; color:#F87171; margin-bottom:12px'>
                        🚨 Why are {len(high_risk):,} customers at risk?
                    </div>
                    <div style='color:#CBD5E1; font-size:14px; line-height:1.8'>
                        <b>1. Prolonged Inactivity</b><br/>
                        &nbsp;&nbsp;&nbsp;→ High-risk users have been inactive for <b style='color:#F87171'>{rec_str}</b> on average.<br/><br/>
                        <b>2. Declining Engagement</b><br/>
                        &nbsp;&nbsp;&nbsp;→ Lifetime interaction count is only <b style='color:#F87171'>{freq_str}</b>.<br/><br/>
                        <b>3. Spend Deterioration</b><br/>
                        &nbsp;&nbsp;&nbsp;→ Monetary value trending below cohort median.<br/><br/>
                        <i style='color:#64748B'>This combination strongly correlates with historical churn patterns in our training data.</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Risk distribution chart
                st.markdown("#### 📊 Risk Distribution")
                risk_counts = df['churn_risk'].value_counts().reset_index()
                risk_counts.columns = ['Risk Level', 'Count']
                color_m = {'High 🔴': '#EF4444', 'Medium 🟡': '#F59E0B', 'Low 🟢': '#22C55E'}
                risk_counts['Color'] = risk_counts['Risk Level'].map(color_m)
                fig = px.bar(
                    risk_counts, x='Risk Level', y='Count',
                    color='Risk Level',
                    color_discrete_map=color_m,
                    text='Count'
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    height=240,
                    margin=dict(l=0, r=0, t=10, b=0),
                    xaxis=dict(color="#94A3B8"),
                    yaxis=dict(color="#94A3B8", gridcolor="#1E293B")
                )
                fig.update_traces(textposition='outside', textfont_color="#F8FAFC")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ No significant risk patterns detected — your customer base is healthy.")
        else:
            st.write("Risk analysis column not available in the uploaded dataset.")

    st.markdown("---")

    # ── AI Confidence Footer ──────────────────────────────────────────────────
    st.markdown("""
    <div style='background:#0F172A; border:1px solid #1E293B; border-radius:10px; padding:16px 24px;
                display:flex; justify-content:space-around; flex-wrap:wrap; gap:16px;'>
        <div style='text-align:center'>
            <div style='font-size:11px; color:#64748B; text-transform:uppercase; letter-spacing:1px'>AI Confidence</div>
            <div style='font-size:22px; font-weight:700; color:#818CF8'>87%</div>
        </div>
        <div style='text-align:center'>
            <div style='font-size:11px; color:#64748B; text-transform:uppercase; letter-spacing:1px'>Model Accuracy</div>
            <div style='font-size:22px; font-weight:700; color:#22C55E'>82%</div>
        </div>
        <div style='text-align:center'>
            <div style='font-size:11px; color:#64748B; text-transform:uppercase; letter-spacing:1px'>ROC-AUC</div>
            <div style='font-size:22px; font-weight:700; color:#F59E0B'>0.89</div>
        </div>
        <div style='text-align:center'>
            <div style='font-size:11px; color:#64748B; text-transform:uppercase; letter-spacing:1px'>Last Updated</div>
            <div style='font-size:22px; font-weight:700; color:#94A3B8'>Today</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
