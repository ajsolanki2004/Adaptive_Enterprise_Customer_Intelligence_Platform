"""
business_impact.py
Layer: Business Impact
Translates ML predictions into boardroom-level ROI and revenue metrics.
Upgraded with: Before vs After simulation, visual comparison, and prescriptive insights.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def render_business_impact():
    st.markdown("""
    <style>
    .roi-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        border: 1px solid #4338ca;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.4);
        margin-bottom: 20px;
    }
    .roi-val   { font-size: 32px; font-weight: 800; color: #818CF8; margin: 10px 0; }
    .roi-label { font-size: 13px; text-transform: uppercase; letter-spacing: 1px; color: #94A3B8; }
    .scenario-card {
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 12px;
    }
    .scenario-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 9px 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        font-size: 14px;
    }
    .scenario-row:last-child { border-bottom: none; }
    .s-label { color: #94A3B8; }
    .s-val   { font-weight: 600; color: #F1F5F9; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 💰 Business Impact & ROI Intelligence")
    st.markdown("Translate AI predictions directly into boardroom-ready financial outcomes.")

    results = st.session_state.get('results', {})
    if not results or results.get('combined') is None:
        st.warning("Please upload and analyze data first.")
        return

    df = results['combined']

    total_rev   = df['monetary_value'].sum() if 'monetary_value' in df.columns else 0
    at_risk_mask = (df['churn_risk'] == 'High 🔴') if 'churn_risk' in df.columns else pd.Series([False]*len(df))
    at_risk_rev = df[at_risk_mask]['monetary_value'].sum() if 'monetary_value' in df.columns else 0
    recov_rev   = at_risk_rev * 0.30

    # ── KPI Strip ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='roi-card'><div class='roi-label'>Total Tracked Revenue</div><div class='roi-val'>₹{total_rev:,.0f}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='roi-card' style='border-color:#EF4444; background:linear-gradient(135deg,#0f172a,#450a0a);'>"
                    f"<div class='roi-label'>Revenue at Risk</div>"
                    f"<div class='roi-val' style='color:#F87171'>₹{at_risk_rev:,.0f}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='roi-card' style='border-color:#22c55e; background:linear-gradient(135deg,#0f172a,#052e16);'>"
                    f"<div class='roi-label'>Recoverable (30% Save)</div>"
                    f"<div class='roi-val' style='color:#4ade80'>₹{recov_rev:,.0f}</div></div>", unsafe_allow_html=True)
    with c4:
        roi_ratio = (recov_rev / (at_risk_rev * 0.15)) if at_risk_rev > 0 else 0
        st.markdown(f"<div class='roi-card' style='border-color:#6366F1;'>"
                    f"<div class='roi-label'>Est. Campaign ROI</div>"
                    f"<div class='roi-val'>{roi_ratio:.1f}x</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    # ── Before vs After Simulation ────────────────────────────────────────────
    with col1:
        st.markdown("#### 📊 Before vs After AI Strategy")
        st.caption("Impact of applying all recommended strategies.")

        loss_without = at_risk_rev
        loss_with    = at_risk_rev * 0.70   # 30% saved
        saved        = loss_without - loss_with
        safe_rev     = total_rev - at_risk_rev

        # Grouped bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Without AI Strategy",
            x=["Revenue Saved", "Revenue Lost"],
            y=[safe_rev, loss_without],
            marker_color=["#334155", "#EF4444"],
        ))
        fig.add_trace(go.Bar(
            name="With AI Strategy",
            x=["Revenue Saved", "Revenue Lost"],
            y=[safe_rev + saved, loss_with],
            marker_color=["#22C55E", "#F59E0B"],
        ))
        fig.update_layout(
            barmode='group',
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font=dict(color="#94A3B8")),
            xaxis=dict(color="#94A3B8"),
            yaxis=dict(color="#94A3B8", gridcolor="#1E293B"),
            font=dict(color="#F8FAFC"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Comparison table
        st.markdown(f"""
        <div style='background:#0F172A; border:1px solid #1E293B; border-radius:10px; padding:16px; font-size:14px;'>
            <div class='scenario-row'>
                <span class='s-label'>❌ Without AI — Revenue Lost</span>
                <span class='s-val' style='color:#F87171'>₹{loss_without:,.0f}</span>
            </div>
            <div class='scenario-row'>
                <span class='s-label'>✅ With AI — Projected Loss</span>
                <span class='s-val' style='color:#FCD34D'>₹{loss_with:,.0f}</span>
            </div>
            <div class='scenario-row'>
                <span class='s-label' style='font-weight:700; color:#F1F5F9'>💰 Net Revenue Saved</span>
                <span class='s-val' style='color:#4ADE80; font-size:18px'>+₹{saved:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── ROI Calculator ────────────────────────────────────────────────────────
    with col2:
        st.markdown("#### 🧮 Retention Campaign ROI Simulator")
        st.caption("Adjust parameters to model your retention investment.")

        discount_pct = st.slider("Proposed Discount (%)", min_value=5, max_value=50, value=15, step=5)
        success_rate = st.slider("Expected Win-back Rate (%)", min_value=5, max_value=80, value=25, step=5)

        target_pool       = at_risk_rev
        cost_of_campaign  = target_pool * (discount_pct / 100.0) * (success_rate / 100.0)
        saved_revenue     = target_pool * (success_rate / 100.0)
        net_roi           = saved_revenue - cost_of_campaign
        roi_multiplier    = (net_roi / cost_of_campaign) if cost_of_campaign > 0 else 0

        # Funnel / waterfall visual
        fig2 = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["At-Risk Pool", "Campaign Cost", "Revenue Saved", "Net Retained"],
            y=[target_pool, -cost_of_campaign, saved_revenue, 0],
            connector={"line": {"color": "#334155"}},
            increasing={"marker": {"color": "#22C55E"}},
            decreasing={"marker": {"color": "#EF4444"}},
            totals={"marker": {"color": "#6366F1"}},
            text=[f"₹{target_pool:,.0f}", f"-₹{cost_of_campaign:,.0f}", f"+₹{saved_revenue:,.0f}", f"₹{net_roi:,.0f}"],
            textposition="outside",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=260,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(color="#94A3B8"),
            yaxis=dict(color="#94A3B8", gridcolor="#1E293B"),
            font=dict(color="#F8FAFC", size=12),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Summary row
        st.markdown(f"""
        <div style='background:#0F172A; border:1px solid #1E293B; border-radius:10px; padding:16px; display:flex; justify-content:space-around; flex-wrap:wrap; gap:16px;'>
            <div style='text-align:center'>
                <div style='color:#64748B; font-size:11px; text-transform:uppercase; letter-spacing:1px'>Campaign Cost</div>
                <div style='color:#F87171; font-size:22px; font-weight:700'>₹{cost_of_campaign:,.0f}</div>
            </div>
            <div style='text-align:center'>
                <div style='color:#64748B; font-size:11px; text-transform:uppercase; letter-spacing:1px'>Revenue Saved</div>
                <div style='color:#4ADE80; font-size:22px; font-weight:700'>₹{saved_revenue:,.0f}</div>
            </div>
            <div style='text-align:center'>
                <div style='color:#64748B; font-size:11px; text-transform:uppercase; letter-spacing:1px'>ROI</div>
                <div style='color:#818CF8; font-size:22px; font-weight:700'>{roi_multiplier:.1f}x</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Prescriptive Insight ──────────────────────────────────────────────────
    if roi_multiplier >= 2:
        st.success(
            f"📈 **High ROI Strategy Detected.** A {discount_pct}% discount campaign with a {success_rate}% win-back rate "
            f"yields a **{roi_multiplier:.1f}x ROI**, saving ₹{net_roi:,.0f} net. This is a commercially strong investment."
        )
    elif roi_multiplier >= 1:
        st.info(
            f"💡 **Moderate ROI.** The simulation shows a {roi_multiplier:.1f}x return. "
            f"Consider lowering the discount or improving targeting to maximise ROI."
        )
    else:
        st.warning("⚠️ Low ROI detected with current parameters. Consider reducing the discount or increasing the expected win-back rate.")
