import streamlit as st
from sections.utils import show_wip_badge

"""
sections/submit.py
Entry submission form. Edit FORM_FIELDS at the top to add or remove questions.
"""

# ── EDITABLE CONTENT ─────────────────────────────────────────────────────────

PAGE_TITLE    = "Submit an Entry"
PAGE_SUBTITLE = (
    "Are you part of the Geneva quantum ecosystem and not yet listed? "
    "Fill in the form below and we will review your submission."
)

# Each field: type in [text, textarea, select, checkbox]
# For select, provide an "options" list.
FORM_FIELDS = [
    {
        "key":      "entity_name",
        "label":    "Organisation / Group name",
        "type":     "text",
        "required": True,
    },
    {
        "key":      "entity_type",
        "label":    "Type of entity",
        "type":     "select",
        "options":  ["Research group", "Industry", "Facilitator", "Other"],
        "required": True,
    },
    {
        "key":      "one_liner",
        "label":    "One-liner description (max 200 characters)",
        "type":     "textarea",
        "required": True,
    },
    {
        "key":      "website",
        "label":    "Website URL",
        "type":     "text",
        "required": False,
    },
    {
        "key":      "contact_email",
        "label":    "Contact email",
        "type":     "text",
        "required": True,
    },
    {
        "key":      "open_to_collab",
        "label":    "Are you open to collaboration?",
        "type":     "checkbox",
        "required": False,
    },
]

SUBMIT_NOTICE = (
    "Thank you for your submission. "
    "We will review it and get back to you within a few days."
)

# ── FORM RENDERER ─────────────────────────────────────────────────────────────

def _render_field(field):
    """Render a single form field based on its type."""
    label = field["label"] + (" *" if field.get("required") else "")

    if field["type"] == "text":
        return st.text_input(label, key=field["key"])

    if field["type"] == "textarea":
        return st.text_area(label, key=field["key"], height=100)

    if field["type"] == "select":
        return st.selectbox(label, field["options"], key=field["key"])

    if field["type"] == "checkbox":
        return st.checkbox(label, key=field["key"])

    return None


def _validate(values):
    """Return a list of missing required field labels."""
    missing = []
    for field in FORM_FIELDS:
        if field.get("required"):
            val = values.get(field["key"])
            if not val or (isinstance(val, str) and not val.strip()):
                missing.append(field["label"])
    return missing


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

    st.markdown("Fields marked with * are required.")
    st.markdown("---")

    # Build form
    values = {}
    with st.form("submission_form", border=False):
        for field in FORM_FIELDS:
            values[field["key"]] = _render_field(field)

        submitted = st.form_submit_button(
            "Submit",
            width="stretch",
            type="primary",
        )

    # Handle submission
    if submitted:
        missing = _validate(values)
        if missing:
            st.error(
                "Please fill in the following required fields: "
                + ", ".join(missing)
            )
        else:
            st.success(SUBMIT_NOTICE)
            # TODO: replace with actual storage (database, email, Google Sheet...)
            with st.expander("Submitted data (debug view)"):
                st.json(values)