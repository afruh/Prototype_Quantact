import streamlit as st

"""
pages/explore.py
Filter panel, result cards, raw table.
Supports pre-filled filters passed via session_state from the AI Assistant.
"""

def _build_entity_card(row):
    tags_html = " ".join(
        f'<span class="tag">{t.strip()}</span>'
        for t in row["Tags"].split(",") if t.strip()
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
    em = str(row.get("Contact_email", ""))
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

    # Read pre-filled filters coming from the AI Assistant (consumed once)
    default_types = st.session_state.pop("filter_types", [])
    default_tags  = st.session_state.pop("filter_tags",  [])
    default_col   = st.session_state.pop("filter_col",   [])

    # Filter panel
    with st.expander("Filters", expanded=True):
        r1, r2, r3 = st.columns(3)
        with r1:
            sel_types = st.multiselect(
                "Entity Type",
                sorted(df["Entity_Type"].dropna().unique()),
                default=default_types,
                placeholder="All types",
            )
        with r2:
            sel_locs = st.multiselect(
                "Location",
                sorted(df["Location"].dropna().unique()),
                placeholder="All locations",
            )
        with r3:
            sel_col = st.multiselect(
                "Open to Collaboration",
                sorted(df["Open_to_Collab"].dropna().unique()),
                default=default_col,
                placeholder="All",
            )

        all_tags = sorted(
            {t.strip() for raw in df["Tags"] for t in raw.split(",") if t.strip()}
        )
        sel_tags = st.multiselect(
            "Research Topics / Tags",
            all_tags,
            default=default_tags,
            placeholder="Select topics...",
        )
        kw = st.text_input("Keyword search (name or description)", "")

    # Apply filters
    filt = df.copy()
    if sel_types: filt = filt[filt["Entity_Type"].isin(sel_types)]
    if sel_locs:  filt = filt[filt["Location"].isin(sel_locs)]
    if sel_col:   filt = filt[filt["Open_to_Collab"].isin(sel_col)]
    if sel_tags:
        filt = filt[
            filt["Tags"].apply(lambda t: any(tg.lower() in t.lower() for tg in sel_tags))
        ]
    if kw:
        q = kw.lower()
        filt = filt[
            filt["Entity_Name"].str.lower().str.contains(q, na=False)
            | filt["One_Liner"].str.lower().str.contains(q, na=False)
        ]

    # Results
    st.markdown(f"**{len(filt)} result(s) found**")
    st.markdown("---")

    if filt.empty:
        st.warning("No results found. Try broadening your filters.")
    else:
        for _, row in filt.iterrows():
            st.markdown(_build_entity_card(row), unsafe_allow_html=True)

    with st.expander("Raw table"):
        st.dataframe(filt, use_container_width=True)