import streamlit as st
from sections.utils import show_wip_badge
"""
sections/about.py
About Us page. Edit the content variables at the top of this file.
"""
# ── EDITABLE CONTENT ─────────────────────────────────────────────────────────
# Edit the variables below to update the page. No Streamlit knowledge needed.

PAGE_TITLE = "About QuantAct"

PAGE_SUBTITLE = (
    "Bridging academic research and industry in the Geneva quantum ecosystem."
)

MISSION_TITLE = "Our Mission"
MISSION_TEXT = """
Blablabla
"""

STORY_TITLE = "Our Story"
STORY_TEXT = """
BlaBla
"""

TEAM_TITLE = "The Team"
TEAM_MEMBERS = [
    {
        "name":  "Name Surname",
        "role":  "Co-founder",
        "linkedin": "https://linkedin.com",
    },
    {
        "name":  "Name Surname",
        "role":  "Co-founder",
        "linkedin": "https://linkedin.com",
    },
]

CONTACT_TITLE = "Get in Touch"
CONTACT_TEXT  = "Have a question or want to collaborate? Reach out to us."
CONTACT_EMAIL = "quantact2revolution@gmail.com"
LINKEDIN_URL  = "https://www.linkedin.com/company/111068204"

# ── PAGE RENDER ───────────────────────────────────────────────────────────────

def render():

    show_wip_badge()

    # Hero
    st.markdown(
        f'<div class="hero">'
        f"<h1>{PAGE_TITLE}</h1>"
        f"<p>{PAGE_SUBTITLE}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Mission
    st.markdown(f"### {MISSION_TITLE}")
    st.markdown(MISSION_TEXT)
    st.markdown("---")

    # Story
    st.markdown(f"### {STORY_TITLE}")
    st.markdown(STORY_TEXT)
    st.markdown("---")

    # Team
    st.markdown(f"### {TEAM_TITLE}")
    cols = st.columns(len(TEAM_MEMBERS))
    for col, member in zip(cols, TEAM_MEMBERS):
        col.markdown(
            f'<div class="stat-card">'
            f'<h2 style="font-size:1.1rem">{member["name"]}</h2>'
            f'<p>{member["role"]}</p>'
            f'<a href="{member["linkedin"]}" target="_blank" '
            f'style="font-size:0.85rem">LinkedIn</a>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Contact
    st.markdown(f"### {CONTACT_TITLE}")
    st.markdown(CONTACT_TEXT)
    c1, c2 = st.columns(2)
    c1.link_button("Send us an email", url=f"mailto:{CONTACT_EMAIL}", width="stretch")
    c2.link_button("Follow us on LinkedIn", url=LINKEDIN_URL, width="stretch")