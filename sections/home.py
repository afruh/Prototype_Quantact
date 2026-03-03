import streamlit as st

"""
pages/home.py
Hero banner, stats row, navigation cards, entity type chart.
"""

def render(df):
    # Hero banner
    st.markdown(
        '<div class="hero">'
        "<h1>Quant@ct Hub</h1>"
        "<p>We build bridges between academic research and industry in Geneva "
        "around the field of Quantum.<br>"
        "Discover research groups, industries, and facilitators pushing the "
        "frontier of quantum science.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Stats row
    total  = len(df)
    types  = df["Entity_Type"].nunique()
    collab = (df["Open_to_Collab"].str.lower() == "yes").sum()
    locs   = df["Location"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    for col, value, label in [
        (c1, total,  "Entities"),
        (c2, types,  "Entity Types"),
        (c3, collab, "Open to Collaboration"),
        (c4, locs,   "Locations"),
    ]:
        col.markdown(
            f'<div class="stat-card"><h2>{value}</h2><p>{label}</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation cards
    st.markdown("### Where do you want to go?")
    card1, card2, card3 = st.columns(3)

    with card1:
        st.markdown(
            '<div class="nav-card"><h3>Explore Database</h3>'
            "<p>Filter by type, location, tags, and collaboration status "
            "to find the right group or organisation.</p></div>",
            unsafe_allow_html=True,
        )
        if st.button("Open", key="goto_explore", use_container_width=True):
            st.session_state.page = "Explore Database"
            st.rerun()

    with card2:
        st.markdown(
            '<div class="nav-card"><h3>AI Assistant</h3>'
            "<p>Use the guided assistant to navigate the database "
            "and find relevant entities step by step.</p></div>",
            unsafe_allow_html=True,
        )
        if st.button("Open", key="goto_ai", use_container_width=True):
            st.session_state.page = "AI Assistant"
            st.rerun()

    with card3:
        st.markdown(
            '<div class="nav-card"><h3>Get in Touch</h3>'
            "<p>Every entity card includes a direct contact email. "
            "Use the database to reach potential collaborators.</p></div>",
            unsafe_allow_html=True,
        )
        if st.button("Open", key="goto_explore2", use_container_width=True):
            st.session_state.page = "Explore Database"
            st.rerun()

    # Entity type chart
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Entity Types in the Database")
    tc = df["Entity_Type"].value_counts().reset_index()
    tc.columns = ["Type", "Count"]
    st.bar_chart(tc.set_index("Type"))