"""
sections/partner_journey.py
─────────────────────────────
Core UX : A Partner's Journey
Visual, non-functional narrative of the 4 key platform steps.
Each step is selectable and shows an expanded mock UI panel.
"""

import streamlit as st

# ── Journey step definitions ───────────────────────────────────────────────────

STEPS = [
    {
        "num": "01",
        "icon": "🗂️",
        "title": "Project Workspace",
        "tagline": "Your mission control for every collaboration",
        "description": (
            "Once logged in, users get a persistent workspace where they can save "
            "searches, build partner shortlists, and collaborate asynchronously with "
            "teammates — all without leaving the platform."
        ),
        "features": [
            ("Saved Searches",       "Bookmark filtered views to revisit as the ecosystem evolves."),
            ("Shortlisted Partners", "Curate a focused list of actors across research, startups, and facilitators."),
            ("Team Collaboration",   "Invite teammates to comment, annotate, and co-edit shortlists."),
            ("Activity Feed",        "Track changes: new actors added, profiles updated, new publications."),
        ],
        "mock_ui": "workspace",
    },
    {
        "num": "02",
        "icon": "👤",
        "title": "Partner Dashboard",
        "tagline": "Deep-dive into any actor's profile",
        "description": (
            "Each actor in the ecosystem has a structured profile showing their "
            "capabilities, technology readiness, publications, patents, and past "
            "collaborations — all in one scannable view."
        ),
        "features": [
            ("Capabilities",          "Structured list of expertise domains and quantum sub-fields."),
            ("Publications & Patents", "Auto-aggregated from public sources (arXiv, EPO, Google Scholar)."),
            ("Technology Readiness",   "TRL estimate derived from outputs — research to deployment."),
            ("Collaboration History",  "Past partnerships with industry, funding obtained, spin-offs."),
        ],
        "mock_ui": "dashboard",
    },
    {
        "num": "03",
        "icon": "📨",
        "title": "Introduction Request",
        "tagline": "One click to a structured opening message",
        "description": (
            "Rather than a cold email, the platform generates a structured one-pager "
            "contextualizing your request: your problem statement, constraints, "
            "expectations, and proposed next steps — ready for both parties."
        ),
        "features": [
            ("Problem Statement",   "Auto-filled from your original query and workspace context."),
            ("Constraints",         "Timeline, budget range, IP preferences, and geographic scope."),
            ("Expected Deliverable", "Jointly defined next step: call, NDA, feasibility study, PoC."),
            ("One-click Send",       "Introduction is sent to both parties with a shared context doc."),
        ],
        "mock_ui": "introduction",
    },
    {
        "num": "04",
        "icon": "📦",
        "title": "Partner Pack Export",
        "tagline": "Share your shortlist with your team or board",
        "description": (
            "Export a structured summary of all shortlisted collaborators into a "
            "shareable document — actor profiles, match rationale, TRL, contact info, "
            "and suggested next steps — ready for internal review or investor sharing."
        ),
        "features": [
            ("Structured PDF/Notion",  "Clean export with all actor cards formatted for sharing."),
            ("Match Rationale",        "Explains why each actor was selected for your specific need."),
            ("Suggested Next Steps",   "Actionable recommendations per actor (email, event, PoC)."),
            ("Version History",        "Track how your shortlist evolved and who reviewed it."),
        ],
        "mock_ui": "export",
    },
]


# ── Mock UI panels ─────────────────────────────────────────────────────────────

def _mock_workspace() -> str:
    return (
        '<div class="ui-preview">'
        '<div class="ui-preview-header">PROJECT WORKSPACE · My Quantum Sensing Project</div>'
        '<div class="ui-row"><span class="ui-dot-blue">📁</span> Saved Searches <span style="margin-left:auto;color:#5B4F7A">3 saved</span></div>'
        '<div class="ui-row"><span class="ui-dot-green">✅</span> Shortlisted Partners <span style="margin-left:auto;color:#5B4F7A">7 actors</span></div>'
        '<div class="ui-row"><span class="ui-dot-amber">👥</span> Team Members <span style="margin-left:auto;color:#5B4F7A">Kateřina, Sara, +2</span></div>'
        '<div class="ui-row"><span style="color:#5B4F7A;font-size:0.8rem">🕐 Last activity: 2 hours ago</span></div>'
        '<div class="ui-btn-mock">Open Workspace →</div>'
        "</div>"
    )


def _mock_dashboard() -> str:
    return (
        '<div class="ui-preview">'
        '<div class="ui-preview-header">PARTNER PROFILE · EPFL Quantum Sensing Center</div>'
        '<div class="ui-row"><span class="ui-dot-blue">🔬</span> Expertise <span style="margin-left:auto;color:#A78BFA">Quantum Sensors, MEMS</span></div>'
        '<div class="ui-row"><span class="ui-dot-green">📄</span> Publications <span style="margin-left:auto;color:#5B4F7A">47 peer-reviewed</span></div>'
        '<div class="ui-row"><span class="ui-dot-amber">⚙️</span> TRL Estimate <span style="margin-left:auto;color:#6EE7B7">TRL 4–6</span></div>'
        '<div class="ui-row"><span class="ui-dot-blue">🤝</span> Open to collab <span style="margin-left:auto;color:#34D399">Yes</span></div>'
        '<div class="ui-row"><span class="ui-dot-amber">📍</span> Location <span style="margin-left:auto;color:#5B4F7A">Lausanne, Switzerland</span></div>'
        '<div class="ui-btn-mock">Send Introduction →</div>'
        "</div>"
    )


def _mock_introduction() -> str:
    return (
        '<div class="ui-preview">'
        '<div class="ui-preview-header">INTRODUCTION REQUEST · Draft</div>'
        '<div class="ui-row"><span class="ui-dot-blue">💬</span> Problem <span style="margin-left:auto;color:#C4B5FD;font-size:0.78rem">Quantum sensing for wearable…</span></div>'
        '<div class="ui-row"><span class="ui-dot-amber">⚠️</span> Constraints <span style="margin-left:auto;color:#C4B5FD;font-size:0.78rem">Q3 2025 · Swiss IP</span></div>'
        '<div class="ui-row"><span class="ui-dot-green">🎯</span> Next step <span style="margin-left:auto;color:#C4B5FD;font-size:0.78rem">30-min discovery call</span></div>'
        '<div class="ui-row"><span style="color:#5B4F7A;font-size:0.8rem">Status: Draft → awaiting review</span></div>'
        '<div class="ui-btn-mock">Send Introduction →</div>'
        "</div>"
    )


def _mock_export() -> str:
    return (
        '<div class="ui-preview">'
        '<div class="ui-preview-header">PARTNER PACK · My Quantum Sensing Project</div>'
        '<div class="ui-row"><span class="ui-dot-blue">🔬</span> EPFL Quantum Sensing Center <span style="margin-left:auto;color:#6EE7B7;font-size:0.78rem">TRL 4–6</span></div>'
        '<div class="ui-row"><span class="ui-dot-green">🚀</span> QSense Analytics <span style="margin-left:auto;color:#6EE7B7;font-size:0.78rem">Seed stage</span></div>'
        '<div class="ui-row"><span class="ui-dot-amber">🤝</span> Innosuisse Grant Office <span style="margin-left:auto;color:#FCD34D;font-size:0.78rem">Funding</span></div>'
        '<div class="ui-row"><span style="color:#5B4F7A;font-size:0.8rem">3 actors · generated Jun 2025</span></div>'
        '<div class="export-card"><strong>📤 Export Ready</strong>PDF · Notion · Slides</div>'
        "</div>"
    )


MOCK_UI_FN = {
    "workspace":    _mock_workspace,
    "dashboard":    _mock_dashboard,
    "introduction": _mock_introduction,
    "export":       _mock_export,
}


# ── Step card ──────────────────────────────────────────────────────────────────

def _step_card_header(step: dict, is_active: bool) -> str:
    active_cls = "active" if is_active else ""
    return (
        f'<div class="journey-step {active_cls}">'
        f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:10px;">'
        f'<div class="journey-step-num">{step["num"]}</div>'
        f'<div>'
        f'<p class="journey-step-title">{step["icon"]} {step["title"]}</p>'
        f'<span style="color:#7C6FA0;font-size:0.82rem;">{step["tagline"]}</span>'
        f'</div>'
        f'</div>'
        f'<p class="journey-step-desc">{step["description"]}</p>'
        f'</div>'
    )


def _features_list(features: list[tuple[str, str]]) -> str:
    items = "".join(
        f'<div class="journey-feature">'
        f'<div class="journey-feature-dot"></div>'
        f'<div class="journey-feature-text">'
        f'<strong style="color:#E9D5FF">{name}</strong> — {detail}'
        f'</div>'
        f'</div>'
        for name, detail in features
    )
    return (
        '<div style="background:#120d28;border:1px solid rgba(139,92,246,0.16);'
        'border-radius:10px;padding:18px 20px;margin-top:4px;">'
        + items
        + "</div>"
    )


# ── Main render ────────────────────────────────────────────────────────────────

def render(df) -> None:  # noqa: ANN001
    st.markdown(
        '<div class="page-header">'
        "<h2>🗺️ Partner's Journey</h2>"
        '<p class="page-subtitle">'
        "Every interaction on QuantAct guides users toward actionable outcomes. "
        "This is what the platform experience looks like — from first search to "
        "final handshake."
        "</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="demo-banner">'
        "⚡ <strong>Concept view</strong> — this page illustrates the intended UX flow. "
        "Select a step to explore its details."
        "</div>",
        unsafe_allow_html=True,
    )

    # Active step state
    if "journey_step" not in st.session_state:
        st.session_state.journey_step = 0

    # ── Top overview: 4 step pills ──────────────────────────────────────────────
    pill_cols = st.columns(4)
    for i, step in enumerate(STEPS):
        is_active = st.session_state.journey_step == i
        label = f'{step["num"]} · {step["title"]}'
        if pill_cols[i].button(
            label,
            key=f"journey_pill_{i}",
            type="primary" if is_active else "secondary",
            width="stretch",
        ):
            st.session_state.journey_step = i
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Active step detail ──────────────────────────────────────────────────────
    active = STEPS[st.session_state.journey_step]
    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        # Step header card
        st.markdown(_step_card_header(active, is_active=True), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Features
        st.markdown(
            '<p style="font-size:0.78rem;font-weight:700;letter-spacing:0.08em;'
            'text-transform:uppercase;color:#5B4F7A;margin-bottom:8px;">WHAT THIS STEP INCLUDES</p>',
            unsafe_allow_html=True,
        )
        st.markdown(_features_list(active["features"]), unsafe_allow_html=True)

    with right:
        # Mock UI panel
        st.markdown(
            '<p style="font-size:0.78rem;font-weight:700;letter-spacing:0.08em;'
            'text-transform:uppercase;color:#5B4F7A;margin-bottom:8px;">INTERFACE PREVIEW</p>',
            unsafe_allow_html=True,
        )
        mock_fn = MOCK_UI_FN.get(active["mock_ui"], lambda: "")
        st.markdown(mock_fn(), unsafe_allow_html=True)

        # Step navigation buttons
        st.markdown("<br>", unsafe_allow_html=True)
        nav_l, nav_r = st.columns(2)
        if nav_l.button(
            "← Previous",
            key="journey_prev",
            disabled=(st.session_state.journey_step == 0),
            width="stretch",
        ):
            st.session_state.journey_step -= 1
            st.rerun()
        if nav_r.button(
            "Next →",
            key="journey_next",
            disabled=(st.session_state.journey_step == len(STEPS) - 1),
            width="stretch",
            type="primary",
        ):
            st.session_state.journey_step += 1
            st.rerun()

    # ── Full journey overview (collapsed) ───────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋 See all steps at a glance"):
        for i, step in enumerate(STEPS):
            is_active = i == st.session_state.journey_step
            cols = st.columns([0.08, 0.92])
            cols[0].markdown(
                f'<div class="journey-step-num" style="margin:4px 0;">{step["num"]}</div>',
                unsafe_allow_html=True,
            )
            cols[1].markdown(
                f'<div style="padding:8px 0;border-bottom:1px solid rgba(139,92,246,0.1);">'
                f'<strong style="color:{"#A78BFA" if is_active else "#E9D5FF"}">'
                f'{step["icon"]} {step["title"]}</strong> '
                f'<span style="color:#7C6FA0;font-size:0.85rem;">— {step["tagline"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if i < len(STEPS) - 1:
                st.markdown(
                    '<div style="display:flex;padding:2px 0 2px 20px;">'
                    '<span style="color:#2a1f4a;font-size:1.2rem;">│</span></div>',
                    unsafe_allow_html=True,
                )

    # ── Journey principle footer ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="background:linear-gradient(135deg,#100d22,#1e1245);'
        'border:1px solid rgba(139,92,246,0.25);border-radius:14px;'
        'padding:28px 36px;text-align:center;">'
        '<p style="color:#A78BFA;font-size:1.15rem;font-weight:600;margin-bottom:8px;">'
        "Translate → Structure → Connect"
        "</p>"
        '<p style="color:#7C6FA0;font-size:0.9rem;max-width:560px;margin:0 auto;line-height:1.7;">'
        "Every step in the partner journey is designed to reduce friction and increase "
        "actionability. QuantAct is not a directory — it's a collaboration engine."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )
