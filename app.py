import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quant@ct", page_icon="⚛️", layout="wide")

CSS = """
<style>
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #b0c4de !important;
    text-align: left !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    font-size: 0.95rem !important;
    transition: background 0.2s, color 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0,212,255,0.1) !important;
    color: #00d4ff !important;
}
/* Bouton actif */
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: rgba(0,212,255,0.15) !important;
    color: #00d4ff !important;
    border-left: 3px solid #00d4ff !important;
}
.hero h1 { font-size: 2.4rem; color: #00d4ff; }
.hero p  { font-size: 1.05rem; color: #b0c4de; line-height: 1.7; }
.stat-card {
    background: #1a1a2e; border: 1px solid rgba(0,212,255,0.2);
    border-radius: 12px; padding: 20px; text-align: center;
}
.stat-card h2 { font-size: 2rem; color: #00d4ff; margin: 0; }
.stat-card p  { color: #b0c4de; margin: 4px 0 0; font-size: 0.9rem; }
.entity-card {
    background: #1a1a2e; border: 1px solid #2a2a4a;
    border-radius: 12px; padding: 20px; margin-bottom: 16px;
}
.entity-card h3 { color: #00d4ff; margin: 0 0 6px; }
.entity-card .meta { color: #888; font-size: 0.85rem; margin-bottom: 10px; }
.entity-card .liner { color: #ccc; margin-bottom: 12px; }
.tag {
    display: inline-block; background: #0f3460; color: #00d4ff;
    border-radius: 20px; padding: 2px 10px; font-size: 0.78rem; margin: 2px;
}
.b-yes { background: #0d4a2e; color: #00e676; border-radius: 20px; padding: 2px 10px; font-size: 0.8rem; }
.b-no  { background: #4a1a1a; color: #ff5252; border-radius: 20px; padding: 2px 10px; font-size: 0.8rem; }
.coming {
    background: linear-gradient(135deg, #0f3460, #16213e);
    border: 2px dashed rgba(0,212,255,0.3); border-radius: 12px;
    padding: 60px 40px; text-align: center;
}
.nav-card {
    background: #1a1a2e;
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 12px;
    padding: 28px 24px 16px;
    margin-bottom: 8px;
    transition: border-color 0.2s, transform 0.2s;
    cursor: pointer;
}
.nav-card:hover {
    border-color: #00d4ff;
    transform: translateY(-2px);
}
.nav-card-icon { font-size: 2rem; margin-bottom: 12px; }
.nav-card h3 { color: #00d4ff; margin: 0 0 8px; font-size: 1.1rem; }
.nav-card p  { color: #888; font-size: 0.9rem; line-height: 1.5; margin: 0; }

.coming h3 { color: #00d4ff; font-size: 1.8rem; }
.coming p  { color: #888; }
a { color: #00d4ff !important; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_excel("MVP_Database.xlsx")
    for c in ["Tags", "Open_to_Collab", "Industry_experience"]:
        df[c] = df[c].fillna("Unknown").astype(str)
    return df


df = load_data()

# Remplace le st.radio par ça dans le sidebar :

with st.sidebar:
    st.markdown("## Quant@ct")
    st.markdown("---")

    # Navigation custom
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    nav_items = {
        "Home": "Home",
        "Explore Database": "Explore Database",
        "AI Assistant": "AI Assistant",
    }

    for key, label in nav_items.items():
        active = st.session_state.page == key
        if st.button(
            label,
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.page = key
            st.rerun()
# Pousse les icônes vers le bas
    st.markdown("<br>" * 8, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style="display:flex; gap:16px; padding:8px 4px;">
        <a href="https://www.linkedin.com/company/111068204" target="_blank"
           style="text-decoration:none; color:#b0c4de; font-size:1.5rem;" title="LinkedIn">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 0h-14C2.239 0 0 2.239 0 5v14c0 2.761 2.239 5 5 5h14c2.762 
                0 5-2.239 5-5V5c0-2.761-2.238-5-5-5zm-11 19H5v-11h3v11zm-1.5-12.268
                c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 
                1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 
                0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
            </svg>
        </a>
        <a href="mailto:quantact2revolution@gmail.com"
           style="text-decoration:none; color:#b0c4de; font-size:1.5rem;" title="Contact">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
                <path d="M0 3v18h24V3H0zm21.518 2L12 12.713 2.482 5h19.036zM2 
                19V7.183l10 8.104 10-8.104V19H2z"/>
            </svg>
        </a>
    </div>
    """, unsafe_allow_html=True)

    page = st.session_state.page  # remplace la variable page partout dans le code

# ── HOME ──────────────────────────────────────────────────────────────────────
if page == "Home":
    st.markdown(
        '<div class="hero"><h1> Quant@ct Hub</h1>'
        "<p>We build bridges between academic research and industry in Geneva around the field of Quantum.<br>"
        "Discover research groups, industries, and facilitators pushing the frontier of quantum science.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    total  = len(df)
    types  = df["Entity_Type"].nunique()
    collab = (df["Open_to_Collab"].str.lower() == "yes").sum()
    locs   = df["Location"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    for col, v, label in [
        (c1, total, "Entities"),
        (c2, types, "Entity Types"),
        (c3, collab, "Open to Collaboration"),
        (c4, locs,   "Locations"),
    ]:
        col.markdown(
            f'<div class="stat-card"><h2>{v}</h2><p>{label}</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### How to use this platform")
    st.markdown("### Where do you want to go?")
    card1, card2, card3 = st.columns(3)

    with card1:
        st.markdown("""
        <div class="nav-card">
            <h3>Explore Database</h3>
            <p>Filter by type, location, tags, and collaboration status to find the right group.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open →", key="goto_explore", use_container_width=True):
            st.session_state.page = "Explore Database"
            st.rerun()

    with card2:
        st.markdown("""
        <div class="nav-card">
            <h3>AI Assistant</h3>
            <p>Ask natural-language questions to navigate the database intelligently.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open →", key="goto_ai", use_container_width=True):
            st.session_state.page = "AI Assistant"
            st.rerun()

    with card3:
        st.markdown("""
        <div class="nav-card">
            <h3>Get in Touch</h3>
            <p>Every entity card includes a direct contact email. Use the database to find collaborators.</p>
        </div>
        """, unsafe_allow_html=True)
    
        st.link_button("Go to Explore →", url="", disabled=True)
    st.markdown("### Entity Types in the Database")
    tc = df["Entity_Type"].value_counts().reset_index()
    tc.columns = ["Type", "Count"]
    st.bar_chart(tc.set_index("Type"))


# ── EXPLORE ───────────────────────────────────────────────────────────────────
elif page == "Explore Database":
    st.markdown("## Explore the Database")
    st.caption("Filter and search across all entities in the Geneva quantum ecosystem.")

    with st.expander("Filters", expanded=True):
        r1, r2, r3 = st.columns(3)
        with r1:
            sel_types = st.multiselect("Entity Type", sorted(df["Entity_Type"].dropna().unique()), placeholder="All types")
        with r2:
            sel_locs  = st.multiselect("Location", sorted(df["Location"].dropna().unique()), placeholder="All locations")
        with r3:
            sel_col   = st.multiselect("Open to Collaboration", sorted(df["Open_to_Collab"].dropna().unique()), placeholder="All")

        all_tags = sorted({t.strip() for raw in df["Tags"] for t in raw.split(",") if t.strip()})
        sel_tags = st.multiselect("Research Topics / Tags", all_tags, placeholder="Select topics...")
        kw = st.text_input("Keyword search (name or description)", "")

    filt = df.copy()
    if sel_types: filt = filt[filt["Entity_Type"].isin(sel_types)]
    if sel_locs:  filt = filt[filt["Location"].isin(sel_locs)]
    if sel_col:   filt = filt[filt["Open_to_Collab"].isin(sel_col)]
    if sel_tags:  filt = filt[filt["Tags"].apply(lambda t: any(tg.lower() in t.lower() for tg in sel_tags))]
    if kw:
        q = kw.lower()
        filt = filt[
            filt["Entity_Name"].str.lower().str.contains(q, na=False)
            | filt["One_Liner"].str.lower().str.contains(q, na=False)
        ]

    st.markdown(f"**{len(filt)} result(s) found**")
    st.markdown("---")

    if filt.empty:
        st.warning("No results found. Try broadening your filters.")
    else:
        for _, row in filt.iterrows():
            tags_html = " ".join(
                f'<span class="tag">{t.strip()}</span>'
                for t in row["Tags"].split(",") if t.strip()
            )
            cv = str(row["Open_to_Collab"]).lower()
            cb = ('<span class="b-yes">Open to collaboration</span>' if cv == "yes"
                  else '<span class="b-no">Not open</span>' if cv == "no"
                  else '<span style="color:#888">Unknown</span>')
            ind = (' <span style="color:#ffd740;font-size:0.8rem">Industry exp.</span>'
                   if str(row["Industry_experience"]).lower() == "yes" else "")
            ws = str(row.get("Website", ""))
            wl = f'<a href="{ws}" target="_blank">Website</a> &nbsp; ' if ws.startswith("http") else ""
            em = str(row.get("Contact_email", ""))
            nm = str(row.get("Contact_Name", ""))
            el = f'<a href="mailto:{em}">{nm}</a>' if "@" in em else ""

            st.markdown(
                f'<div class="entity-card">'
                f"<h3>{row['Entity_Name']}</h3>"
                f'<div class="meta">{row["Entity_Type"]} &middot;{row["Location"]} &middot; {cb}{ind}</div>'
                f'<div class="liner">{row["One_Liner"]}</div>'
                f'<div style="margin-bottom:10px">{tags_html}</div>'
                f'<div style="font-size:0.88rem">{wl}{el}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    with st.expander("Raw table"):
        st.dataframe(filt, use_container_width=True)


# ── AI ASSISTANT ──────────────────────────────────────────────────────────────
elif page == "AI Assistant":
    st.markdown("## AI Assistant")
    st.caption("Ask anything about the Geneva quantum research ecosystem in natural language.")

    st.info(
        "Examples: *'Which groups work on superconductivity and are open to collaboration?'* "
        "— *'Find contacts with industry experience in quantum materials.'*"
    )

    st.markdown(
        '<div class="coming"><h3>Coming Soon</h3>'
        "<p>The chatbot is under development. It will use an LLM connected to the live database "
        "to answer your questions intelligently in natural language.</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Planned capabilities")
    p1, p2 = st.columns(2)
    p1.success("Natural language search over the full database")
    p1.success("Multi-criteria reasoning (e.g. 'open to collab + superconductivity')")
    p2.success("Suggested contacts based on your research interests")
    p2.success("Plain-English summaries of each research group")