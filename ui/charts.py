"""
ui/charts.py
============
All Plotly chart rendering functions.
Receives pre-computed DataFrames from analytics/aggregations.py.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analytics.aggregations import (
    survival_by_sex,
    survival_by_pclass,
    survival_by_agegroup,
    survival_by_title,
    pivot_pclass_sex,
    fare_describe_by_pclass,
    correlation_matrix,
)

# ── Shared Layout Base ─────────────────────────────────────────────────────────
_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#CBD5E1", size=12),
    margin=dict(l=16, r=16, t=44, b=16),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.08)",
        font=dict(color="#CBD5E1"),
    ),
    title_font=dict(size=14, color="#E2E8F0", family="Inter"),
)

# Default axis styles applied via update_xaxes / update_yaxes
_XAXIS = dict(showgrid=False, zeroline=False, tickfont=dict(size=11, color="#94A3B8"), title_font=dict(size=12, color="#94A3B8"))
_YAXIS = dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False, tickfont=dict(size=11, color="#94A3B8"), title_font=dict(size=12, color="#94A3B8"))


def _apply_axes(fig, xkwargs=None, ykwargs=None):
    """Apply default axis styles + optional per-chart overrides."""
    x = {**_XAXIS, **(xkwargs or {})}
    y = {**_YAXIS, **(ykwargs or {})}
    fig.update_xaxes(**x)
    fig.update_yaxes(**y)
    return fig

_GENDER_MAP  = {"female": "#EC4899", "male": "#3B82F6"}
_PCLASS_MAP  = {1: "#7C3AED", 2: "#06B6D4", 3: "#10B981"}
_GRAD_SCALE  = [[0.0, "#1e0a4d"], [0.5, "#7C3AED"], [1.0, "#06B6D4"]]


def _empty_warning():
    st.warning("⚠️ No data matches the current filter selection. Adjust the sidebar to see results.")


# ── Tab 1: Overview ────────────────────────────────────────────────────────────

def render_overview_tab(df: pd.DataFrame) -> None:
    if df.empty:
        _empty_warning()
        return

    # ── Row 1: Sex + Pclass ────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        sex_df = survival_by_sex(df)
        sex_df["pct"] = (sex_df["Survival Rate"] * 100).round(1)

        fig = px.bar(
            sex_df,
            x="Sex", y="pct",
            color="Sex",
            color_discrete_map=_GENDER_MAP,
            text=sex_df["pct"].astype(str) + "%",
            title="Survival Rate by Gender",
            labels={"pct": "Survival Rate (%)", "Sex": "Gender"},
        )
        fig.update_traces(
            textposition="outside",
            textfont=dict(color="#E2E8F0", size=13, family="Inter"),
            width=0.45,
            marker=dict(line=dict(width=0)),
        )
        fig.update_layout(
            **_BASE,
            showlegend=False,
            yaxis_range=[0, 105],
            yaxis_title="Survival Rate (%)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        pc_df = survival_by_pclass(df)
        pc_df["pct"]   = (pc_df["Survival Rate"] * 100).round(1)
        pc_df["label"] = pc_df["Pclass"].map({1: "1st Class", 2: "2nd Class", 3: "3rd Class"})
        pc_df["color"] = pc_df["Pclass"].map(_PCLASS_MAP)

        fig2 = px.bar(
            pc_df,
            x="label", y="pct",
            color="Pclass",
            color_discrete_map=_PCLASS_MAP,
            text=pc_df["pct"].astype(str) + "%",
            title="Survival Rate by Passenger Class",
            labels={"pct": "Survival Rate (%)", "label": "Class"},
        )
        fig2.update_traces(
            textposition="outside",
            textfont=dict(color="#E2E8F0", size=13, family="Inter"),
            width=0.45,
            marker=dict(line=dict(width=0)),
        )
        fig2.update_layout(
            **_BASE,
            showlegend=False,
            yaxis_range=[0, 105],
            yaxis_title="Survival Rate (%)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Pivot Heatmap ──────────────────────────────────────────────────────────
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 🔥 Survival Rate Heatmap — Pclass × Sex")

    pivot = pivot_pclass_sex(df)

    if not pivot.empty:
        z_pct     = (pivot.values * 100).round(1).tolist()
        x_labels  = [c.title() for c in pivot.columns.tolist()]
        y_labels  = [f"Class {r}" for r in pivot.index.tolist()]

        hmap = go.Figure(go.Heatmap(
            z=z_pct,
            x=x_labels,
            y=y_labels,
            colorscale=_GRAD_SCALE,
            zmin=0, zmax=100,
            text=[[f"{v}%" for v in row] for row in z_pct],
            texttemplate="%{text}",
            textfont=dict(size=20, color="white", family="Inter"),
            hovertemplate="%{y} | %{x}: <b>%{z}%</b><extra></extra>",
            showscale=True,
            colorbar=dict(
                title=dict(text="Survival %", font=dict(color="#94A3B8", size=11)),
                ticksuffix="%",
                tickfont=dict(color="#94A3B8"),
                thickness=14,
                len=0.85,
            ),
        ))
        # Use fig.layout.update() to avoid keyword conflicts from **_BASE spread
        hmap.layout.update(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#CBD5E1", size=12),
            margin=dict(l=16, r=16, t=10, b=16),
            height=330,
            title="",
        )
        hmap.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=14, color="#E2E8F0"))
        hmap.update_yaxes(showgrid=False, zeroline=False, tickfont=dict(size=13, color="#E2E8F0"))
        st.plotly_chart(hmap, use_container_width=True)

    # Raw pivot table in expander
    with st.expander("📋 View Raw Pivot Table Values"):
        display = (pivot * 100).round(1)
        display.index = display.index.map({1: "1st Class", 2: "2nd Class", 3: "3rd Class"})
        display.columns = [c.title() for c in display.columns]
        st.dataframe(
            display.style
                   .background_gradient(cmap="RdYlGn", vmin=0, vmax=100)
                   .format("{:.1f}%"),
            use_container_width=True,
        )


# ── Tab 2: Deep Analysis ───────────────────────────────────────────────────────

def render_deep_analysis_tab(df: pd.DataFrame) -> None:
    if df.empty:
        _empty_warning()
        return

    col1, col2 = st.columns(2)

    # AgeGroup survival
    with col1:
        age_df = survival_by_agegroup(df)
        age_df["pct"] = (age_df["Survival Rate"] * 100).round(1)

        fig = px.bar(
            age_df,
            x="AgeGroup", y="pct",
            color="pct",
            color_continuous_scale=_GRAD_SCALE,
            text=age_df["pct"].astype(str) + "%",
            title="Survival Rate by Age Group",
            labels={"pct": "Survival Rate (%)", "AgeGroup": "Age Group"},
        )
        fig.update_traces(
            textposition="outside",
            textfont=dict(color="#E2E8F0", size=13),
            width=0.5,
            marker=dict(line=dict(width=0)),
        )
        fig.update_layout(
            **_BASE,
            coloraxis_showscale=False,
            yaxis_range=[0, 105],
            yaxis_title="Survival Rate (%)",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Title survival (horizontal bar)
    with col2:
        title_df = survival_by_title(df).head(8).copy()
        title_df["pct"] = (title_df["Survival Rate"] * 100).round(1)

        fig2 = px.bar(
            title_df,
            x="pct", y="Title",
            orientation="h",
            color="pct",
            color_continuous_scale=_GRAD_SCALE,
            text=title_df["pct"].astype(str) + "%",
            title="Survival Rate by Title (Top 8)",
            labels={"pct": "Survival Rate (%)", "Title": ""},
        )
        fig2.update_traces(
            textposition="outside",
            textfont=dict(color="#E2E8F0", size=12),
            marker=dict(line=dict(width=0)),
        )
        fig2.update_layout(
            **_BASE,
            coloraxis_showscale=False,
            xaxis_range=[0, 115],
            xaxis_title="Survival Rate (%)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Expander: Fare Distribution ────────────────────────────────────────────
    with st.expander("📈 Fare Distribution by Passenger Class"):
        st.markdown("**Descriptive Statistics — Fare**")
        fare_stats = fare_describe_by_pclass(df)
        fare_stats.index = fare_stats.index.map({1: "1st Class", 2: "2nd Class", 3: "3rd Class"})
        st.dataframe(
            fare_stats.style.background_gradient(cmap="Blues").format("{:.2f}"),
            use_container_width=True,
        )

        box_fig = px.box(
            df, x="Pclass", y="Fare",
            color="Pclass",
            color_discrete_map=_PCLASS_MAP,
            title="Fare Distribution by Class (Box Plot)",
            labels={"Pclass": "Class", "Fare": "Fare (£)"},
            points="outliers",
        )
        box_fig.update_layout(
            **_BASE,
            showlegend=False,
            yaxis_title="Fare (£)",
        )
        box_fig.update_xaxes(
            tickvals=[1, 2, 3],
            ticktext=["1st Class", "2nd Class", "3rd Class"],
        )
        st.plotly_chart(box_fig, use_container_width=True)

    # ── Expander: Correlation Matrix ───────────────────────────────────────────
    with st.expander("🔢 Feature Correlation Matrix"):
        corr = correlation_matrix(df)
        corr_fig = px.imshow(
            corr,
            color_continuous_scale=[[0, "#06B6D4"], [0.5, "#1a0a3d"], [1, "#7C3AED"]],
            zmin=-1, zmax=1,
            text_auto=".2f",
            title="Pearson Correlation Heatmap (Numeric Features)",
        )
        corr_fig.layout.update(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#CBD5E1", size=12),
            margin=dict(l=16, r=16, t=44, b=16),
            height=500,
            title_font=dict(size=14, color="#E2E8F0", family="Inter"),
            coloraxis_colorbar=dict(
                title=dict(text="r", font=dict(color="#94A3B8")),
                tickfont=dict(color="#94A3B8"),
                thickness=14,
            ),
        )
        corr_fig.update_traces(textfont=dict(size=11, color="white"))
        st.plotly_chart(corr_fig, use_container_width=True)

        st.markdown(
            """
            > **How to read this:** Values close to **+1** mean strong positive correlation;
            values near **-1** mean strong inverse relationship.
            `Pclass` is negative with `Fare` because higher class = lower number = higher fare.
            """,
        )
