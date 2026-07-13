import streamlit as st
import pandas as pd
from analytics.aggregations import insights_engine


# ── Tiny single-line HTML helpers (no indentation = no Markdown code-block issue)
def _badge(css_class: str, label: str) -> str:
    return f'<span class="{css_class}" style="font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:999px;">{label}</span>'

def _grad_text(text: str, size: str = "2rem") -> str:
    return (
        f'<p style="font-size:{size};font-weight:800;margin:0;line-height:1.1;'
        f'background:linear-gradient(135deg,#a78bfa,#38bdf8);'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        f'background-clip:text;">{text}</p>'
    )

def _small(text: str, color: str = "rgba(255,255,255,0.4)") -> str:
    return f'<p style="font-size:0.76rem;color:{color};margin:0.1rem 0;">{text}</p>'

def _section_title(text: str) -> str:
    return (
        f'<p style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:rgba(255,255,255,0.35);margin:0.6rem 0 0.3rem;">'
        f'{text}</p>'
    )


def render_insights_tab(df: pd.DataFrame) -> None:
    """
    AI Insights tab — uses native Streamlit components to avoid
    Markdown-indentation rendering issues with unsafe_allow_html.
    """

    # ── Page Header ────────────────────────────────────────────────────────────
    st.markdown("### 🤖 AI Insights & Scouting Report")
    st.caption(
        "Survival probabilities auto-generated from filtered data. "
        "Confidence accounts for **sample size** and alignment with the "
        "historical **'Women and children first'** evacuation policy. "
        "All values computed live — nothing is hardcoded."
    )

    if df.empty:
        st.warning("No data matches the current filters. Adjust the sidebar.")
        return

    insights = insights_engine(df)

    if not insights:
        st.info("Not enough segments to generate insights for the current filter.")
        return

    # ── Legend ─────────────────────────────────────────────────────────────────
    l1, l2, l3, _ = st.columns([1.1, 1.4, 1.0, 4])
    with l1:
        st.markdown(_badge("badge-high", "🟢 HIGH ≥85%"), unsafe_allow_html=True)
    with l2:
        st.markdown(_badge("badge-medium", "🟡 MODERATE 60–84%"), unsafe_allow_html=True)
    with l3:
        st.markdown(_badge("badge-low", "🔴 LOW &lt;60%"), unsafe_allow_html=True)

    st.markdown('<div class="fancy-divider" style="margin:0.8rem 0;"></div>', unsafe_allow_html=True)

    # ── Cards ─────────────────────────────────────────────────────────────────
    cols = st.columns(2)

    for idx, ins in enumerate(insights):
        col = cols[idx % 2]
        with col:
            # Card wrapper via native container
            with st.container(border=True):

                # ① Title + badge
                t_col, b_col = st.columns([3, 1])
                with t_col:
                    st.markdown(f"**{ins['title']}**")
                with b_col:
                    st.markdown(
                        _badge(ins["css_class"], ins["level"]),
                        unsafe_allow_html=True,
                    )

                # ② Big survival rate (gradient text — single line, no indentation issue)
                st.markdown(_grad_text(f"{ins['rate'] * 100:.1f}%"), unsafe_allow_html=True)

                # ③ Sample info
                st.markdown(
                    _small(f"Survival Rate &nbsp;·&nbsp; n = <strong style='color:rgba(255,255,255,0.65);'>{ins['n']:,}</strong> passengers"),
                    unsafe_allow_html=True,
                )

                st.markdown("")  # spacer

                # ④ Confidence label
                conf_col1, conf_col2 = st.columns([2, 1])
                with conf_col1:
                    st.markdown(_small("Confidence Score:"), unsafe_allow_html=True)
                with conf_col2:
                    st.markdown(
                        f'<p style="font-size:0.9rem;font-weight:700;color:#E2E8F0;margin:0;text-align:right;">{ins["confidence"]}%</p>',
                        unsafe_allow_html=True,
                    )

                # ⑤ Confidence bar (native st.progress — always works)
                st.progress(ins["confidence"] / 100)

                # ⑥ Reasoning (native st.expander — always works)
                with st.expander("📎 Confidence Reasoning"):
                    for reason in ins["reasons"]:
                        st.markdown(f"- {reason}")

    # ── Summary Table ──────────────────────────────────────────────────────────
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 📊 Segment Summary")

    rows = [
        {
            "Segment":       ins["title"],
            "Survival Rate": f"{ins['rate'] * 100:.1f}%",
            "Sample (n)":    f"{ins['n']:,}",
            "Confidence":    f"{ins['confidence']}%",
            "Level":         ins["level"],
        }
        for ins in insights
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Key Takeaway ───────────────────────────────────────────────────────────
    if len(insights) >= 2:
        top    = insights[0]
        bottom = insights[-1]
        gap    = (top["rate"] - bottom["rate"]) * 100

        st.info(
            f"💡 **Key Takeaway** — "
            f"Highest-survival segment: **{top['title']}** at **{top['rate']*100:.1f}%** · "
            f"Lowest: **{bottom['title']}** at **{bottom['rate']*100:.1f}%** · "
            f"Gap = **{gap:.1f} percentage points** driven by gender bias and class-based deck access."
        )
