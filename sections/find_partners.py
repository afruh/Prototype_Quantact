"""
sections/find_partners.py
──────────────────────────
Page "Find My Partners" — two modes:

  🧠 NLP Mode  : NLPMatcher available → real database results
                 with semantic scoring, filters extracted automatically
  📋 Demo Mode : mock-data fallback if nlp_matcher is not installed

Mode selection is automatic (based on dependency availability)
with a manual toggle in the UI.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

# ── Optional NLP engine import ────────────────────────────────────────────────
try:
    from nlp_matcher import NLPMatcher, NLP_AVAILABLE as _NLP_MODULE_OK
    _NLP_IMPORT_OK = True
except ImportError:
    _NLP_IMPORT_OK = False
    _NLP_MODULE_OK = False

# ── Card builder from ecosystem_explorer ─────────────────────────────────────
try:
    from sections.ecosystem_explorer import _build_entity_card, _safe, _tag_html
    _CARD_IMPORT_OK = True
except ImportError:
    _CARD_IMPORT_OK = False

from database import col as db_col


# ════════════════════════════════════════════════════════════════════════════════
#  MOCK DATA — used in demo mode if nlp_matcher is not installed
# ════════════════════════════════════════════════════════════════════════════════

MOCK_RESEARCH = [
    {
        "name": "UNIGE Quantum Photonics Lab",
        "affiliation": "University of Geneva",
        "tags": ["Quantum Optics", "Photonic Sensing", "Quantum Communication"],
        "trl": "TRL 3–5",
        "description": "Specialises in quantum light-matter interactions, applicable to ultra-precise sensors for biometric and medical monitoring devices.",
        "score": 95, "collab": True, "contact": "photonics@unige.ch",
    },
    {
        "name": "EPFL Quantum Sensing Center",
        "affiliation": "EPFL Lausanne",
        "tags": ["Quantum Sensors", "MEMS Integration", "Signal Processing"],
        "trl": "TRL 4–6",
        "description": "Applied research in quantum sensors bridging fundamental physics and miniaturised hardware for consumer electronics and health IoT.",
        "score": 88, "collab": True, "contact": "sensing@epfl.ch",
    },
    {
        "name": "PSI Quantum Materials Group",
        "affiliation": "Paul Scherrer Institute",
        "tags": ["Quantum Materials", "Coherence", "Low-Temperature Physics"],
        "trl": "TRL 2–4",
        "description": "Fundamental research on quantum coherence in novel materials, with growing interest in real-world sensing applications.",
        "score": 71, "collab": False, "contact": "qmaterials@psi.ch",
    },
]

MOCK_STARTUPS = [
    {
        "name": "QuantumPath AG",
        "stage": "Seed",
        "tags": ["Quantum Software", "Algorithm SDK", "Hardware Integration"],
        "trl": "TRL 5–7",
        "description": "Quantum algorithm middleware for hardware deployment, specialised in sensor data processing at the quantum layer.",
        "score": 91, "collab": True, "contact": "partnerships@quantumpath.ch",
    },
    {
        "name": "QSense Analytics",
        "stage": "Pre-Seed",
        "tags": ["Biometric Sensing", "Edge AI", "Wearable IoT"],
        "trl": "TRL 4–6",
        "description": "Combines quantum sensor outputs with embedded AI for real-time biometric monitoring in consumer wearables.",
        "score": 84, "collab": True, "contact": "hello@qsense.io",
    },
]

MOCK_FACILITATORS = [
    {
        "name": "Innosuisse – Swiss Innovation Agency",
        "role": "Funding",
        "tags": ["R&D Grants", "Partnership Co-funding", "IP Strategy"],
        "description": "Swiss federal innovation agency providing grants and co-funding for academia-industry R&D partnerships in deep tech.",
        "score": 90, "contact": "contact@innosuisse.ch",
    },
    {
        "name": "Geneva Quantum Hub",
        "role": "Network / Incubation",
        "tags": ["Ecosystem Facilitation", "Introductions", "Events"],
        "description": "Connects quantum startups, research groups, and industry in the Geneva ecosystem. Bi-annual matchmaking events.",
        "score": 85, "contact": "hub@genevatech.ch",
    },
]

REFINEMENT_LINES = [
    ("Domain",      "Quantum sensors for biometric monitoring (wearable / health context)"),
    ("Core need",   "Quantum-level sensor integration + signal processing expertise"),
    ("Ideal TRL",   "Research (TRL 2–5) for academic groups · Execution (TRL 4–7) for startups"),
    ("Constraints", "Miniaturisation capacity · Low-power design · Industry experience"),
    ("Approach",    "Research groups (core science) + Startups (execution) + Facilitators (IP/funding)"),
]


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
#  DEMO MODE — mock data display
# ════════════════════════════════════════════════════════════════════════════════

def _show_refinement_mock(query: str) -> None:
    st.markdown(
        f'<div class="refinement-box">'
        f'<strong>🤖 Consultant Parser · Query analyzed</strong><br><br>'
        + "".join(
            f'<span style="color:var(--t4);font-size:0.82rem">{k}&nbsp;&nbsp;</span>'
            f'<span style="color:var(--t2);font-size:0.88rem">{v}</span><br>'
            for k, v in REFINEMENT_LINES
        )
        + "</div>",
        unsafe_allow_html=True,
    )


def _show_mock_results(query: str) -> None:
    _show_refinement_mock(query)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin:8px 0 24px">'
        '<span style="color:var(--t4);font-size:0.88rem">Shortlist ready ·</span>'
        '<span style="color:var(--ok);font-size:0.88rem;font-weight:600">'
        "3 research groups &nbsp;·&nbsp; 2 startups &nbsp;·&nbsp; 2 facilitators"
        "</span></div>",
        unsafe_allow_html=True,
    )

    # Research groups
    st.markdown(
        _section_header("🔬", "icon-research", "Research Groups", len(MOCK_RESEARCH)),
        unsafe_allow_html=True,
    )
    for r in MOCK_RESEARCH:
        collab_badge = (
            '<span class="b-yes">Open to collaboration</span>'
            if r["collab"] else '<span class="b-no">Not open</span>'
        )
        st.markdown(
            f'<div class="match-card">'
            f'<div class="match-card-header">'
            f'<div><p class="match-card-name">{r["name"]}</p>'
            f'<p class="match-card-affil">{r["affiliation"]}</p></div>'
            f'<span class="{_score_class(r["score"])}">★ {r["score"]}%</span>'
            f'</div>'
            f'<p class="match-card-desc">{r["description"]}</p>'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:8px">'
            f'{_tags_html(r["tags"])} <span class="match-trl">{r["trl"]}</span>'
            f'{collab_badge}</div>'
            f'<div class="match-contact">✉ <a href="mailto:{r["contact"]}">{r["contact"]}</a></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Startups
    st.markdown(
        _section_header("🚀", "icon-startup", "Startups", len(MOCK_STARTUPS)),
        unsafe_allow_html=True,
    )
    for s in MOCK_STARTUPS:
        st.markdown(
            f'<div class="match-card">'
            f'<div class="match-card-header">'
            f'<div><p class="match-card-name">{s["name"]}</p>'
            f'<p class="match-card-affil">Startup · {s["stage"]}</p></div>'
            f'<span class="{_score_class(s["score"])}">★ {s["score"]}%</span>'
            f'</div>'
            f'<p class="match-card-desc">{s["description"]}</p>'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px">'
            f'{_tags_html(s["tags"])} <span class="match-stage">{s["stage"]}</span>'
            f'<span class="match-trl">{s["trl"]}</span></div>'
            f'<div class="match-contact">✉ <a href="mailto:{s["contact"]}">{s["contact"]}</a></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Facilitators
    st.markdown(
        _section_header("🤝", "icon-facil", "Facilitators", len(MOCK_FACILITATORS)),
        unsafe_allow_html=True,
    )
    for f in MOCK_FACILITATORS:
        st.markdown(
            f'<div class="match-card">'
            f'<div class="match-card-header">'
            f'<div><p class="match-card-name">{f["name"]}</p>'
            f'<p class="match-card-affil">Facilitator · {f["role"]}</p></div>'
            f'<span class="{_score_class(f["score"])}">★ {f["score"]}%</span>'
            f'</div>'
            f'<p class="match-card-desc">{f["description"]}</p>'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px">'
            f'{_tags_html(f["tags"])} <span class="match-role">{f["role"]}</span></div>'
            f'<div class="match-contact">✉ <a href="mailto:{f["contact"]}">{f["contact"]}</a></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Export CTA
    st.markdown(
        '<div class="export-card"><strong>📦 Export Partner Pack</strong>'
        "Generates a structured summary of all shortlisted collaborators, "
        "ready to share with your team.</div>",
        unsafe_allow_html=True,
    )
    c1, c2, _ = st.columns([1, 1, 2])
    c1.button("📤 Export Partner Pack", disabled=True, width="stretch", key="mock_export")
    if c2.button("🔄 New search", width="stretch", key="mock_reset"):
        st.session_state.fmp_show_results = False
        st.session_state.fmp_query = ""
        st.session_state.pop("fmp_nlp_result", None)
        st.rerun()


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
        groups       = result_df.groupby(type_col, sort=False)
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
            else:
                # Fallback inline card
                name      = str(row.get(db_col("name"),        "?"))
                affil     = str(row.get(db_col("affiliation"),  ""))
                one_liner = str(row.get(db_col("one_liner"),    ""))
                tags_raw  = str(row.get(db_col("tags"),         ""))
                country   = str(row.get(db_col("country"),      ""))
                email     = str(row.get(db_col("email"),        ""))

                tags_html = " ".join(
                    f'<span class="tag">{t.strip()}</span>'
                    for t in tags_raw.split(" / ")
                    if t.strip() and tags_raw not in ("nan", "")
                )
                email_html = (
                    f'<div class="match-contact">✉ <a href="mailto:{email}">{email}</a></div>'
                    if "@" in email else ""
                )
                affil_text = f"{affil} · {country}" if affil and country else (affil or country)
                desc = one_liner if one_liner not in ("nan", "") else ""

                st.markdown(
                    f'<div class="match-card" style="position:relative">'
                    f'<div style="position:absolute;top:14px;right:16px">{score_html}</div>'
                    f'<p class="match-card-name">{name}</p>'
                    f'<p class="match-card-affil">{affil_text}</p>'
                    f'<p class="match-card-desc">{desc}</p>'
                    f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px">'
                    f"{tags_html}</div>"
                    f"{email_html}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

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

    # ── Bannière de mode ──────────────────────────────────────────────────────
    if _NLP_IMPORT_OK:
        st.markdown(
            '<div class="demo-banner">'
            "🧠 <strong>NLP mode active</strong> — results from the real database."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="demo-banner">'
            "📋 <strong>Demo mode</strong> — install <code>sentence-transformers</code> "
            "and <code>rake-nltk</code> (requirements_nlp.txt) to activate real NLP."
            "</div>",
            unsafe_allow_html=True,
        )

    # Session state init
    if "fmp_show_results" not in st.session_state:
        st.session_state.fmp_show_results = False
    if "fmp_query" not in st.session_state:
        st.session_state.fmp_query = ""
    if "fmp_use_nlp" not in st.session_state:
        st.session_state.fmp_use_nlp = _NLP_IMPORT_OK

    # ── STEP 1 : Input ───────────────────────────────────────────────────────
    if not st.session_state.fmp_show_results:

        # Toggle NLP / Demo
        if _NLP_IMPORT_OK:
            col_toggle, _ = st.columns([2, 3])
            st.session_state.fmp_use_nlp = col_toggle.toggle(
                "🧠 Use NLP (real data)",
                value=st.session_state.fmp_use_nlp,
                key="fmp_nlp_toggle",
            )

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
                use_nlp = st.session_state.get("fmp_use_nlp", False)
                label   = "Running NLP analysis…" if use_nlp else "Running simulation…"
                with st.spinner(label):
                    if use_nlp and _NLP_IMPORT_OK:
                        # PERF: run matcher.match() here, inside the spinner,
                        #       and cache the result in session_state.
                        #       This prevents re-running the semantic search on
                        #       every subsequent Streamlit rerun (button clicks,
                        #       navigation, etc.) while results are displayed.
                        try:
                            matcher = _load_matcher_cached()
                            result_df, filters, explanation = matcher.match(query, top_k=12)
                            st.session_state.fmp_nlp_result = (result_df, filters, explanation)
                        except Exception as e:
                            st.error(f"NLP error: {e}")
                            return
                    else:
                        import time; time.sleep(1.0)
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

        use_nlp = st.session_state.get("fmp_use_nlp", False) and _NLP_IMPORT_OK

        if use_nlp:
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
                        st.error(f"NLP error: {e}. Falling back to demo mode.")
                        _show_mock_results(query)
                        return
            _show_nlp_results(result_df, filters, explanation, query)
        else:
            _show_mock_results(query)
