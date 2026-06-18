"""
sections/ecosystem_explorer.py
────────────────────────────────
Model 2 : Explore the Ecosystem
Visual catalog with thematic filters, actor grid cards,
geographic distribution — uses the real database (df).
"""

import streamlit as st
import pandas as pd

# ── Constants ──────────────────────────────────────────────────────────────────

# Thematic filter labels (mapped to keyword searches on tags/description)
THEMATIC_FILTERS = [
    "Quantum Computing",
    "Quantum Sensors",
    "Quantum Communication",
    "Quantum Cryptography",
    "Quantum Materials",
    "Photonics",
    "Software & Algorithms",
    "Hardware & Devices",
]

# Actor-type style map  (values: CSS class suffix, display label)
TYPE_STYLE: dict[str, tuple[str, str]] = {
    "Academia":      ("academia",    "Academia"),
    "Research":      ("academia",    "Academia"),
    "University":    ("academia",    "Academia"),
    "Startup":       ("startup",     "Startup"),
    "Industry":      ("industry",    "Industry"),
    "Company":       ("industry",    "Industry"),
    "Facilitator":   ("facilitator", "Facilitator"),
    "Foundation":    ("facilitator", "Facilitator"),
    "Government":    ("facilitator", "Facilitator"),
    "Investor":      ("facilitator", "Facilitator"),
    "Incubator":     ("facilitator", "Facilitator"),
    "Other":         ("other",       "Other"),
}

REGIONS = ["All Regions", "Switzerland", "France", "Germany", "USA", "Asia-Pacific", "Other"]

# ── Helpers ────────────────────────────────────────────────────────────────────

def _resolve_type_style(entity_type: str) -> tuple[str, str]:
    """Return (css_class_suffix, display_label) for an entity type string."""
    if not isinstance(entity_type, str):
        return "other", "Other"
    for key, val in TYPE_STYLE.items():
        if key.lower() in entity_type.lower():
            return val
    return "other", entity_type


def _tag_html(tags_raw) -> str:
    """Render a comma-separated tag string as HTML pill spans."""
    if not isinstance(tags_raw, str) or not tags_raw.strip():
        return ""
    pills = [t.strip() for t in tags_raw.split(",") if t.strip()]
    return " ".join(f'<span class="tag">{p}</span>' for p in pills[:4])


def _eco_card(row: pd.Series) -> str:
    css_sfx, type_label = _resolve_type_style(str(row.get("Type", "")))
    name    = str(row.get("Name", "Unknown"))
    affil   = str(row.get("Affiliation", "") or row.get("Organisation", "") or "")
    desc    = str(row.get("One-liner", "") or row.get("Description", "") or "")
    country = str(row.get("Country / Region", "") or "")
    tags    = _tag_html(str(row.get("Tags", "") or ""))

    affil_part = f'<p class="eco-card-affil">{affil}</p>' if affil and affil != "nan" else ""
    country_part = (
        f'<span style="color:#5B4F7A;font-size:0.78rem;">📍 {country}</span>'
        if country and country != "nan" else ""
    )
    desc_part = (
        f'<p class="eco-card-desc">{desc}</p>'
        if desc and desc != "nan" else ""
    )

    return (
        f'<div class="eco-card">'
        f'<span class="eco-card-type type-{css_sfx}">{type_label}</span>'
        f'<p class="eco-card-name">{name}</p>'
        f'{affil_part}'
        f'{desc_part}'
        f'<div style="display:flex;flex-wrap:wrap;gap:4px;align-items:center;">'
        f'{tags} {country_part}'
        f'</div>'
        f'</div>'
    )


def _geo_bar(label: str, count: int, total: int) -> str:
    pct = round(count / total * 100) if total else 0
    return (
        f'<div class="geo-bar-wrap">'
        f'<div class="geo-bar-label"><span>{label}</span><span>{count} actors · {pct}%</span></div>'
        f'<div class="geo-bar-track"><div class="geo-bar-fill" style="width:{pct}%"></div></div>'
        f'</div>'
    )


def _type_filter_html(active_types: list[str], all_types: list[str]) -> str:
    pills = []
    for t in all_types:
        css = "filter-pill-active" if t in active_types else "filter-pill"
        pills.append(f'<span class="{css}">{t}</span>')
    return "".join(pills)


# ── Sidebar-style filter panel ─────────────────────────────────────────────────

def _filter_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Render filter widgets and return the filtered dataframe."""

    # ── Thematic keyword filter ──
    st.markdown("**Thematic focus**")
    selected_themes = st.multiselect(
        "Thematic focus",
        options=THEMATIC_FILTERS,
        default=[],
        placeholder="All topics",
        label_visibility="collapsed",
    )

    # ── Actor type ──
    st.markdown("**Actor type**")
    all_types_raw = df.get("Type", pd.Series(dtype=str)).dropna().unique().tolist()
    all_display   = sorted({_resolve_type_style(t)[1] for t in all_types_raw})
    selected_types = st.multiselect(
        "Actor type",
        options=all_display,
        default=[],
        placeholder="All types",
        label_visibility="collapsed",
    )

    # ── Geographic proximity ──
    st.markdown("**Geographic region**")
    selected_region = st.selectbox(
        "Region",
        options=REGIONS,
        index=0,
        label_visibility="collapsed",
    )

    # ── Open to collaboration ──
    collab_only = st.toggle("Open to collaboration only", value=False)

    # ── Apply filters ──
    filtered = df.copy()

    if selected_themes:
        mask = filtered.apply(
            lambda row: any(
                theme.lower() in str(row.get("Tags", "")).lower()
                or theme.lower() in str(row.get("One-liner", "")).lower()
                or theme.lower() in str(row.get("Description", "")).lower()
                for theme in selected_themes
            ),
            axis=1,
        )
        filtered = filtered[mask]

    if selected_types:
        filtered = filtered[
            filtered["Type"].apply(
                lambda t: _resolve_type_style(str(t))[1] in selected_types
            )
        ]

    if selected_region != "All Regions":
        filtered = filtered[
            filtered.get("Country / Region", pd.Series(dtype=str))
            .fillna("")
            .str.contains(selected_region, case=False, na=False)
        ]

    if collab_only:
        collab_col = next(
            (c for c in filtered.columns if "collab" in c.lower()), None
        )
        if collab_col:
            filtered = filtered[
                filtered[collab_col].astype(str).str.lower().isin(["yes", "true", "1", "oui"])
            ]

    return filtered


# ── Geographic distribution sidebar ───────────────────────────────────────────

def _geo_section(df: pd.DataFrame) -> None:
    st.markdown("**Geographic distribution**")
    country_col = next((c for c in df.columns if "country" in c.lower()), None)
    if country_col is None:
        st.caption("No geographic data available.")
        return

    counts = (
        df[country_col]
        .fillna("Unknown")
        .replace("", "Unknown")
        .value_counts()
        .head(6)
    )
    total = counts.sum()
    for country, cnt in counts.items():
        st.markdown(_geo_bar(str(country), int(cnt), int(total)), unsafe_allow_html=True)


# ── Stats row ──────────────────────────────────────────────────────────────────

def _stats_row(total: int, filtered: int, type_breakdown: dict) -> None:
    cols = st.columns(4)
    cols[0].markdown(
        f'<div class="stat-card"><h2>{filtered}</h2><p>Actors shown</p></div>',
        unsafe_allow_html=True,
    )
    cols[1].markdown(
        f'<div class="stat-card"><h2>{type_breakdown.get("Academia", 0)}</h2>'
        f'<p>Research groups</p></div>',
        unsafe_allow_html=True,
    )
    cols[2].markdown(
        f'<div class="stat-card"><h2>{type_breakdown.get("Startup", 0)}</h2>'
        f'<p>Startups</p></div>',
        unsafe_allow_html=True,
    )
    cols[3].markdown(
        f'<div class="stat-card"><h2>{type_breakdown.get("Facilitator", 0)}</h2>'
        f'<p>Facilitators</p></div>',
        unsafe_allow_html=True,
    )


# ── Main render ────────────────────────────────────────────────────────────────

def render(df: pd.DataFrame) -> None:
    st.markdown(
        '<div class="page-header">'
        "<h2>🌐 Explore the Ecosystem</h2>"
        '<p class="page-subtitle">'
        "Browse the full quantum landscape — filter by topic, actor type, and geography "
        "to discover the research groups, startups, companies, and facilitators that "
        "shape the ecosystem."
        "</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="demo-banner">'
        "⚡ <strong>Demo mode</strong> — showing real database actors with an "
        "enhanced visual interface."
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Layout: filter sidebar + main grid ──────────────────────────────────────
    left, right = st.columns([1, 3], gap="large")

    with left:
        st.markdown(
            '<p style="font-size:0.8rem;font-weight:700;letter-spacing:0.08em;'
            'text-transform:uppercase;color:#5B4F7A;margin-bottom:14px;">FILTERS</p>',
            unsafe_allow_html=True,
        )
        filtered_df = _filter_panel(df)
        st.markdown("<br>", unsafe_allow_html=True)
        _geo_section(filtered_df if not filtered_df.empty else df)

    with right:
        # ── Type breakdown for stats ──
        type_breakdown: dict[str, int] = {}
        if not filtered_df.empty and "Type" in filtered_df.columns:
            for _, row in filtered_df.iterrows():
                label = _resolve_type_style(str(row.get("Type", "")))[1]
                type_breakdown[label] = type_breakdown.get(label, 0) + 1

        _stats_row(len(df), len(filtered_df), type_breakdown)
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Sort & search bar ──
        s_col, sort_col = st.columns([3, 1])
        search_text = s_col.text_input(
            "Search",
            placeholder="Search by name, tag, or keyword…",
            label_visibility="collapsed",
        )
        sort_by = sort_col.selectbox(
            "Sort",
            ["Name A–Z", "Type", "Region"],
            label_visibility="collapsed",
        )

        # Apply text search
        if search_text.strip():
            mask = filtered_df.apply(
                lambda row: search_text.lower() in str(row.values).lower(), axis=1
            )
            filtered_df = filtered_df[mask]

        # Apply sort
        name_col = next((c for c in filtered_df.columns if "name" in c.lower()), None)
        type_col = next((c for c in filtered_df.columns if "type" in c.lower()), None)
        geo_col  = next((c for c in filtered_df.columns if "country" in c.lower()), None)

        if sort_by == "Name A–Z" and name_col:
            filtered_df = filtered_df.sort_values(name_col)
        elif sort_by == "Type" and type_col:
            filtered_df = filtered_df.sort_values(type_col)
        elif sort_by == "Region" and geo_col:
            filtered_df = filtered_df.sort_values(geo_col)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Actor grid (3 columns) ──────────────────────────────────────────────
        if filtered_df.empty:
            st.markdown(
                '<div class="coming"><h3>No actors match your filters</h3>'
                "<p>Try broadening your search or adjusting the filters.</p></div>",
                unsafe_allow_html=True,
            )
        else:
            # Paginate: 12 cards per page
            PAGE_SIZE = 12
            total_pages = max(1, -(-len(filtered_df) // PAGE_SIZE))  # ceiling div

            if "eco_page" not in st.session_state:
                st.session_state.eco_page = 0
            # Reset to page 0 when filters change (proxy: total count changed)
            if "eco_last_count" not in st.session_state:
                st.session_state.eco_last_count = len(filtered_df)
            if st.session_state.eco_last_count != len(filtered_df):
                st.session_state.eco_page = 0
                st.session_state.eco_last_count = len(filtered_df)

            page_idx = st.session_state.eco_page
            start = page_idx * PAGE_SIZE
            page_rows = filtered_df.iloc[start : start + PAGE_SIZE]

            # Render 3-column grid
            g1, g2, g3 = st.columns(3)
            for i, (_, row) in enumerate(page_rows.iterrows()):
                target = [g1, g2, g3][i % 3]
                with target:
                    st.markdown(_eco_card(row), unsafe_allow_html=True)

            # Pagination controls
            if total_pages > 1:
                st.markdown("<br>", unsafe_allow_html=True)
                p_left, p_mid, p_right = st.columns([1, 2, 1])
                if p_left.button("← Previous", disabled=(page_idx == 0), key="eco_prev", width="stretch"):
                    st.session_state.eco_page -= 1
                    st.rerun()
                p_mid.markdown(
                    f'<p style="text-align:center;color:#7C6FA0;font-size:0.85rem;margin-top:10px;">'
                    f'Page {page_idx + 1} of {total_pages} · {len(filtered_df)} actors</p>',
                    unsafe_allow_html=True,
                )
                if p_right.button("Next →", disabled=(page_idx >= total_pages - 1), key="eco_next", width="stretch"):
                    st.session_state.eco_page += 1
                    st.rerun()
