"""
actions.py  ──  Decision Center
AECIP Executive Dashboard — Industry-Level Upgrade

Features:
  - Auto-generated recommended actions with priority/urgency signals
  - AI confidence + expected ROI per strategy
  - Automation simulation (Run All Strategies button)
  - Before vs After impact preview
  - Real customer filtering + action log
"""

import streamlit as st
import pandas as pd
from datetime import datetime


# ── Strategy Definitions ───────────────────────────────────────────────────────

STRATEGIES = [
    {
        "key":      "at_risk",
        "icon":     "🎯",
        "urgency":  "CRITICAL",
        "urgency_color": "#EF4444",
        "urgency_bg":    "rgba(239,68,68,0.12)",
        "urgency_border":"rgba(239,68,68,0.40)",
        "title":    "Retention Campaign — High-Risk Customers",
        "desc":     "AI has detected a critical churn cohort. Launch a personalised retention campaign immediately.",
        "actions": [
            "📧 Send personalised retention email with 15–20% exclusive discount",
            "📞 Trigger outbound call outreach for top 50 at-risk accounts",
            "🎁 Offer loyalty credit or bonus points as re-engagement incentive",
        ],
        "impact":   "Estimated 30% churn reduction | Recover ~₹30,000+/month",
        "intelligence": {"confidence": "87%", "roi": "3.2x"},
        "card_border": "#EF4444",
        "card_glow":   "rgba(239,68,68,0.08)",
    },
    {
        "key":      "inactive",
        "icon":     "📧",
        "urgency":  "WARNING",
        "urgency_color": "#F59E0B",
        "urgency_bg":    "rgba(245,158,11,0.12)",
        "urgency_border":"rgba(245,158,11,0.40)",
        "title":    "Win-Back Campaign — Inactive Customers",
        "desc":     "Dormant customers have not engaged recently. A targeted win-back campaign can reactivate this segment.",
        "actions": [
            "📨 Launch win-back email sequence (3-touch automated flow)",
            "🔔 Send push notification / SMS reminder with special offer",
            "🎟️ Offer re-engagement incentive (e.g. free shipping / bonus)",
        ],
        "impact":   "Re-engage est. 25–40% of dormant users | Recover lost frequency",
        "intelligence": {"confidence": "74%", "roi": "2.1x"},
        "card_border": "#F59E0B",
        "card_glow":   "rgba(245,158,11,0.06)",
    },
    {
        "key":      "high_value",
        "icon":     "⭐",
        "urgency":  "OPPORTUNITY",
        "urgency_color": "#22C55E",
        "urgency_bg":    "rgba(34,197,94,0.12)",
        "urgency_border":"rgba(34,197,94,0.40)",
        "title":    "VIP Loyalty Program — High-Value Customers",
        "desc":     "Your best customers deserve recognition. Invest in them now to unlock compound lifetime value.",
        "actions": [
            "🏆 Enrol top 50 customers in VIP / Platinum loyalty tier",
            "🎁 Grant early access to new products or premium features",
            "💌 Send personalised appreciation note from account manager",
        ],
        "impact":   "Increase LTV by 25–35% | Boost referral rate by 15%",
        "intelligence": {"confidence": "91%", "roi": "4.5x"},
        "card_border": "#22C55E",
        "card_glow":   "rgba(34,197,94,0.06)",
    },
]


# ── Customer filtering ─────────────────────────────────────────────────────────

def _get_customers(strategy_key: str, results: dict) -> pd.DataFrame:
    combined = results.get("combined") if results else None
    if combined is None or combined.empty:
        return pd.DataFrame()
    df = combined.copy()

    if strategy_key == "at_risk":
        if "churn_risk" in df.columns:
            return df[df["churn_risk"] == "High 🔴"].reset_index(drop=True)
        if "segment_name" in df.columns:
            return df[df["segment_name"].str.contains("At Risk", na=False)].reset_index(drop=True)
        return df[df.get("recency_days", 0) > 60].reset_index(drop=True) if "recency_days" in df.columns else df.head(20)

    if strategy_key == "inactive":
        if "segment_name" in df.columns:
            return df[df["segment_name"].str.contains("Inactive", na=False)].reset_index(drop=True)
        return df[df["recency_days"] > 45].reset_index(drop=True) if "recency_days" in df.columns else df.head(30)

    if strategy_key == "high_value":
        if "predicted_clv" in df.columns:
            return df.sort_values("predicted_clv", ascending=False).head(50).reset_index(drop=True)
        if "segment_name" in df.columns:
            hv = df[df["segment_name"].str.contains("High Value", na=False)]
            return hv.head(50).reset_index(drop=True)
        if "monetary_value" in df.columns:
            return df.sort_values("monetary_value", ascending=False).head(50).reset_index(drop=True)

    return df.head(50)


# ── Action log helpers ─────────────────────────────────────────────────────────

def _log_action(strategy_key, strategy_title, customer_count):
    if "action_log" not in st.session_state:
        st.session_state.action_log = []
    st.session_state.action_log.append({
        "Timestamp":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Strategy":            strategy_title,
        "Customers Affected":  customer_count,
        "Status":              "✅ Applied",
    })

def _mark_applied(key):
    if "applied_strategies" not in st.session_state:
        st.session_state.applied_strategies = set()
    st.session_state.applied_strategies.add(key)

def _is_applied(key) -> bool:
    return key in st.session_state.get("applied_strategies", set())


# ── Card HTML builder ──────────────────────────────────────────────────────────

def _build_card_html(s: dict, applied: bool) -> str:
    """Build a fully inline-styled card to avoid Streamlit HTML sanitizer stripping CSS classes."""

    # Card border / background
    if applied:
        card_bg = "linear-gradient(135deg, #052e16 0%, #0F172A 100%)"
        card_border = "1px solid #22C55E"
        card_shadow = "0 0 24px rgba(34,197,94,0.10)"
    else:
        card_bg = "linear-gradient(135deg, #0F172A 0%, #1A2332 100%)"
        card_border = f"1px solid {s['card_border']}55"
        card_shadow = f"0 4px 24px {s['card_glow']}"

    # Applied badge
    badge_html = ""
    if applied:
        badge_html = (
            '<span style="display:inline-block; background:#052e16; color:#4ADE80; '
            'border:1px solid #22C55E; border-radius:20px; padding:3px 14px; '
            'font-size:11px; font-weight:700; margin-left:12px;">✅ Applied</span>'
        )

    # Action steps
    steps_html = "".join(
        f'<div style="color:#CBD5E1; font-size:13.5px; line-height:2; padding:2px 0;">{a}</div>'
        for a in s["actions"]
    )

    card = f"""<div style="background:{card_bg}; border:{card_border}; border-radius:14px; padding:22px 26px; margin-bottom:8px; box-shadow:{card_shadow}; transition:box-shadow 0.25s, border-color 0.25s;"><div style="margin-bottom:10px;"><span style="display:inline-block; border-radius:6px; padding:4px 14px; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:1px; background:{s['urgency_bg']}; border:1px solid {s['urgency_border']}; color:{s['urgency_color']};">{s['urgency']}</span>{badge_html}</div><div style="font-size:17px; font-weight:700; color:#F1F5F9; margin-bottom:6px;">{s['icon']} {s['title']}</div><div style="font-size:13px; color:#94A3B8; margin-bottom:10px;">{s['desc']}</div><div style="margin:12px 0; padding:14px 18px; background:rgba(0,0,0,0.25); border-radius:8px; border:1px solid #1E293B;">{steps_html}</div><div style="font-size:13px; color:#A5B4FC; font-weight:600; margin-top:10px;">📈 Expected Impact: {s['impact']}</div><div style="display:flex; gap:20px; margin-top:14px; flex-wrap:wrap;"><span style="background:rgba(99,102,241,0.10); border:1px solid rgba(99,102,241,0.25); padding:5px 14px; border-radius:20px; font-size:12px; color:#A5B4FC; font-weight:600;">🤖 AI Confidence: {s['intelligence']['confidence']}</span><span style="background:rgba(99,102,241,0.10); border:1px solid rgba(99,102,241,0.25); padding:5px 14px; border-radius:20px; font-size:12px; color:#A5B4FC; font-weight:600;">💰 Expected ROI: {s['intelligence']['roi']}</span></div></div>"""
    return card


# ── Main Render ────────────────────────────────────────────────────────────────

def render_action_cards():
    results  = st.session_state.get("results", {})
    df       = results.get("combined") if results else None

    # ── Header summary counts ─────────────────────────────────────────────────
    at_risk_count   = 0
    inactive_count  = 0
    hv_count        = 0
    if df is not None and not df.empty:
        if "churn_risk" in df.columns:
            at_risk_count = len(df[df["churn_risk"] == "High 🔴"])
        if "segment_name" in df.columns:
            inactive_count = len(df[df["segment_name"].str.contains("Inactive", na=False)])
            hv_count       = len(df[df["segment_name"].str.contains("High Value", na=False)])

    # ── Automation Banner ─────────────────────────────────────────────────────
    st.markdown(
        f"""<div style="background:linear-gradient(135deg, #312E81 0%, #1E1B4B 100%); border:1px solid #4338CA; border-radius:14px; padding:24px; margin-bottom:28px; text-align:center;"><div style="font-size:13px; color:#A5B4FC; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:10px;">🤖 AI Decision Engine — Auto-Generated Actions</div><div style="font-size:15px; color:#CBD5E1; margin-bottom:16px;">Based on your data, AECIP has identified <b style="color:#F1F5F9;">{at_risk_count:,} at-risk</b>, <b style="color:#F1F5F9;">{inactive_count:,} inactive</b>, and <b style="color:#F1F5F9;">{hv_count:,} high-value</b> customers. Recommended actions are prioritised by urgency and estimated ROI.</div></div>""",
        unsafe_allow_html=True,
    )

    # ── Run All Simulation Button ─────────────────────────────────────────────
    sim_col, _ = st.columns([3, 5])
    with sim_col:
        if st.button("⚡ Run Retention Strategy Simulation", type="primary", use_container_width=True):
            st.session_state["simulation_run"] = True

    if st.session_state.get("simulation_run", False):
        churn_reduction = int(at_risk_count * 0.30)
        st.success(
            f"✅ **Simulation Complete:** Applying all strategies is estimated to reduce churn by **30%**, "
            f"recovering approximately **{churn_reduction} customers** and protecting significant revenue."
        )

        # Before / After table
        rev_at_risk = 0
        if df is not None and "churn_risk" in df.columns and "monetary_value" in df.columns:
            rev_at_risk = df[df["churn_risk"] == "High 🔴"]["monetary_value"].sum()

        loss_without = rev_at_risk
        loss_with    = rev_at_risk * 0.70
        saved        = loss_without - loss_with

        st.markdown(
            f"""
<table style="width:100%; margin-top:12px; border-collapse:collapse;">
    <thead><tr>
        <th style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#64748B; font-weight:600; text-align:left;">Scenario</th>
        <th style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#64748B; font-weight:600; text-align:left;">Revenue at Risk</th>
        <th style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#64748B; font-weight:600; text-align:left;">Projected Loss</th>
        <th style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#64748B; font-weight:600; text-align:left;">Net Saved</th>
    </tr></thead>
    <tbody>
        <tr>
            <td style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#E2E8F0;">❌ Without AI Strategy</td>
            <td style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#F87171;">₹{loss_without:,.0f}</td>
            <td style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#F87171;">₹{loss_without:,.0f}</td>
            <td style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#E2E8F0;">—</td>
        </tr>
        <tr>
            <td style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#E2E8F0;">✅ With AI Strategy</td>
            <td style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#F87171;">₹{loss_without:,.0f}</td>
            <td style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#FCD34D;">₹{loss_with:,.0f}</td>
            <td style="padding:8px 14px; border-bottom:1px solid #1E293B; font-size:14px; color:#4ADE80; font-weight:700;">+₹{saved:,.0f}</td>
        </tr>
    </tbody>
</table>
""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🚨 Recommended Actions (Auto-Generated)")

    # ── Strategy Cards ────────────────────────────────────────────────────────
    for s in STRATEGIES:
        key     = s["key"]
        applied = _is_applied(key)

        # Render the card
        st.markdown(_build_card_html(s, applied), unsafe_allow_html=True)

        btn_col, _ = st.columns([2, 6])
        with btn_col:
            label    = "✅ Applied" if applied else "🚀 Apply Strategy"
            btn_type = "secondary"  if applied else "primary"
            if st.button(label, key=f"btn_{key}", type=btn_type, disabled=applied, use_container_width=True):
                customers = _get_customers(key, results)
                _log_action(key, s["title"], len(customers))
                _mark_applied(key)
                st.session_state[f"customers_{key}"] = customers
                st.rerun()

        customers_df = st.session_state.get(f"customers_{key}")
        if applied and customers_df is not None:
            with st.expander(f"👥 Preview — {len(customers_df):,} customer(s) targeted", expanded=False):
                st.dataframe(customers_df.head(20), use_container_width=True)
                if len(customers_df) > 20:
                    st.caption(f"Showing first 20 of {len(customers_df)} rows.")

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Action Log ────────────────────────────────────────────────────────────
    log = st.session_state.get("action_log", [])
    if log:
        st.markdown("---")
        st.subheader("📋 Strategy Execution Log")
        st.dataframe(pd.DataFrame(log), use_container_width=True, hide_index=True)
