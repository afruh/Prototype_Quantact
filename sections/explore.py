import streamlit as st
from database import FILTERS, apply_filters, apply_keyword_search, get_unique_values, col as db_col

"""
sections/explore.py
Filter panel, result cards, raw table.
Supports pre-filled filters passed via session_state from the AI Assistant.
"""

def _safe(row, key: str) -> str:
    """Get a cell value safely — returns empty string for nan/None/empty."""
    val = row.get(db_col(key), "")
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


def _build_entity_card(row):
    name        = _safe(row, "name")
    entity_type = _safe(row, "entity_type")
    sub_type    = _safe(row, "sub_type")
    affiliation = _safe(row, "affiliation")
    country     = _safe(row, "country")
    one_liner   = _safe(row, "one_liner")
    quantum     = _safe(row, "quantum_field")
    trl         = _safe(row, "trl")
    collab      = _safe(row, "open_to_collab")
    ind_exp     = _safe(row, "industry_exp")
    looking_for = _safe(row, "looking_for")
    website     = _safe(row, "website")
    linkedin    = _safe(row, "linkedin")
    email       = _safe(row, "email")
    contact     = _safe(row, "contact_name")

    # Fallback: use quantum_field as description if one_liner is empty
    description = one_liner if one_liner else quantum

    # Tag pills from quantum field
    tags_html = _pills(quantum)

    # Collaboration badge
    if collab.lower() == "yes":
        collab_badge = _badge("Open to collaboration", "b-yes")
    elif collab.lower() == "no":
        collab_badge = _badge("Not open", "b-no")
    else:
        collab_badge = '<span style="color:#888;font-size:0.8rem">Collaboration unknown</span>'

    # TRL badge
    trl_badge = (
        f'<span style="background:#1a2a4a;color:#7eb8f7;border-radius:20px;'
        f'padding:2px 10px;font-size:0.8rem">TRL: {trl}</span>'
        if trl else ""
    )

    # Industry experience badge
    ind_badge = (
        '<span style="color:#ffd740;font-size:0.8rem">Industry exp.</span>'
        if ind_exp.lower() == "yes" else ""
    )

    # Sub-type and affiliation line
    meta_parts = [p for p in [entity_type, sub_type, affiliation, country] if p]
    meta_line  = " &middot; ".join(meta_parts)

    # Looking for section
    looking_html = (
        f'<div style="color:#aaa;font-size:0.82rem;margin-top:6px">'
        f'<span style="color:#888">Looking for:</span> {looking_for}</div>'
        if looking_for else ""
    )

    # Links row
    links = []
    if website.startswith("http"):
        links.append(f'<a href="{website}" target="_blank">Website</a>')
    if linkedin.startswith("http"):
        links.append(f'<a href="{linkedin}" target="_blank">LinkedIn</a>')
    if "@" in email:
        label = contact if contact else email
        links.append(f'<a href="mailto:{email}">{label}</a>')
    links_html = " &nbsp; ".join(links)

    return (
        f'<div class="entity-card">'
        # Header
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px">'
        f'<h3 style="margin:0">{name}</h3>'
        f'<span style="color:#888;font-size:0.8rem;padding-top:4px">{entity_type}</span>'
        f'</div>'
        # Meta line
        f'<div class="meta">{meta_line}</div>'
        # Description
        f'<div class="liner">{description}</div>'
        # Tags
        f'<div style="margin-bottom:10px">{tags_html}</div>'
        # Badges row
        f'<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px">'
        f'{collab_badge} {trl_badge} {ind_badge}'
        f'</div>'
        # Looking for
        f'{looking_html}'
        # Links
        f'<div style="font-size:0.88rem;margin-top:10px">{links_html}</div>'
        f'</div>'
    )


def render(df):
    st.markdown("## Explore the Database")
    st.caption("Filter and search across all entities in the Geneva quantum ecosystem.")

    # Read pre-filled filters from AI Assistant if any
    active_filters = {}
    for f in FILTERS:
        default = st.session_state.pop(f"filter_{f['key']}", [])
        active_filters[f["key"]] = default

    # Filter panel — built dynamically from FILTERS in database.py
    with st.expander("Filters", expanded=True):
        cols_ui = st.columns(3)
        for i, f in enumerate(FILTERS):
            options = get_unique_values(df, f["column"], f["multi_value"])
            with cols_ui[i % 3]:
                active_filters[f["key"]] = st.multiselect(
                    f["label"],
                    options,
                    default=active_filters[f["key"]],
                    placeholder="All",
                    key=f"filter_widget_{f['key']}",
                )
        kw = st.text_input("Keyword search (name, description, tags...)", "")

    # Apply
    filt = apply_filters(df, active_filters)
    filt = apply_keyword_search(filt, kw)

    st.markdown(f"**{len(filt)} result(s) found**")
    st.markdown("---")

    if filt.empty:
        st.warning("No results found. Try broadening your filters.")
    else:
        for _, row in filt.iterrows():
            st.markdown(_build_entity_card(row), unsafe_allow_html=True)

    with st.expander("Raw table"):
        st.dataframe(filt, width="stretch")