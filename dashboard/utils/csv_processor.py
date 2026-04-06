"""
csv_processor.py
Backend utility for the AECIP CSV Analysis page.
Validates uploaded data, maps columns, and routes to the correct models.
"""

import sys
import os
import warnings
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

warnings.filterwarnings("ignore")

# ── helpers ─────────────────────────────────────────────────────────────────

SEGMENT_LABELS = {
    0: "High Value ⭐",
    1: "Regular 🔁",
    2: "Inactive 😴",
    3: "At Risk ⚠️",
}

REQUIRED_FOR_CHURN = ["recency_days", "purchase_frequency"]
REQUIRED_FOR_CLV   = ["purchase_frequency", "monetary_value"]
REQUIRED_FOR_SEG   = ["recency_days", "purchase_frequency", "monetary_value"]


# ── validation ───────────────────────────────────────────────────────────────

def validate(df: pd.DataFrame, column_map: dict, analyses: list) -> list[str]:
    """
    Returns a list of warning strings.  Empty list means all good.
    """
    warnings_out = []

    if df.empty or len(df) == 0:
        return ["Uploaded CSV is empty. Please upload a file with at least one data row."]

    if len(df) < 5:
        warnings_out.append(
            f"⚠️ Only {len(df)} rows found. Results may be unreliable. "
            "It is recommended to have at least 5 rows."
        )

    mapped_cols = set(column_map.values())

    def _check_required(needed, task_name):
        missing = [c for c in needed if c not in mapped_cols]
        if missing:
            warnings_out.append(
                f"⚠️ **{task_name}** requires columns: `{'`, `'.join(missing)}` "
                "— please map them or deselect this analysis."
            )
        return not missing

    if "Customer Loss Prediction" in analyses:
        _check_required(REQUIRED_FOR_CHURN, "Customer Loss Prediction")
    if "CLV Prediction" in analyses:
        _check_required(REQUIRED_FOR_CLV, "CLV Prediction")
    if "Customer Segmentation" in analyses:
        _check_required(REQUIRED_FOR_SEG, "Customer Segmentation")

    return warnings_out


# ── column extraction ─────────────────────────────────────────────────────────

def _extract_mapped(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    """Rename user columns to AECIP standard names, coerce types, drop bad rows."""
    # column_map = {aecip_name: user_col}  e.g. {"recency_days": "Recency"}
    renamed = {}
    for aecip_name, user_col in column_map.items():
        if user_col and user_col in df.columns:
            renamed[user_col] = aecip_name

    out = df.rename(columns=renamed)

    # Coerce numeric columns
    numeric_cols = ["recency_days", "purchase_frequency", "monetary_value", "age"]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    return out


# ── churn ─────────────────────────────────────────────────────────────────────

def _run_churn(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lightweight rule-based churn scoring that works without a trained model.
    Also attempts to load the saved XGB model if it exists.
    """
    result = df[["customer_id"]].copy() if "customer_id" in df.columns else pd.DataFrame(index=df.index)

    # Try the trained model first
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from models.churn_model import ChurnModel
        cm = ChurnModel()
        needed = ["recency_days", "purchase_frequency"]
        X = df[[c for c in needed if c in df.columns]].fillna(df.mean(numeric_only=True))
        probs = cm.predict_proba(X)
        result["churn_probability"] = (probs * 100).round(1)
        result["churn_risk"] = pd.cut(
            result["churn_probability"],
            bins=[-1, 30, 60, 101],
            labels=["Low 🟢", "Medium 🟡", "High 🔴"],
        )
        result["_model_used"] = "XGBoost (trained)"
    except Exception:
        # Fallback: rule-based sigmoid approximation
        rec  = df["recency_days"].fillna(df["recency_days"].median()) if "recency_days" in df.columns else 30
        freq = df["purchase_frequency"].fillna(df["purchase_frequency"].median()) if "purchase_frequency" in df.columns else 5
        score = 1 / (1 + np.exp(-(rec / 30 - freq / 3)))
        result["churn_probability"] = (score * 100).round(1)
        result["churn_risk"] = pd.cut(
            result["churn_probability"],
            bins=[-1, 30, 60, 101],
            labels=["Low 🟢", "Medium 🟡", "High 🔴"],
        )
        result["_model_used"] = "Rule-based (fallback)"

    return result


# ── CLV ───────────────────────────────────────────────────────────────────────

def _run_clv(df: pd.DataFrame) -> pd.DataFrame:
    result = df[["customer_id"]].copy() if "customer_id" in df.columns else pd.DataFrame(index=df.index)

    try:
        from models.clv_model import CLVModel
        cm = CLVModel()
        needed = ["purchase_frequency", "monetary_value"]
        X = df[[c for c in needed if c in df.columns]].fillna(df.mean(numeric_only=True))
        preds = cm.predict(X)
        result["predicted_clv"] = preds.round(2)
        result["_model_used"] = "GradientBoosting (trained)"
    except Exception:
        # Fallback: RFM-derived heuristic CLV
        freq = df["purchase_frequency"].fillna(5) if "purchase_frequency" in df.columns else 5
        mon  = df["monetary_value"].fillna(500)   if "monetary_value"     in df.columns else 500
        result["predicted_clv"] = (freq * mon * 1.5).round(2)
        result["_model_used"] = "Heuristic (fallback)"

    return result


# ── segmentation ──────────────────────────────────────────────────────────────

def _run_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    result = df[["customer_id"]].copy() if "customer_id" in df.columns else pd.DataFrame(index=df.index)

    feature_cols = [c for c in ["recency_days", "purchase_frequency", "monetary_value"] if c in df.columns]
    X = df[feature_cols].fillna(df[feature_cols].mean())

    if X.shape[0] < 4:
        result["segment_id"]   = 0
        result["segment_name"] = SEGMENT_LABELS.get(0, "Cluster 0")
        return result

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    # Auto-select best k (2–5)
    best_k, best_score = 3, -1
    for k in range(2, min(6, len(X))):
        labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(Xs)
        try:
            s = silhouette_score(Xs, labels)
            if s > best_score:
                best_k, best_score = k, s
        except Exception:
            pass

    km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    labels = km.fit_predict(Xs)

    # Map cluster centres to meaningful labels based on monetary value
    centers_df = pd.DataFrame(km.cluster_centers_, columns=feature_cols)
    if "monetary_value" in centers_df.columns:
        order = centers_df["monetary_value"].argsort().argsort()
    else:
        order = pd.Series(range(best_k))

    label_map = {}
    tier_names = ["Inactive 😴", "Regular 🔁", "High Value ⭐", "At Risk ⚠️"]
    for i, rank in enumerate(order):
        label_map[i] = tier_names[int(rank) % len(tier_names)]

    result["segment_id"]   = labels
    result["segment_name"] = [label_map[l] for l in labels]
    result["silhouette"]   = round(best_score, 4)
    return result


# ── main entry point ──────────────────────────────────────────────────────────

def process(
    df: pd.DataFrame,
    column_map: dict,
    analyses: list,
) -> dict:
    """
    Parameters
    ----------
    df          : Raw uploaded DataFrame
    column_map  : {aecip_field: user_column}  e.g. {"recency_days": "days_since_purchase"}
    analyses    : list of strings from ["Customer Loss Prediction","CLV Prediction","Customer Segmentation"]

    Returns
    -------
    dict with keys:
        "warnings" : list[str]
        "summary"  : dict  (high-level KPIs)
        "churn"    : pd.DataFrame | None
        "clv"      : pd.DataFrame | None
        "segments" : pd.DataFrame | None
        "combined" : pd.DataFrame  (merged output for download)
    """
    warnings_list = validate(df, column_map, analyses)

    mapped = _extract_mapped(df.copy(), column_map)

    # Add synthetic customer_id if not mapped
    if "customer_id" not in mapped.columns:
        mapped["customer_id"] = range(1, len(mapped) + 1)

    results = {
        "warnings": warnings_list,
        "summary":  {},
        "churn":    None,
        "clv":      None,
        "segments": None,
        "combined": mapped.copy(),
    }

    if "Customer Loss Prediction" in analyses and all(c in mapped.columns for c in REQUIRED_FOR_CHURN):
        churn_df = _run_churn(mapped)
        results["churn"] = churn_df
        results["combined"] = results["combined"].merge(
            churn_df.drop(columns=["_model_used"], errors="ignore"),
            on="customer_id", how="left"
        )
        pct_high = (churn_df["churn_risk"] == "High 🔴").mean() * 100
        results["summary"]["At-Risk Customers"] = f"{pct_high:.1f}%"

    if "CLV Prediction" in analyses and all(c in mapped.columns for c in REQUIRED_FOR_CLV):
        clv_df = _run_clv(mapped)
        results["clv"] = clv_df
        results["combined"] = results["combined"].merge(
            clv_df.drop(columns=["_model_used"], errors="ignore"),
            on="customer_id", how="left"
        )
        avg_clv = clv_df["predicted_clv"].mean()
        results["summary"]["Avg Predicted CLV"] = f"₹{avg_clv:,.0f}"

    if "Customer Segmentation" in analyses and all(c in mapped.columns for c in REQUIRED_FOR_SEG):
        seg_df = _run_segmentation(mapped)
        results["segments"] = seg_df
        results["combined"] = results["combined"].merge(
            seg_df[["customer_id", "segment_name"]],
            on="customer_id", how="left"
        )
        top_seg = seg_df["segment_name"].value_counts().idxmax() if len(seg_df) else "—"
        results["summary"]["Dominant Segment"] = top_seg

    results["summary"]["Total Customers Processed"] = f"{len(df):,}"

    return results
