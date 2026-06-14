"""
sections/find_partners.py
──────────────────────────
Page "Find Me Partners" — deux modes :

  🧠 NLP Mode  : NLPMatcher disponible → résultats réels de la BD
                 avec score sémantique, filtres extraits automatiquement
  📋 Demo Mode : fallback mock-data si nlp_matcher n'est pas installé

La sélection du mode est automatique (basée sur la disponibilité des deps)
avec un toggle manuel dans l'UI.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

# ── Import optionnel du moteur NLP ────────────────────────────────────────────
try:
    from nlp_matcher import NLPMatcher, NLP_AVAILABLE as _NLP_MODULE_OK
    _NLP_IMPORT_OK = True
except ImportError:
    _NLP_IMPORT_OK = False
    _NLP_MODULE_OK = False

# ── Card builder depuis ecosystem_explorer ────────────────────────────────────
try:
    from sections.ecosystem_explorer import _build_entity_card, _safe, _tag_html
    _CARD_IMPORT_OK = True
except ImportError:
    _CARD_IMPORT_OK = False

from database import col as db_col


# ════════════════════════════════════════════════════════════════════════════════
#  MOCK DATA — utilisé en mode démo si nlp_matcher n'est pas disponible
# ════════════════════════════════════════════════════════════════════════════════

MOCK_RESEARCH = [
    {
        "name": "UNIGE Quantum Photonics Lab",
        "affiliation": "University of Geneva",
        "tags": ["Quantum Optics", "Photonic Sensing", "Quantum Communication"],
        "trl": "TRL 3–5",
        "description": "Spécialise dans les interactions lumière-matière quantiques, applicable aux capteurs ultra-précis pour les dispositifs de surveillance biométrique et médicale.",
        "score": 95, "collab": True, "contact": "photonics@unige.ch",
    },
    {
        "name": "EPFL Quantum Sensing Center",
        "affiliation": "EPFL Lausanne",
        "tags": ["Quantum Sensors", "MEMS Integration", "Signal Processing"],
        "trl": "TRL 4–6",
        "description": "Recherche appliquée en capteurs quantiques reliant la physique fondamentale au matériel miniaturisé pour l'électronique grand public et les IoT de santé.",
        "score": 88, "collab": True, "contact": "sensing@epfl.ch",
    },
    {
        "name": "PSI Quantum Materials Group",
        "affiliation": "Paul Scherrer Institute",
        "tags": ["Quantum Materials", "Coherence", "Low-Temperature Physics"],
        "trl": "TRL 2–4",
        "description": "Recherche fondamentale sur la cohérence quantique dans de nouveaux matériaux, avec intérêt croissant pour les applications réelles de détection.",
        "score": 71, "collab": False, "contact": "qmaterials@psi.ch",
    },
]

MOCK_STARTUPS = [
    {
        "name": "QuantumPath AG",
        "stage": "Seed",
        "tags": ["Quantum Software", "Algorithm SDK", "Hardware Integration"],
        "trl": "TRL 5–7",
        "description": "Middleware d'algorithmes quantiques pour déploiement matériel, spécialisé dans le traitement des données de capteurs au niveau de la couche quantique.",
        "score": 91, "collab": True, "contact": "partnerships@quantumpath.ch",
    },
    {
        "name": "QSense Analytics",
        "stage": "Pre-Seed",
        "tags": ["Biometric Sensing", "Edge AI", "Wearable IoT"],
        "trl": "TRL 4–6",
        "description": "Combine les sorties de capteurs quantiques avec l'IA embarquée pour la surveillance biométrique en temps réel dans les appareils portables grand public.",
        "score": 84, "collab": True, "contact": "hello@qsense.io",
    },
]

MOCK_FACILITATORS = [
    {
        "name": "Innosuisse – Swiss Innovation Agency",
        "role": "Funding",
        "tags": ["R&D Grants", "Partnership Co-funding", "IP Strategy"],
        "description": "Agence fédérale d'innovation suisse offrant des subventions et co-financements pour les partenariats R&D academia-industrie en deep tech.",
        "score": 90, "contact": "contact@innosuisse.ch",
    },
    {
        "name": "Geneva Quantum Hub",
        "role": "Network / Incubation",
        "tags": ["Ecosystem Facilitation", "Introductions", "Events"],
        "description": "Connecte startups quantiques, groupes de recherche et industrie dans l'écosystème genevois. Événements bi-annuels de matchmaking.",
        "score": 85, "contact": "hub@genevatech.ch",
    },
]

REFINEMENT_LINES = [
    ("Domaine",          "Capteurs quantiques pour monitoring biométrique (contexte wearable / santé)"),
    ("Besoin clé",       "Intégration de capteurs au niveau quantique + expertise traitement du signal"),
    ("TRL idéal",        "Recherche (TRL 2–5) pour groupes académiques · Exécution (TRL 4–7) pour startups"),
    ("Contraintes",      "Capacité de miniaturisation · Design basse consommation · Expérience industrie"),
    ("Recherche",        "Groupes de recherche (science core) + Startups (exécution) + Facilitateurs (IP/financement)"),
]


# ════════════════════════════════════════════════════════════════════════════════
#  HELPERS COMMUNS
# ════════════════════════════════════════════════════════════════════════════════

def _score_class(score: int) -> str:
    if score >= 88: return "match-score match-score-high"
    if score >= 72: return "match-score match-score-mid"
    return "match-score match-score-low"


def _tags_html(tags: list) -> str:
    return " ".join(f'<span class="tag">{t}</span>' for t in tags)


def _section_header(icon: str, icon_cls: str, title: str, count: int) -> str:
    return (
        f'<div class="result-section-header">'
        f'<div class="result-section-icon {icon_cls}">{icon}</div>'
        f'<h3>{title}</h3>'
        f'<span class="result-section-count">{count}</span>'
        f'</div>'
    )


# ════════════════════════════════════════════════════════════════════════════════
#  MODE DÉMO — affichage mock data
# ════════════════════════════════════════════════════════════════════════════════

def _show_refinement_mock(query: str) -> None:
    st.markdown(
        f'<div class="refinement-box">'
        f'<strong>🤖 Consultant Parser · Requête analysée</strong><br><br>'
        + "".join(
            f'<span style="color:var(--t4);font-size:0.82rem">{k}&nbsp;&nbsp;</span>'
            f'<span style="color:var(--t2);font-size:0.88rem">{v}</span><br>'
            for k, v in REFINEMENT_LINES
        )
        + "</div>",
        unsafe_allow_html=True,
    )


def _show_mock_results(query: str) -> None:
    _show_refinement_mock(query)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin:8px 0 24px">'
        '<span style="color:var(--t4);font-size:0.88rem">Shortlist prête ·</span>'
        '<span style="color:var(--ok);font-size:0.88rem;font-weight:600">'
        "3 research groups &nbsp;·&nbsp; 2 startups &nbsp;·&nbsp; 2 facilitators"
        "</span></div>",
        unsafe_allow_html=True,
    )

    # Research groups
    st.markdown(
        _section_header("🔬", "icon-research", "Research Groups", len(MOCK_RESEARCH)),
        unsafe_allow_html=True,
    )
    for r in MOCK_RESEARCH:
        collab_badge = (
            '<span class="b-yes">Open to collaboration</span>'
            if r["collab"] else '<span class="b-no">Not open</span>'
        )
        st.markdown(
            f'<div class="match-card">'
            f'<div class="match-card-header">'
            f'<div><p class="match-card-name">{r["name"]}</p>'
            f'<p class="match-card-affil">{r["affiliation"]}</p></div>'
            f'<span class="{_score_class(r["score"])}">★ {r["score"]}%</span>'
            f'</div>'
            f'<p class="match-card-desc">{r["description"]}</p>'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:8px">'
            f'{_tags_html(r["tags"])} <span class="match-trl">{r["trl"]}</span>'
            f'{collab_badge}</div>'
            f'<div class="match-contact">✉ <a href="mailto:{r["contact"]}">{r["contact"]}</a></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Startups
    st.markdown(
        _section_header("🚀", "icon-startup", "Startups", len(MOCK_STARTUPS)),
        unsafe_allow_html=True,
    )
    for s in MOCK_STARTUPS:
        st.markdown(
            f'<div class="match-card">'
            f'<div class="match-card-header">'
            f'<div><p class="match-card-name">{s["name"]}</p>'
            f'<p class="match-card-affil">Startup · {s["stage"]}</p></div>'
            f'<span class="{_score_class(s["score"])}">★ {s["score"]}%</span>'
            f'</div>'
            f'<p class="match-card-desc">{s["description"]}</p>'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px">'
            f'{_tags_html(s["tags"])} <span class="match-stage">{s["stage"]}</span>'
            f'<span class="match-trl">{s["trl"]}</span></div>'
            f'<div class="match-contact">✉ <a href="mailto:{s["contact"]}">{s["contact"]}</a></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Facilitators
    st.markdown(
        _section_header("🤝", "icon-facil", "Facilitators", len(MOCK_FACILITATORS)),
        unsafe_allow_html=True,
    )
    for f in MOCK_FACILITATORS:
        st.markdown(
            f'<div class="match-card">'
            f'<div class="match-card-header">'
            f'<div><p class="match-card-name">{f["name"]}</p>'
            f'<p class="match-card-affil">Facilitator · {f["role"]}</p></div>'
            f'<span class="{_score_class(f["score"])}">★ {f["score"]}%</span>'
            f'</div>'
            f'<p class="match-card-desc">{f["description"]}</p>'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px">'
            f'{_tags_html(f["tags"])} <span class="match-role">{f["role"]}</span></div>'
            f'<div class="match-contact">✉ <a href="mailto:{f["contact"]}">{f["contact"]}</a></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Export CTA
    st.markdown(
        '<div class="export-card"><strong>📦 Export Partner Pack</strong>'
        "Génère un résumé structuré de tous les collaborateurs présélectionnés, "
        "prêt à partager avec votre équipe.</div>",
        unsafe_allow_html=True,
    )
    c1, c2, _ = st.columns([1, 1, 2])
    c1.button("📤 Export Partner Pack", disabled=True, width="stretch", key="mock_export")
    if c2.button("🔄 Nouvelle recherche", width="stretch", key="mock_reset"):
        st.session_state.fmp_show_results = False
        st.session_state.fmp_query = ""
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
#  MODE NLP — affichage résultats réels
# ════════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def _load_matcher_cached():
    """Charge NLPMatcher une seule fois pour toute la session Streamlit."""
    from database import load_data
    from nlp_matcher import NLPMatcher
    df = load_data()
    return NLPMatcher(df)


def _show_nlp_refinement(explanation: dict) -> None:
    """Affiche la box 'Consultant Parser' avec les vrais filtres détectés."""
    lines: list[tuple[str, str]] = []

    if explanation.get("entity_types"):
        lines.append(("Types détectés", ", ".join(explanation["entity_types"])))
    if explanation.get("tags"):
        lines.append(("Tags extraits", ", ".join(explanation["tags"])))
    if explanation.get("quantum_fields"):
        lines.append(("Champs quantiques", ", ".join(explanation["quantum_fields"])))
    if explanation.get("trl"):
        lines.append(("TRL inféré", ", ".join(explanation["trl"])))
    if explanation.get("collab"):
        lines.append(("Collaboration", "Ouvert à la collaboration"))
    if explanation.get("country"):
        lines.append(("Région", ", ".join(explanation["country"])))

    mode_label = (
        f'Semantic NLP · modèle `{explanation["model"]}`'
        if explanation["mode"] == "semantic"
        else "Keyword matching (installez sentence-transformers pour le mode sémantique)"
    )
    lines.append(("Méthode", mode_label))

    if explanation.get("relaxed"):
        lines.append(("ℹ️ Note", "Filtres relâchés — peu de résultats stricts, résultats sémantiques utilisés"))

    st.markdown(
        '<div class="refinement-box">'
        "<strong>🧠 NLP Parser · Analyse de la requête</strong><br><br>"
        + "".join(
            f'<span style="color:var(--t4);font-size:0.82rem">{k}&nbsp;&nbsp;</span>'
            f'<span style="color:var(--t2);font-size:0.88rem">{v}</span><br>'
            for k, v in lines
        )
        + "</div>",
        unsafe_allow_html=True,
    )


def _icon_for_type(entity_type: str) -> tuple[str, str]:
    """Retourne (emoji, css_class) selon le type d'entité."""
    t = entity_type.lower()
    if "acad" in t or "research" in t or "univers" in t:
        return "🔬", "icon-research"
    if "start" in t or "spin" in t:
        return "🚀", "icon-startup"
    if "facil" in t or "fund" in t or "invest" in t:
        return "🤝", "icon-facil"
    return "🏢", "icon-research"


def _nlp_score_badge(score: int) -> str:
    css = _score_class(score)
    return f'<span class="{css}">★ {score}%</span>'


def _show_nlp_results(
    result_df: pd.DataFrame,
    filters: dict,
    explanation: dict,
    query: str,
) -> None:
    """Affiche les résultats réels de la BD avec scores NLP, groupés par type."""

    _show_nlp_refinement(explanation)

    if result_df.empty:
        st.warning(
            "Aucun résultat trouvé pour cette requête. "
            "Essayez des termes plus généraux ou passez en mode Explore Ecosystem."
        )
        if st.button("🌐 Ouvrir Explore Ecosystem", key="nlp_goto_explore"):
            st.session_state.page = "Explore Ecosystem"
            st.rerun()
        return

    # Résumé
    type_col = db_col("entity_type")
    n = len(result_df)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:8px 0 24px">'
        f'<span style="color:var(--t4);font-size:0.88rem">Résultats ·</span>'
        f'<span style="color:var(--ok);font-size:0.88rem;font-weight:600">'
        f"{n} entité(s) correspondantes depuis la base de données"
        f"</span></div>",
        unsafe_allow_html=True,
    )

    # Groupement par type d'entité
    if type_col in result_df.columns:
        groups = result_df.groupby(type_col, sort=False)
        ordered_types = result_df[type_col].unique().tolist()
    else:
        groups = {"Entités": result_df}.items()
        ordered_types = ["Entités"]

    for etype in ordered_types:
        try:
            group_df = groups.get_group(etype)
        except Exception:
            group_df = result_df[result_df[type_col] == etype]

        icon, icon_cls = _icon_for_type(str(etype))
        st.markdown(
            _section_header(icon, icon_cls, str(etype), len(group_df)),
            unsafe_allow_html=True,
        )

        for _, row in group_df.iterrows():
            score = int(row.get("_match_pct", 70))
            score_html = _nlp_score_badge(score)

            # Utilise le card builder partagé si disponible, sinon version allégée
            if _CARD_IMPORT_OK:
                card_html = _build_entity_card(row)
                # Injecte le badge score dans le card header
                card_html = card_html.replace(
                    '<div class="entity-card">',
                    f'<div class="match-card">',
                    1,
                ).replace(
                    "</div>",
                    f'<div style="position:absolute;top:18px;right:18px">{score_html}</div>',
                    1,
                )
                # Wrap en position:relative pour le badge
                card_html = card_html.replace(
                    '<div class="match-card">',
                    '<div class="match-card" style="position:relative">',
                    1,
                )
                st.markdown(card_html, unsafe_allow_html=True)
            else:
                # Fallback inline card
                name     = str(row.get(db_col("name"),       "?"))
                affil    = str(row.get(db_col("affiliation"), ""))
                one_liner= str(row.get(db_col("one_liner"),   ""))
                tags_raw = str(row.get(db_col("tags"),        ""))
                country  = str(row.get(db_col("country"),     ""))
                email    = str(row.get(db_col("email"),       ""))

                tags_html = " ".join(
                    f'<span class="tag">{t.strip()}</span>'
                    for t in tags_raw.split(" / ")
                    if t.strip() and tags_raw not in ("nan", "")
                )
                email_html = (
                    f'<div class="match-contact">✉ <a href="mailto:{email}">{email}</a></div>'
                    if "@" in email else ""
                )
                affil_text = f"{affil} · {country}" if affil and country else (affil or country)
                desc = one_liner if one_liner not in ("nan", "") else ""

                st.markdown(
                    f'<div class="match-card" style="position:relative">'
                    f'<div style="position:absolute;top:14px;right:16px">{score_html}</div>'
                    f'<p class="match-card-name">{name}</p>'
                    f'<p class="match-card-affil">{affil_text}</p>'
                    f'<p class="match-card-desc">{desc}</p>'
                    f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px">'
                    f"{tags_html}</div>"
                    f"{email_html}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # Boutons CTA
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, _ = st.columns([1.2, 1.2, 1, 1.5])

    if c1.button("🌐 Voir dans Ecosystem", width="stretch", key="nlp_goto_eco", type="primary"):
        # Pré-remplit les filtres dans Explore Ecosystem
        active = {k: v for k, v in filters.items() if v}
        for k, v in active.items():
            st.session_state[f"filter_{k}"] = v
        st.session_state.page = "Explore Ecosystem"
        st.rerun()

    c2.button("📤 Export Partner Pack", disabled=True, width="stretch", key="nlp_export")

    if c3.button("🔄 Nouvelle recherche", width="stretch", key="nlp_reset"):
        st.session_state.fmp_show_results = False
        st.session_state.fmp_query = ""
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
#  MAIN RENDER
# ════════════════════════════════════════════════════════════════════════════════

def render(df: pd.DataFrame) -> None:
    st.markdown(
        '<div class="page-header"><h2>🔍 Find Me Partners</h2>'
        '<p class="page-subtitle">'
        "Décrivez votre projet ou défi technologique. La plateforme surface les "
        "groupes de recherche, startups et facilitateurs les plus pertinents."
        "</p></div>",
        unsafe_allow_html=True,
    )

    # ── Bannière de mode ──────────────────────────────────────────────────────
    if _NLP_IMPORT_OK:
        st.markdown(
            '<div class="demo-banner">'
            "🧠 <strong>Mode NLP disponible</strong> — résultats issus de la vraie base de données."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="demo-banner">'
            "📋 <strong>Mode démo</strong> — installez <code>sentence-transformers</code> "
            "et <code>rake-nltk</code> (requirements_nlp.txt) pour activer le NLP réel."
            "</div>",
            unsafe_allow_html=True,
        )

    # Session state
    if "fmp_show_results" not in st.session_state:
        st.session_state.fmp_show_results = False
    if "fmp_query" not in st.session_state:
        st.session_state.fmp_query = ""
    if "fmp_use_nlp" not in st.session_state:
        st.session_state.fmp_use_nlp = _NLP_IMPORT_OK

    # ── ÉTAPE 1 : Saisie ─────────────────────────────────────────────────────
    if not st.session_state.fmp_show_results:

        # Toggle NLP / Demo
        if _NLP_IMPORT_OK:
            col_toggle, _ = st.columns([2, 3])
            st.session_state.fmp_use_nlp = col_toggle.toggle(
                "🧠 Utiliser le NLP (données réelles)",
                value=st.session_state.fmp_use_nlp,
                key="fmp_nlp_toggle",
            )

        st.markdown('<div class="fmp-input-box"><h3>Décrivez votre besoin</h3>', unsafe_allow_html=True)

        examples = [
            "Smartwatch powered by quantum sensors for biometric monitoring",
            "Quantum communication for secure industrial data transfer",
            "Quantum computing partner for drug discovery optimization",
        ]
        st.caption("Exemples :")
        ex_cols = st.columns(len(examples))
        for col_w, ex in zip(ex_cols, examples):
            if col_w.button(ex, key=f"ex_{ex[:18]}", width="stretch"):
                st.session_state.fmp_query = ex

        query = st.text_area(
            "Votre projet",
            value=st.session_state.fmp_query,
            height=110,
            placeholder=(
                "Ex : We are developing a smartwatch powered by quantum sensors for "
                "biometric monitoring. We need research groups with expertise in quantum "
                "sensing and startups that can help with hardware integration…"
            ),
            key="fmp_query_input",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2, _ = st.columns([1.3, 1, 2.7])
        go = c1.button("🔍 Trouver des partenaires", type="primary", width="stretch", key="fmp_go")
        if c2.button("Effacer", width="stretch", key="fmp_clear"):
            st.session_state.fmp_query = ""
            st.rerun()

        if go:
            if not query.strip():
                st.warning("Veuillez décrire votre projet avant de lancer la recherche.")
            else:
                use_nlp = st.session_state.get("fmp_use_nlp", False)
                label   = "Analyse NLP en cours…" if use_nlp else "Simulation en cours…"
                with st.spinner(label):
                    if use_nlp and _NLP_IMPORT_OK:
                        # Pré-charge le matcher (mis en cache par @st.cache_resource)
                        try:
                            _load_matcher_cached()
                        except Exception as e:
                            st.error(f"Erreur NLP : {e}")
                            return
                    else:
                        import time; time.sleep(1.0)
                st.session_state.fmp_query = query
                st.session_state.fmp_show_results = True
                st.rerun()

        with st.expander("💡 Conseils pour de meilleurs résultats"):
            st.markdown(
                """
                - **Soyez spécifique** : mentionnez le domaine d'application, le type de technologie, le contexte d'intégration.
                - **Incluez les contraintes** : limitations matérielles, budget, calendrier, préférence géographique.
                - **Décrivez ce que vous apportez** : votre expertise, IP ou infrastructure aide le moteur à calibrer.
                - **Précisez votre stade** : exploration précoce vs intégration prête à déployer.
                """
            )

    # ── ÉTAPE 2 : Résultats ───────────────────────────────────────────────────
    else:
        query = st.session_state.fmp_query
        query_display = query[:90] + ("…" if len(query) > 90 else "")
        st.markdown(
            f'<div style="background:oklch(0.57 0.22 303 / 0.07);border-radius:8px;'
            f'padding:10px 16px;margin-bottom:16px;font-size:0.88rem;color:var(--t3)">'
            f'<strong style="color:var(--a300)">Requête :</strong> {query_display}</div>',
            unsafe_allow_html=True,
        )

        use_nlp = st.session_state.get("fmp_use_nlp", False) and _NLP_IMPORT_OK

        if use_nlp:
            with st.spinner("Recherche sémantique en cours…"):
                try:
                    matcher = _load_matcher_cached()
                    result_df, filters, explanation = matcher.match(query, top_k=12)
                except Exception as e:
                    st.error(f"Erreur NLP : {e}. Basculement en mode démo.")
                    _show_mock_results(query)
                    return
            _show_nlp_results(result_df, filters, explanation, query)
        else:
            _show_mock_results(query)
