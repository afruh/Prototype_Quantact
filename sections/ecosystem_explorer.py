"""
sections/ecosystem_explorer.py
────────────────────────────────
Model 2 : Explore the Ecosystem
Visual catalog with thematic filters, actor grid cards,
geographic distribution — uses the real database (df).
"""

import streamlit as st
import pandas as pd
from database import FILTERS, apply_filters, apply_keyword_search, get_unique_values, col as db_col


# ── Card helpers (copied from explore.py) ─────────────────────────────────────

def _safe(row, key: str) -> str:
    """Get a cell value safely — returns empty string for nan/None/empty."""
    val = row.get(key, "")   # ← plus de db_col, on prend la clé telle quelle
    return "" if str(val).lower() in ("nan", "none", "") else str(val).strip()

def _pills(text: str, sep: str = " / ") -> str:
    """Convert a separated string into HTML tag pills."""
    if not text:
        return ""
    return " ".join(
        f'<span class="tag">{t.strip()}</span>'
        for t in text.split(sep) if t.strip()
    )


def _badge(text: str, css_class: str) -> str:
    return f'<span class="{css_class}">{text}</span>' if text else ""


def _build_entity_card(row) -> str:
    """Build a clean, minimal card showing only the essential fields (WIP-friendly)."""
    # On utilise les noms EXACTS des colonnes Excel pour être sûr de tout récupérer
    name        = _safe(row, "Entity_Name")
    affiliation = _safe(row, "Affiliation")
    sub_type    = _safe(row, "Sub_Type")
    country     = _safe(row, "Country / Region")
    website     = _safe(row, "Website")

    # Ligne de métadonnées (Affiliation · Pays)
    meta_parts = [p for p in [affiliation, country] if p]
    meta_line  = " &middot; ".join(meta_parts)

    # Badge Sub-type (optionnel, affiché en haut à droite)
    sub_badge = (
        f'<span style="background:#9347df0f;color:#9B8EC4;border:1px solid #3a3a5a;'
        f'border-radius:20px;padding:2px 12px;font-size:0.7rem;white-space:nowrap;">{sub_type}</span>'
        if sub_type else ""
    )

    # Lien vers le site web
    links = []
    if website.startswith("http"):
        links.append(
            f'<a href="{website}" target="_blank" style="text-decoration:none;color:#7C6FA0;">🌐 Website</a>'
        )
    links_html = " &nbsp; ".join(links)

    return (
        f'<div class="entity-card" '
        f'border:1px solid #2a2a40;padding:16px;height:100%;display:flex;flex-direction:column;">'
        # En-tête : Nom + badge Sub-type
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:6px;">'
        f'<h3 style="margin:0;font-size:1.1rem;color:#fff;flex:1;">{name}</h3>'
        f'{sub_badge}'
        f'</div>'
        # Affiliation · Pays
        f'<div style="color:#aaa;font-size:0.85rem;margin-bottom:10px;">{meta_line}</div>'
        # Lien site web
        f'<div style="margin-top:auto;border-top:1px solid #ffffff;padding-top:10px;font-size:0.9rem;">'
        f'{links_html}'
        f'</div>'
        f'</div>'
    )


# ── Geographic distribution ───────────────────────────────────────────────────

def _geo_bar(label: str, count: int, total: int) -> str:
    pct = round(count / total * 100) if total else 0
    return (
        f'<div class="geo-bar-wrap">'
        f'<div class="geo-bar-label"><span>{label}</span>'
        f'<span>{count} actors · {pct}%</span></div>'
        f'<div class="geo-bar-track">'
        f'<div class="geo-bar-fill" style="width:{pct}%"></div></div>'
        f'</div>'
    )


def _geo_section(df: pd.DataFrame) -> None:
    st.markdown("**Geographic distribution**")
    country_col = db_col("country")
    if country_col not in df.columns:
        st.caption("No geographic data available.")
        return

    counts = (
        df[country_col]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .head(6)
    )
    if counts.empty:
        st.caption("No geographic data available.")
        return

    total = counts.sum()
    for country, cnt in counts.items():
        st.markdown(_geo_bar(str(country), int(cnt), int(total)), unsafe_allow_html=True)


# ── Stats row ─────────────────────────────────────────────────────────────────

def _stats_row(filtered_df: pd.DataFrame) -> None:
    entity_col = db_col("entity_type")

    def count_type(label: str) -> int:
        if entity_col not in filtered_df.columns:
            return 0
        return int(
            filtered_df[entity_col]
            .str.contains(label, case=False, na=False)
            .sum()
        )

    cols = st.columns(4)
    cols[0].markdown(
        f'<div class="stat-card"><h2>{len(filtered_df)}</h2>'
        f'<p>Actors shown</p></div>',
        unsafe_allow_html=True,
    )
    cols[1].markdown(
        f'<div class="stat-card"><h2>{count_type("Academia")}</h2>'
        f'<p>Research groups</p></div>',
        unsafe_allow_html=True,
    )
    cols[2].markdown(
        f'<div class="stat-card"><h2>{count_type("Startup")}</h2>'
        f'<p>Startups</p></div>',
        unsafe_allow_html=True,
    )
    cols[3].markdown(
        f'<div class="stat-card"><h2>{count_type("Facilitator")}</h2>'
        f'<p>Facilitators</p></div>',
        unsafe_allow_html=True,
    )


# ── Filter panel ──────────────────────────────────────────────────────────────

def _filter_panel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render sidebar filter widgets built dynamically from FILTERS.
    The open_to_collab filter is rendered as a toggle; all others as multiselects.
    Returns the filtered DataFrame.
    """
    active_filters: dict[str, list] = {}

    for f in FILTERS:
        key = f["key"]

        if key == "open_to_collab":
            # Render as toggle — maps True → ["Yes"] for apply_filters
            collab_only = st.toggle(
                "Open to collaboration only",
                value=False,
                key="eco_collab_toggle",
            )
            active_filters[key] = ["Yes"] if collab_only else []

        else:
            st.markdown(f'**{f["label"]}**')
            options = get_unique_values(df, f["column"], f["multi_value"])
            active_filters[key] = st.multiselect(
                f["label"],
                options,
                default=[],
                placeholder="All",
                label_visibility="collapsed",
                key=f"eco_filter_{key}",
            )

    return apply_filters(df, active_filters)


# ── Main render ───────────────────────────────────────────────────────────────

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

    # ── Layout: filter sidebar (1) + main grid (3) ────────────────────────────
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
        _stats_row(filtered_df)
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Search + sort bar ─────────────────────────────────────────────────
        s_col, sort_col = st.columns([3, 1])
        search_text = s_col.text_input(
            "Search",
            placeholder="Search by name, tag, or keyword…",
            label_visibility="collapsed",
            key="eco_search",
        )
        sort_by = sort_col.selectbox(
            "Sort",
            ["Name A–Z", "Type", "Region"],
            label_visibility="collapsed",
            key="eco_sort",
        )

        # Apply keyword search
        if search_text.strip():
            filtered_df = apply_keyword_search(filtered_df, search_text)

        # Apply sort
        name_col    = db_col("name")
        type_col    = db_col("entity_type")
        country_col = db_col("country")

        if sort_by == "Name A–Z" and name_col in filtered_df.columns:
            filtered_df = filtered_df.sort_values(
                name_col, key=lambda s: s.str.lower()
            )
        elif sort_by == "Type" and type_col in filtered_df.columns:
            filtered_df = filtered_df.sort_values(type_col)
        elif sort_by == "Region" and country_col in filtered_df.columns:
            filtered_df = filtered_df.sort_values(country_col)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Actor grid (3 columns, paginated) ─────────────────────────────────
        if filtered_df.empty:
            st.markdown(
                '<div class="coming"><h3>No actors match your filters</h3>'
                "<p>Try broadening your search or adjusting the filters.</p></div>",
                unsafe_allow_html=True,
            )
        else:
            PAGE_SIZE   = 12
            total_pages = max(1, -(-len(filtered_df) // PAGE_SIZE))  # ceiling div

            # Reset to page 0 when result count changes (filters updated)
            if "eco_page" not in st.session_state:
                st.session_state.eco_page = 0
            if "eco_last_count" not in st.session_state:
                st.session_state.eco_last_count = len(filtered_df)
            if st.session_state.eco_last_count != len(filtered_df):
                st.session_state.eco_page = 0
                st.session_state.eco_last_count = len(filtered_df)

            page_idx  = st.session_state.eco_page
            start     = page_idx * PAGE_SIZE
            page_rows = filtered_df.iloc[start : start + PAGE_SIZE]

            # 2-column grid
            g1, g2 = st.columns(2)
            for i, (_, row) in enumerate(page_rows.iterrows()):
                target = [g1, g2][i % 2]
                with target:
                    st.markdown(_build_entity_card(row), unsafe_allow_html=True)

            # Pagination controls
            if total_pages > 1:
                st.markdown("<br>", unsafe_allow_html=True)
                p_left, p_mid, p_right = st.columns([1, 2, 1])

                if p_left.button(
                    "← Previous",
                    disabled=(page_idx == 0),
                    key="eco_prev",
                    use_container_width=True,
                ):
                    st.session_state.eco_page -= 1
                    st.rerun()

                p_mid.markdown(
                    f'<p style="text-align:center;color:#7C6FA0;font-size:0.85rem;'
                    f'margin-top:10px;">Page {page_idx + 1} of {total_pages} '
                    f'· {len(filtered_df)} actors</p>',
                    unsafe_allow_html=True,
                )

                if p_right.button(
                    "Next →",
                    disabled=(page_idx >= total_pages - 1),
                    key="eco_next",
                    use_container_width=True,
                ):
                    st.session_state.eco_page += 1
                    st.rerun()
