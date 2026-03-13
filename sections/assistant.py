import streamlit as st
from rapidfuzz import process, fuzz
from sections.utils import show_wip_badge
from database import count_results, get_unique_values, get_all_tags, col as db_col

"""
pages/assistant.py
Guided wizard assistant with fuzzy tag matching (no external API).
Flow: entity type -> collaboration -> topics -> results -> redirect to Explore.
"""

# -- Constants ----------------------------------------------------------------

STEPS = ["entity_type", "collaboration", "topics", "results"]


# -- Helpers ------------------------------------------------------------------

def _reset_wizard():
    st.session_state.wizard_step = 0
    st.session_state.wizard_filters = {
        "entity_type": [],
        "collaboration": [],
        "topics": [],
    }
    st.session_state.wizard_history = []


def _add_message(role, content):
    st.session_state.wizard_history.append({"role": role, "content": content})


def _render_history():
    for msg in st.session_state.wizard_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def _fuzzy_match_tags(user_input, all_tags, score_cutoff=60):
    """Return tags from all_tags that fuzzy-match the user input string."""
    if not user_input.strip():
        return []
    results = process.extract(
        user_input,
        all_tags,
        scorer=fuzz.WRatio,
        limit=5,
        score_cutoff=score_cutoff,
    )
    return [match[0] for match in results]

# -- Step renderers -----------------------------------------------------------

def _step_entity_type(df):
    entity_types = sorted({
        t.strip()
        for val in df[db_col("entity_type")].dropna()
        for t in str(val).split(" / ")
        if t.strip()
    })

    _add_message("assistant", "Hello! What type of entity are you looking for?")
    _render_history()

    with st.chat_message("assistant"):
        cols = st.columns(len(entity_types) + 1)
        for i, etype in enumerate(entity_types):
            if cols[i].button(etype, key=f"etype_{etype}", width="stretch"):
                st.session_state.wizard_filters["entity_type"] = [etype]
                _add_message("user", etype)
                st.session_state.wizard_step = 1
                st.rerun()
        if cols[-1].button("All types", key="etype_all", width="stretch"):
            st.session_state.wizard_filters["entity_type"] = []
            _add_message("user", "All types")
            st.session_state.wizard_step = 1
            st.rerun()


def _step_collaboration(df):
    _render_history()

    with st.chat_message("assistant"):
        st.markdown("Should the entity be open to collaboration?")
        c1, c2, c3 = st.columns(3)
        if c1.button("Yes", key="collab_yes", width="stretch"):
            st.session_state.wizard_filters["collaboration"] = ["Yes"]
            _add_message("user", "Open to collaboration")
            st.session_state.wizard_step = 2
            st.rerun()
        if c2.button("No", key="collab_no", width="stretch"):
            st.session_state.wizard_filters["collaboration"] = ["No"]
            _add_message("user", "Not open to collaboration")
            st.session_state.wizard_step = 2
            st.rerun()
        if c3.button("Does not matter", key="collab_any", width="stretch"):
            st.session_state.wizard_filters["collaboration"] = []
            _add_message("user", "No preference on collaboration")
            st.session_state.wizard_step = 2
            st.rerun()


def _step_topics(df):
    all_tags = get_unique_values(df, "tags", multi_value=True)

    _render_history()

    with st.chat_message("assistant"):
        st.markdown(
            "Any specific research topics? Click one or more tags, "
            "or type a term below (typos are fine)."
        )

        # -- Clickable tag buttons (grouped in rows of 5) ---------------------
        selected_topics = st.session_state.wizard_filters.get("topics", [])

        tag_cols_per_row = 5
        rows = [
            all_tags[i : i + tag_cols_per_row]
            for i in range(0, len(all_tags), tag_cols_per_row)
        ]
        for row in rows:
            cols = st.columns(len(row))
            for btn_col, tag in zip(cols, row):
                is_selected = tag in selected_topics
                label = f"+ {tag}" if not is_selected else f"x {tag}"
                if btn_col.button(label, key=f"tag_{tag}", width="stretch"):
                    if is_selected:
                        selected_topics.remove(tag)
                    else:
                        selected_topics.append(tag)
                    st.session_state.wizard_filters["topics"] = selected_topics
                    st.rerun()

        st.markdown("---")

        # -- Free text input with fuzzy matching ------------------------------
        user_text = st.text_input(
            "Or type a topic (e.g. supraconductivite, quantum optic...)",
            key="topic_text_input",
        )
        fuzzy_matches = []
        if user_text:
            fuzzy_matches = _fuzzy_match_tags(user_text, all_tags)
            if fuzzy_matches:
                st.caption(
                    f"Closest matches: {', '.join(fuzzy_matches)}"
                )
            else:
                st.caption("No close match found. Try a different term.")

        # -- Action buttons ---------------------------------------------------
        a1, a2, a3 = st.columns(3)

        if fuzzy_matches:
            if a1.button("Add matches", key="add_fuzzy", width="stretch"):
                for m in fuzzy_matches:
                    if m not in selected_topics:
                        selected_topics.append(m)
                st.session_state.wizard_filters["topics"] = selected_topics
                st.rerun()

        if selected_topics:
            summary = ", ".join(selected_topics)
            if a2.button(
                f"Continue with {len(selected_topics)} topic(s)",
                key="confirm_topics",
                width="stretch",
            ):
                _add_message("user", f"Topics: {summary}")
                st.session_state.wizard_step = 3
                st.rerun()

        if a3.button("Skip — show all", key="skip_topics", width="stretch"):
            st.session_state.wizard_filters["topics"] = []
            _add_message("user", "No topic filter")
            st.session_state.wizard_step = 3
            st.rerun()


def _step_results(df):
    filters = st.session_state.wizard_filters
    count = count_results(df, st.session_state.wizard_filters)

    _render_history()

    with st.chat_message("assistant"):
        if count == 0:
            st.warning(
                "No entities match your criteria. "
                "Try restarting with broader filters."
            )
        else:
            # Build a readable summary
            parts = []
            if filters["entity_type"]:
                parts.append(f"type: **{', '.join(filters['entity_type'])}**")
            if filters["collaboration"]:
                parts.append(f"collaboration: **{filters['collaboration'][0]}**")
            if filters["topics"]:
                parts.append(f"topics: **{', '.join(filters['topics'])}**")
            summary = " | ".join(parts) if parts else "no filters applied"

            st.markdown(
                f"I found **{count} result(s)** matching your search ({summary})."
            )

            c1, c2 = st.columns(2)
            if c1.button(
                f"View {count} result(s) in Explore",
                key="goto_explore_from_wizard",
                width="stretch",
                type="primary",
            ):
                # Push filters to session_state for explore.py to consume
                st.session_state.filter_entity_type    = filters["entity_type"]
                st.session_state.filter_tags           = filters["topics"]
                st.session_state.filter_open_to_collab = filters["collaboration"]
                st.session_state.page = "Explore Database"
                st.rerun()

            if c2.button("Start over", key="restart_wizard", width="stretch"):
                _reset_wizard()
                st.rerun()


# -- Main entry point ---------------------------------------------------------

def render(df):

    show_wip_badge()
    
    st.markdown("## AI Assistant")
    st.caption(
        "Answer a few questions and the assistant will find the right entities for you."
    )

    # Initialise state on first load
    if "wizard_step" not in st.session_state:
        _reset_wizard()

    step = st.session_state.wizard_step

    if step == 0:
        _step_entity_type(df)
    elif step == 1:
        _step_collaboration(df)
    elif step == 2:
        _step_topics(df)
    elif step == 3:
        _step_results(df)