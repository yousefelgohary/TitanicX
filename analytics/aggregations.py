"""
analytics/aggregations.py
=========================
All aggregation functions and the AI insights engine.
Pure pandas — zero Streamlit imports.
"""

import pandas as pd
from typing import List, Dict, Any


# ── Survival Aggregations ─────────────────────────────────────────────────────

def survival_by_sex(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Sex", observed=True)["Survived"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "Survival Rate", "count": "Count"})
        .reset_index()
    )


def survival_by_pclass(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Pclass", observed=True)["Survived"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "Survival Rate", "count": "Count"})
        .reset_index()
    )


def survival_by_agegroup(df: pd.DataFrame) -> pd.DataFrame:
    order = ["Child", "Teen", "Adult", "Senior"]
    result = (
        df.groupby("AgeGroup", observed=True)["Survived"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "Survival Rate", "count": "Count"})
        .reset_index()
    )
    result["AgeGroup"] = pd.Categorical(result["AgeGroup"], categories=order, ordered=True)
    return result.sort_values("AgeGroup").reset_index(drop=True)


def survival_by_title(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Title", observed=True)["Survived"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "Survival Rate", "count": "Count"})
        .sort_values("Survival Rate", ascending=False)
        .reset_index()
    )


def pivot_pclass_sex(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot table: survival rate with Pclass as rows, Sex as columns."""
    return df.pivot_table(
        values="Survived",
        index="Pclass",
        columns="Sex",
        aggfunc="mean"
    ).round(3)


def fare_describe_by_pclass(df: pd.DataFrame) -> pd.DataFrame:
    """Descriptive statistics of Fare grouped by Pclass."""
    return df.groupby("Pclass")["Fare"].describe().round(2)


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pearson correlation matrix for numeric features."""
    numeric_cols = [c for c in ["Survived", "Pclass", "Age", "SibSp", "Parch", "Fare", "has_cabin"]
                    if c in df.columns]
    return df[numeric_cols].corr().round(3)


# ── AI Insights Engine ────────────────────────────────────────────────────────

_POLICY_NOTE = "Aligns with documented 'Women and children first' evacuation policy (historical consensus)."
_CLASS_NOTE  = "Higher deck position = earlier, privileged lifeboat access (structural advantage)."
_MALE3_NOTE  = "3rd-class men faced the worst odds: lowest class + farthest from lifeboats + male."


def _confidence_score(n: int, aligns_with_policy: bool) -> int:
    """
    Confidence formula:
      sample_score = min(n / 50, 1.0) * 70    → up to 70 pts from sample size
      policy_bonus = 30 if segment aligns with known evacuation bias, else 0
      total        = sample_score + policy_bonus  (capped at 100)
    """
    sample_score = min(n / 50.0, 1.0) * 70
    policy_bonus = 30 if aligns_with_policy else 0
    return min(100, int(round(sample_score + policy_bonus)))


def _badge_info(score: int):
    if score >= 85:
        return "HIGH",     "badge-high",   "🟢"
    elif score >= 60:
        return "MODERATE", "badge-medium", "🟡"
    else:
        return "LOW",      "badge-low",    "🔴"


def insights_engine(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Dynamically compute confidence-scored insight cards for each (Pclass × Sex) segment.
    All statistics are derived from `df` — nothing is hardcoded.
    Returns a sorted list of dicts ready for the UI to render.
    """
    if df.empty:
        return []

    agg = (
        df.groupby(["Pclass", "Sex"], observed=True)["Survived"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "rate", "count": "n"})
    )

    insights: List[Dict[str, Any]] = []

    for _, row in agg.iterrows():
        pclass    = int(row["Pclass"])
        sex       = str(row["Sex"])
        rate      = float(row["rate"])
        n         = int(row["n"])
        is_female = sex == "female"

        # Does this segment align with the known evacuation bias?
        aligns = is_female or pclass == 1

        conf               = _confidence_score(n, aligns)
        level, css, icon   = _badge_info(conf)
        class_label        = {1: "1st", 2: "2nd", 3: "3rd"}.get(pclass, str(pclass))
        sex_label          = "Women" if is_female else "Men"
        emoji              = "👩" if is_female else "👨"

        # Build justification list
        reasons: List[str] = []
        if n >= 50:
            reasons.append(f"Large sample (n={n}) → high statistical reliability.")
        elif n >= 20:
            reasons.append(f"Moderate sample (n={n}) → conclusions are directionally reliable.")
        else:
            reasons.append(f"Small sample (n={n}) → interpret with caution; wide confidence interval.")

        if is_female:
            reasons.append(_POLICY_NOTE)
        if pclass == 1:
            reasons.append(_CLASS_NOTE)
        if not is_female and pclass == 3:
            reasons.append(_MALE3_NOTE)

        insights.append({
            "title"     : f"{emoji} {class_label} Class — {sex_label}",
            "rate"      : rate,
            "n"         : n,
            "confidence": conf,
            "level"     : level,
            "css_class" : css,
            "icon"      : icon,
            "reasons"   : reasons,
            "pclass"    : pclass,
            "sex"       : sex,
        })

    # Sort: highest survival rate first
    insights.sort(key=lambda x: x["rate"], reverse=True)
    return insights
