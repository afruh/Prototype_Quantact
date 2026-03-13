import streamlit as st
from database import FILTERS, apply_filters, apply_keyword_search, get_unique_values, col

"""
pages/explore.py
Filter panel, result cards, raw table.
Supports pre-filled filters passed via session_state from the AI Assistant.
"""

def _build_entity_card(row):
    tags_html = " ".join(
        f'<span class="tag">{t.strip()}</span>'
        for t in str(row.get("Tags", "")).split("/") if t.strip()
    )
    cv = str(row["Open_to_Collab"]).lower()
    if cv == "yes":
        collab_badge = '<span class="b-yes">Open to collaboration</span>'
    elif cv == "no":
        collab_badge = '<span class="b-no">Not open</span>'
    else:
        collab_badge = '<span style="color:#888">Unknown</span>'

    industry_badge = (
        ' <span style="color:#ffd740;font-size:0.8rem">Industry exp.</span>'
        if str(row["Industry_experience"]).lower() == "yes" else ""
    )
    ws = str(row.get("Website", ""))
    website_link = (
        f'<a href="{ws}" target="_blank">Website</a> &nbsp; '
        if ws.startswith("http") else ""
    )
    em = str(row.get("Email", ""))
    nm = str(row.get("Contact_Name", ""))
    contact_link = f'<a href="mailto:{em}">{nm}</a>' if "@" in em else ""

    return (
        f'<div class="entity-card">'
        f"<h3>{row['Entity_Name']}</h3>"
        f'<div class="meta">'
        f'{row["Entity_Type"]} &middot; {row["Location"]} &middot; {collab_badge}{industry_badge}'
        f"</div>"
        f'<div class="liner">{row["One_Liner"]}</div>'
        f'<div style="margin-bottom:10px">{tags_html}</div>'
        f'<div style="font-size:0.88rem">{website_link}{contact_link}</div>'
        f"</div>"
    )

def render(df):
    st.markdown("## Explore the Database")
    st.caption("Filter and search across all entities in the Geneva quantum ecosystem.")

    # Read pre-filled filters from AI Assistant if any
    active_filters = {}
    for f in FILTERS:
        default = st.session_state.pop(f"filter_{f['key']}", [])
        active_filters[f["key"]] = default

    # Filter panel — built dynamically from FILTERS definition
    with st.expander("Filters", expanded=True):
        cols_ui = st.columns(3)
        for i, f in enumerate(FILTERS):
            options = get_unique_values(df, f["column"], f["multi_value"])
            with cols_ui[i % 3]:
                active_filters[f["key"]] = st.multiselect(
                    f["label"],
                    options,
                    default=active_filters[f["key"]],
                    placeholder=f"All",
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
        st.dataframe(filt, use_container_width=True)