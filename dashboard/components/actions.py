"""
actions.py
Fully functional Recommended Actions component for the AECIP Executive Dashboard.
Features:
  - Real customer filtering per strategy
  - Action logging with timestamps
  - "Applied" green tick state per strategy
  - Removed all CSV export functions as requested.
"""

import streamlit as st
import pandas as pd
from datetime import datetime


# ── Strategy definitions ───────────────────────────────────────────────────────

STRATEGIES = [
    {
        "key":     "at_risk",
        "icon":    "🎁",
        "title":   "Offer discount to at-risk customers",
        "desc":    "Target customers with high customer loss risk with a personalised discount to retain them.",
        "impact":  "Recover ~₹30,000/month",
        "color":   "#EF4444",
    },
    {
        "key":     "inactive",
        "icon":    "📧",
        "title":   "Send reminder emails to inactive users",
        "desc":    "Re-engage customers who have not interacted recently with a targeted email campaign.",
        "impact":  "Re-engage 400 customers",
        "color":   "#F59E0B",
    },
    {
        "key":     "high_value",
        "icon":    "⭐",
        "title":   "Reward top 50 high-value customers",
        "desc":    "Recognise and reward your best customers with loyalty perks to strengthen retention.",
        "impact":  "Increase loyalty by 25%",
        "color":   "#6366F1",
    },
]


# ── Customer filtering logic ────────────────────────────────────────────────────

def _get_customers(strategy_key: str, results: dict) -> pd.DataFrame:
    """Return the relevant subset of customers for each strategy."""
    combined = results.get("combined") if results else None
    if combined is None or combined.empty:
        return pd.DataFrame()

    df = combined.copy()

    if strategy_key == "at_risk":
        if "churn_risk" in df.columns:
            filtered = df[df["churn_risk"] == "High 🔴"]
        elif "segment_name" in df.columns:
            filtered = df[df["segment_name"].str.contains("At Risk", na=False)]
        elif "recency_days" in df.columns:
            filtered = df[df["recency_days"] > 60]
        else:
            filtered = df.head(20)
        return filtered.reset_index(drop=True)

    elif strategy_key == "inactive":
        if "segment_name" in df.columns:
            filtered = df[df["segment_name"].str.contains("Inactive", na=False)]
        elif "recency_days" in df.columns:
            filtered = df[df["recency_days"] > 45]
        else:
            filtered = df.head(30)
        return filtered.reset_index(drop=True)

    elif strategy_key == "high_value":
        if "predicted_clv" in df.columns:
            filtered = df.sort_values("predicted_clv", ascending=False).head(50)
        elif "segment_name" in df.columns:
            hv = df[df["segment_name"].str.contains("High Value", na=False)]
            filtered = hv.head(50)
        elif "monetary_value" in df.columns:
            filtered = df.sort_values("monetary_value", ascending=False).head(50)
        else:
            filtered = df.head(50)
        return filtered.reset_index(drop=True)

    return df.head(50)


# ── Action log helpers ──────────────────────────────────────────────────────────

def _log_action(strategy_key: str, strategy_title: str, customer_count: int):
    if "action_log" not in st.session_state:
        st.session_state.action_log = []
    st.session_state.action_log.append({
        "Timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Strategy":        strategy_title,
        "Customers Affected": customer_count,
        "Status":          "✅ Applied",
    })


def _mark_applied(strategy_key: str):
    if "applied_strategies" not in st.session_state:
        st.session_state.applied_strategies = set()
    st.session_state.applied_strategies.add(strategy_key)


def _is_applied(strategy_key: str) -> bool:
    return strategy_key in st.session_state.get("applied_strategies", set())


# ── CSS ────────────────────────────────────────────────────────────────────────

def _inject_css():
    st.markdown("""
    <style>
    .action-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
        transition: box-shadow 0.25s;
    }
    .action-card:hover {
        box-shadow: 0 6px 28px rgba(99,102,241,0.18);
    }
    .action-card.applied {
        border-color: #22C55E;
        background: linear-gradient(135deg, #052e16 0%, #0F172A 100%);
    }
    .action-title {
        font-size: 16px;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 4px;
    }
    .action-desc {
        font-size: 13px;
        color: #94A3B8;
        margin-bottom: 6px;
        line-height: 1.5;
    }
    .action-impact {
        font-size: 13px;
        font-weight: 600;
        color: #A5B4FC;
    }
    .applied-badge {
        display: inline-block;
        background: #052e16;
        color: #4ADE80;
        border: 1px solid #22C55E;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


# ── Main render ─────────────────────────────────────────────────────────────────

def render_action_cards():
    _inject_css()

    results = st.session_state.get("results", {})

    for s in STRATEGIES:
        key        = s["key"]
        applied    = _is_applied(key)
        card_class = "action-card applied" if applied else "action-card"
        badge      = '<span class="applied-badge">✅ Applied</span>' if applied else ""

        # ── Card header ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="{card_class}">
            <div class="action-title">{s['icon']} {s['title']}{badge}</div>
            <div class="action-desc">{s['desc']}</div>
            <div class="action-impact">📈 Impact: {s['impact']}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Button row ───────────────────────────────────────────────────────
        btn_col, _ = st.columns([2, 6])

        with btn_col:
            btn_label = "✅ Applied" if applied else "🚀 Apply Strategy"
            btn_type  = "secondary" if applied else "primary"
            if st.button(btn_label, key=f"btn_{key}", type=btn_type, disabled=applied, use_container_width=True):
                customers = _get_customers(key, results)
                _log_action(key, s["title"], len(customers))
                _mark_applied(key)
                st.session_state[f"customers_{key}"] = customers
                st.rerun()

        customers_df = st.session_state.get(f"customers_{key}")

        # ── Preview ───────────────────────────────────────────────────────────
        if applied and customers_df is not None:
            count = len(customers_df)
            with st.expander(f"👥 Preview — {count} customer(s) targeted", expanded=False):
                st.dataframe(customers_df.head(20), use_container_width=True)
                if count > 20:
                    st.caption(f"Showing first 20 of {count} rows.")

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Action Log ───────────────────────────────────────────────────────────
    log = st.session_state.get("action_log", [])
    if log:
        st.markdown("---")
        st.subheader("📋 Action Log")
        log_df = pd.DataFrame(log)
        st.dataframe(log_df, use_container_width=True, hide_index=True)
