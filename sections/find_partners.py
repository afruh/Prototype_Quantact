"""
sections/find_partners.py
──────────────────────────
Page "Find My Partners" — NLP mode only.

NLPMatcher provides real database results with semantic scoring.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

# ── NLP engine import ────────────────────────────────────────────────────────
from nlp_matcher import NLPMatcher

# ── Card builder from ecosystem_explorer ─────────────────────────────────────
try:
    from sections.ecosystem_explorer import _build_entity_card
    _CARD_IMPORT_OK = True
except ImportError:
    _CARD_IMPORT_OK = False

from database import col as db_col


# ════════════════════════════════════════════════════════════════════════════════
#  SHARED HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _score_class(score: int) -> str:
    if score >= 88: return "match-score match-score-high"
    if score >= 72: return "match-score match-score-mid"
    return "match-score match-score-low"


def _tags_html(tags: list) -> str:
    return " ".join(f'<span class="tag">{t}</span>' for t in tags)


def _section_header(icon: str, icon_cls: str, title: str, count: int) -> str:
    return (
        f'<div class="result-section-header">'
        f'<div class="result-section-icon {icon_cls}">{icon}</div>'
        f'<h3>{title}</h3>'
        f'<span class="result-section-count">{count}</span>'
        f'</div>'
    )


# ════════════════════════════════════════════════════════════════════════════════
#  NLP MODE — real database results
# ════════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def _load_matcher_cached():
    """Load NLPMatcher once for the entire Streamlit session."""
    from database import load_data
    from nlp_matcher import NLPMatcher
    df = load_data()
    return NLPMatcher(df)


def _show_nlp_refinement(explanation: dict) -> None:
    """Display the 'Consultant Parser' box with the real detected filters."""
    lines: list[tuple[str, str]] = []

    if explanation.get("entity_types"):
        lines.append(("Detected types", ", ".join(explanation["entity_types"])))
    if explanation.get("tags"):
        lines.append(("Extracted tags", ", ".join(explanation["tags"])))
    if explanation.get("quantum_fields"):
        lines.append(("Quantum fields", ", ".join(explanation["quantum_fields"])))
    if explanation.get("trl"):
        lines.append(("Inferred TRL", ", ".join(explanation["trl"])))
    if explanation.get("collab"):
        lines.append(("Collaboration", "Open to collaboration"))
    if explanation.get("country"):
        lines.append(("Region", ", ".join(explanation["country"])))

    mode_label = (
        f'Semantic NLP · model `{explanation["model"]}`'
        if explanation["mode"] == "semantic"
        else "Keyword matching (install sentence-transformers for semantic mode)"
    )
    lines.append(("Method", mode_label))

    if explanation.get("relaxed"):
        lines.append(("ℹ️ Note", "Filters relaxed — few strict matches; semantic results used instead"))

    st.markdown(
        '<div class="refinement-box">'
        "<strong>🧠 NLP Parser · Query analysis</strong><br><br>"
        + "".join(
            f'<span style="color:var(--t4);font-size:0.82rem">{k}&nbsp;&nbsp;</span>'
            f'<span style="color:var(--t2);font-size:0.88rem">{v}</span><br>'
            for k, v in lines
        )
        + "</div>",
        unsafe_allow_html=True,
    )


def _icon_for_type(entity_type: str) -> tuple[str, str]:
    """Return (emoji, css_class) for a given entity type string."""
    t = entity_type.lower()
    if "acad" in t or "research" in t or "univers" in t:
        return "🔬", "icon-research"
    if "start" in t or "spin" in t:
        return "🚀", "icon-startup"
    if "facil" in t or "fund" in t or "invest" in t:
        return "🤝", "icon-facil"
    return "🏢", "icon-research"


def _nlp_score_badge(score: int) -> str:
    css = _score_class(score)
    return f'<span class="{css}">★ {score}%</span>'


def _show_nlp_results(
    result_df: pd.DataFrame,
    filters: dict,
    explanation: dict,
    query: str,
) -> None:
    """Display real database results with NLP scores, grouped by entity type."""

    _show_nlp_refinement(explanation)

    if result_df.empty:
        st.warning(
            "No results found for this query. "
            "Try broader terms or switch to Explore Ecosystem."
        )
        if st.button("🌐 Open Explore Ecosystem", key="nlp_goto_explore"):
            st.session_state.page = "Explore Ecosystem"
            st.rerun()
        return

    # Summary
    type_col = db_col("entity_type")
    n = len(result_df)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:8px 0 24px">'
        f'<span style="color:var(--t4);font-size:0.88rem">Results ·</span>'
        f'<span style="color:var(--ok);font-size:0.88rem;font-weight:600">'
        f"{n} matching entities from the database"
        f"</span></div>",
        unsafe_allow_html=True,
    )

    # Group by entity type
    if type_col in result_df.columns:
        groups        = result_df.groupby(type_col, sort=False)
        ordered_types = result_df[type_col].unique().tolist()
    else:
        groups        = {"Entities": result_df}.items()
        ordered_types = ["Entities"]

    for etype in ordered_types:
        try:
            group_df = groups.get_group(etype)
        except Exception:
            group_df = result_df[result_df[type_col] == etype]

        icon, icon_cls = _icon_for_type(str(etype))
        st.markdown(
            _section_header(icon, icon_cls, str(etype), len(group_df)),
            unsafe_allow_html=True,
        )

        for _, row in group_df.iterrows():
            score      = int(row.get("_match_pct", 70))
            score_html = _nlp_score_badge(score)

            # Use shared card builder if available, otherwise use lightweight fallback
            if _CARD_IMPORT_OK:
                card_html = _build_entity_card(row)
                # Inject score badge into card header
                card_html = card_html.replace(
                    '<div class="entity-card">',
                    f'<div class="match-card">',
                    1,
                ).replace(
                    "</div>",
                    f'<div style="position:absolute;top:18px;right:18px">{score_html}</div>',
                    1,
                )
                # Wrap in position:relative for the badge
                card_html = card_html.replace(
                    '<div class="match-card">',
                    '<div class="match-card" style="position:relative">',
                    1,
                )
                st.markdown(card_html, unsafe_allow_html=True)
            else : 
                print('ERROR')
            # else:
            #     # Fallback inline card
            #     name      = str(row.get(db_col("name"),        "?"))
            #     affil     = str(row.get(db_col("affiliation"),  ""))
            #     one_liner = str(row.get(db_col("one_liner"),    ""))
            #     tags_raw  = str(row.get(db_col("tags"),         ""))
            #     country   = str(row.get(db_col("country"),      ""))
            #     email     = str(row.get(db_col("email"),        ""))

            #     tags_html = " ".join(
            #         f'<span class="tag">{t.strip()}</span>'
            #         for t in tags_raw.split(" / ")
            #         if t.strip() and tags_raw not in ("nan", "")
            #     )
            #     email_html = (
            #         f'<div class="match-contact">✉ <a href="mailto:{email}">{email}</a></div>'
            #         if "@" in email else ""
            #     )
            #     affil_text = f"{affil} · {country}" if affil and country else (affil or country)
            #     desc = one_liner if one_liner not in ("nan", "") else ""

            #     st.markdown(
            #         f'<div class="match-card" style="position:relative">'
            #         f'<div style="position:absolute;top:14px;right:16px">{score_html}</div>'
            #         f'<p class="match-card-name">{name}</p>'
            #         f'<p class="match-card-affil">{affil_text}</p>'
            #         f'<p class="match-card-desc">{desc}</p>'
            #         f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px">'
            #         f"{tags_html}</div>"
            #         f"{email_html}"
            #         f"</div>",
            #         unsafe_allow_html=True,
            #     )

    # CTA buttons
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, _ = st.columns([1.2, 1.2, 1, 1.5])

    if c1.button("🌐 View in Ecosystem", width="stretch", key="nlp_goto_eco", type="primary"):
        # Pre-fill filters in Explore Ecosystem
        active = {k: v for k, v in filters.items() if v}
        for k, v in active.items():
            st.session_state[f"filter_{k}"] = v
        st.session_state.page = "Explore Ecosystem"
        st.rerun()

    c2.button("📤 Export Partner Pack", disabled=True, width="stretch", key="nlp_export")

    if c3.button("🔄 New search", width="stretch", key="nlp_reset"):
        st.session_state.fmp_show_results = False
        st.session_state.fmp_query = ""
        # PERF: clear cached match result so next search starts fresh
        st.session_state.pop("fmp_nlp_result", None)
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
#  MAIN RENDER
# ════════════════════════════════════════════════════════════════════════════════

def render(df: pd.DataFrame) -> None:
    st.markdown(
        '<div class="page-header"><h2> Find My Partners</h2>'
        '<p class="page-subtitle">'
        "Describe your project or technology challenge to find matching "
        "research groups, startups, and facilitators."
        "</p></div>",
        unsafe_allow_html=True,
    )

    # Session state init
    if "fmp_show_results" not in st.session_state:
        st.session_state.fmp_show_results = False
    if "fmp_query" not in st.session_state:
        st.session_state.fmp_query = ""

    # ── STEP 1 : Input ───────────────────────────────────────────────────────
    if not st.session_state.fmp_show_results:

        st.markdown('<div class="fmp-input-box"><h3>Describe your need</h3>', unsafe_allow_html=True)

        examples = [
            "Smartwatch powered by quantum sensors for biometric monitoring",
            "Quantum communication for secure industrial data transfer",
            "Quantum computing partner for drug discovery optimization",
        ]
        st.caption("Examples:")
        ex_cols = st.columns(len(examples))
        for col_w, ex in zip(ex_cols, examples):
            if col_w.button(ex, key=f"ex_{ex[:18]}", width="stretch"):
                st.session_state.fmp_query = ex

        query = st.text_area(
            "Your project",
            value=st.session_state.fmp_query,
            height=110,
            placeholder=(
                "Ex : We are developing a smartwatch powered by quantum sensors for "
                "biometric monitoring. We need research groups with expertise in quantum "
                "sensing and startups that can help with hardware integration…"
            ),
            key="fmp_query_input",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2, _ = st.columns([1.3, 1, 2.7])
        go = c1.button("🔍 Find Partners", type="primary", width="stretch", key="fmp_go")
        if c2.button("Clear", width="stretch", key="fmp_clear"):
            st.session_state.fmp_query = ""
            st.rerun()

        if go:
            if not query.strip():
                st.warning("Please describe your project before searching.")
            else:
                with st.spinner("Running NLP analysis…"):
                    try:
                        matcher = _load_matcher_cached()
                        result_df, filters, explanation = matcher.match(query, top_k=12)
                        st.session_state.fmp_nlp_result = (result_df, filters, explanation)
                    except Exception as e:
                        st.error(f"NLP error: {e}")
                        return
                st.session_state.fmp_query        = query
                st.session_state.fmp_show_results = True
                st.rerun()

        with st.expander("💡 Tips for better results"):
            st.markdown(
                """
                - **Be specific**: mention the application domain, technology type, and integration context.
                - **Include constraints**: hardware limits, budget, timeline, geographic preference.
                - **Describe what you bring**: your expertise, IP, or infrastructure helps calibrate the results.
                - **Specify your stage**: early exploration vs. deployment-ready integration.
                """
            )

    # ── STEP 2 : Results ─────────────────────────────────────────────────────
    else:
        query         = st.session_state.fmp_query
        query_display = query[:90] + ("…" if len(query) > 90 else "")
        st.markdown(
            f'<div style="background:oklch(0.57 0.22 303 / 0.07);border-radius:8px;'
            f'padding:10px 16px;margin-bottom:16px;font-size:0.88rem;color:var(--t3)">'
            f'<strong style="color:var(--a300)">Query:</strong> {query_display}</div>',
            unsafe_allow_html=True,
        )

        # PERF: retrieve match results from session_state cache (computed in Step 1).
        #       Falls back to re-running matcher.match() only on cold load
        #       (e.g. page refresh with results still in state).
        cached = st.session_state.get("fmp_nlp_result")
        if cached is not None:
            result_df, filters, explanation = cached
        else:
            with st.spinner("Running semantic search…"):
                try:
                    matcher = _load_matcher_cached()
                    result_df, filters, explanation = matcher.match(query, top_k=12)
                    st.session_state.fmp_nlp_result = (result_df, filters, explanation)
                except Exception as e:
                    st.error(f"NLP error: {e}")
                    return
        _show_nlp_results(result_df, filters, explanation, query)
