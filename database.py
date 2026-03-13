import pandas as pd
import streamlit as st

"""
database.py
Centralized data access layer for the Quant@ct application.

Responsibilities:
- Loading and caching the Excel database
- Defining column names and their display labels
- Normalizing raw data (filling NaN, splitting multi-value fields)
- Providing filter functions used by explore.py and assistant.py
- Exposing helper functions to extract unique values for UI widgets

To adapt to a new data source (SQLite, Supabase, etc.), only this file
needs to change — the rest of the application remains untouched.
"""

# -- Configuration ------------------------------------------------------------

DB_PATH  = "MVP_Database_V2.xlsx"
DB_SHEET = "Horizontal"

# Separator used in multi-value text columns (Tags, Quantum_Field, etc.)
MULTI_VALUE_SEP = "/"

# Columns that contain multiple values separated by MULTI_VALUE_SEP
MULTI_VALUE_COLS = [
    "Tags",
    "Quantum_Field",
    "Technology_Focus",
    "Core_Expertise",
    "Secondary_Expertise",
    "Looking_For",
    "Offers",
]

# Columns filled with "Unknown" when empty
FILLNA_UNKNOWN_COLS = [
    "Open_To_Collaboration",
    "Industry_experience",
    "TRL",
]

# -- Column registry ----------------------------------------------------------
# Maps internal column name -> display label shown in the UI.
# Add or rename entries here to update the entire app at once.

COLUMNS = {
    # Identity
    "entity_id":        "Entity_ID",
    "name":             "Entity_Name",
    "entity_type":      "Entity_Type",
    "sub_type":         "Sub_Type",
    "affiliation":      "Affiliation",
    "country":          "Country / Region",
    "one_liner":        "One liner",

    # Tags & topics
    "tags":             "Tags",
    "quantum_field":    "Quantum_Field",
    "tech_focus":       "Technology_Focus",
    "trl":              "Technology Readiness Level (TRL)",
    "core_expertise":   "Core_Expertise",
    "secondary_exp":    "Secondary_Expertise",

    # Outputs
    "primary_output":   "Primary_Output",
    "publications":     "Key_Publications",
    "patents":          "Key_Patents",
    "flagship":         "Flagship_Technology",

    # Collaboration
    "open_to_collab":   "Open_To_Collaboration",
    "industry_exp":     "Industry_experience",
    "looking_for":      "Looking_For",
    "offers":           "Offers",
    "previous_partners":"Previous_Partners",

    # Business
    "funding_stage":    "Funding_Stage",
    "acad_ind_fit":     "Academia_Industry_Fit",
    "commercial":       "Commercial_Potential",
    "innovation":       "Innovation_Depth",
    "ecosystem":        "Ecosystem_Influence",
    "role":             "Role",
    "decision_maker":   "Decision_Maker",
    "hardware_access":  "Hardware_Access",
    "scalability":      "Scalability_Constraint",

    # Contact
    "website":          "Website",
    "email":            "Email",
    "contact_name":     "Contact_Name",
    "linkedin":         "LinkedIn",
}

# Shorthand accessor — use col("name") instead of COLUMNS["name"] in code
def col(key: str) -> str:
    """Return the raw DataFrame column name for a given registry key."""
    return COLUMNS[key]


# -- Filter definitions -------------------------------------------------------
# Each filter entry defines one UI widget on the Explore page.
# Add a new dict here to add a new filter — no other file needs to change.
#
# Keys:
#   key          : unique identifier (used in session_state)
#   label        : displayed in the UI
#   column       : col() key from the registry above
#   type         : "multiselect" | "select" | "toggle"
#   multi_value  : True if the column contains "/" separated values

FILTERS = [
    {
        "key":         "entity_type",
        "label":       "Entity Type",
        "column":      "entity_type",
        "type":        "multiselect",
        "multi_value": False,
    },
    {
        "key":         "sub_type",
        "label":       "Sub-type",
        "column":      "sub_type",
        "type":        "multiselect",
        "multi_value": False,
    },
    {
        "key":         "country",
        "label":       "Country / Region",
        "column":      "country",
        "type":        "multiselect",
        "multi_value": False,
    },
    {
        "key":         "open_to_collab",
        "label":       "Open to Collaboration",
        "column":      "open_to_collab",
        "type":        "multiselect",
        "multi_value": False,
    },
    {
        "key":         "quantum_field",
        "label":       "Quantum Field",
        "column":      "quantum_field",
        "type":        "multiselect",
        "multi_value": True,
    },
    {
        "key":         "trl",
        "label":       "Technology Readiness Level",
        "column":      "trl",
        "type":        "multiselect",
        "multi_value": False,
    },
    {
        "key":         "tags",
        "label":       "Research Topics / Tags",
        "column":      "tags",
        "type":        "multiselect",
        "multi_value": True,
    },
]


# -- Data loading -------------------------------------------------------------

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and normalize the database. Cached by Streamlit."""
    df = pd.read_excel(DB_PATH, sheet_name=DB_SHEET)
    df = _normalize(df)
    return df


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize raw DataFrame columns."""
    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

    # Fill NaN in collaboration/experience columns
    for c in FILLNA_UNKNOWN_COLS:
        raw = col(c) if c in COLUMNS else c
        if raw in df.columns:
            df[raw] = df[raw].fillna("Unknown").astype(str)

    # Fill remaining string NaN with empty string
    df[str_cols] = df[str_cols].fillna("")

    return df


# -- Unique value extraction --------------------------------------------------

def get_unique_values(df: pd.DataFrame, column_key: str, multi_value: bool = False) -> list:
    """
    Return sorted unique values for a given column.
    If multi_value=True, splits each cell on MULTI_VALUE_SEP before deduplicating.
    """
    raw_col = col(column_key)
    if raw_col not in df.columns:
        return []

    if multi_value:
        values = {
            item.strip()
            for cell in df[raw_col].dropna()
            for item in str(cell).split(MULTI_VALUE_SEP)
            if item.strip()
        }
    else:
        values = {v for v in df[raw_col].dropna() if str(v).strip()}

    return sorted(values)


def get_all_tags(df: pd.DataFrame) -> list:
    """Return all unique tags from the Tags column."""
    return get_unique_values(df, "tags", multi_value=True)


def get_all_quantum_fields(df: pd.DataFrame) -> list:
    """Return all unique quantum fields."""
    return get_unique_values(df, "quantum_field", multi_value=True)


# -- Filtering ----------------------------------------------------------------

def apply_filters(df: pd.DataFrame, active_filters: dict) -> pd.DataFrame:
    """
    Apply a dict of active filters to the DataFrame.

    active_filters format:
        { filter_key: [selected_value_1, selected_value_2, ...] }

    Only filters with non-empty selection lists are applied.
    Returns a filtered copy of the DataFrame.
    """
    filt = df.copy()

    for f in FILTERS:
        key        = f["key"]
        raw_col    = col(f["column"])
        multi      = f["multi_value"]
        selection  = active_filters.get(key, [])

        if not selection or raw_col not in filt.columns:
            continue

        if multi:
            # Match if any selected value appears in the cell (split on sep)
            mask = filt[raw_col].apply(
                lambda cell: any(
                    sel.lower() in [
                        item.strip().lower()
                        for item in str(cell).split(MULTI_VALUE_SEP)
                    ]
                    for sel in selection
                )
            )
        else:
            mask = filt[raw_col].isin(selection)

        filt = filt[mask]

    return filt


def apply_keyword_search(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    """
    Filter rows where keyword appears in name, one_liner, tags,
    quantum_field, or tech_focus (case-insensitive).
    """
    if not keyword.strip():
        return df

    q = keyword.lower()
    search_cols = [
        col("name"),
        col("one_liner"),
        col("tags"),
        col("quantum_field"),
        col("tech_focus"),
    ]
    existing_cols = [c for c in search_cols if c in df.columns]

    mask = pd.Series(False, index=df.index)
    for c in existing_cols:
        mask |= df[c].str.lower().str.contains(q, na=False)

    return df[mask]


def count_results(df: pd.DataFrame, active_filters: dict) -> int:
    """Return the number of rows matching active_filters."""
    return len(apply_filters(df, active_filters))