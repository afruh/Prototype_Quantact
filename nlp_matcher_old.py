"""
nlp_matcher.py  —  QuantAct NLP Matching Engine
================================================
Module OPTIONNEL et indépendant de Streamlit.
Peut être importé ou testé en CLI sans lancer l'application.

PIPELINE (3 étapes) :
  1. extract_keywords(query)   — RAKE ou tokenisation de secours
  2. extract_filters(query)    — keywords → dict compatible apply_filters()
  3. semantic_search(query)    — cosine similarity sur embeddings (si dispo)
  4. match(query)              — pipeline complet → (df_résultats, filtres, explication)

DÉPENDANCES OPTIONNELLES (requirements_nlp.txt) :
  pip install sentence-transformers rake-nltk
  - Sans sentence-transformers → keyword matching uniquement (mode dégradé)
  - Sans rake-nltk            → tokenisation simple (mode dégradé)
  - rapidfuzz est déjà utilisé par le projet (assistant.py)

INTÉGRATION DANS find_partners.py :
  from nlp_matcher import NLPMatcher, NLP_AVAILABLE

TEST CLI :
  python nlp_matcher.py "quantum sensors for biometric monitoring in wearables"
  python nlp_matcher.py --query "startup quantum computing Geneva" --top 5
"""

from __future__ import annotations

import sys
import time
import argparse
import numpy as np
import pandas as pd
from typing import Optional

# ── Dépendances optionnelles ──────────────────────────────────────────────────
try:
    from sentence_transformers import SentenceTransformer
    _ST_AVAILABLE = True
except ImportError:
    _ST_AVAILABLE = False

try:
    from rake_nltk import Rake
    import nltk
    _RAKE_AVAILABLE = True
except ImportError:
    _RAKE_AVAILABLE = False

try:
    from rapidfuzz import process as rfprocess, fuzz
    _FUZZY_AVAILABLE = True
except ImportError:
    _FUZZY_AVAILABLE = False

# ── Imports du projet ─────────────────────────────────────────────────────────
from database_old import (
    FILTERS,
    MULTI_VALUE_SEP,
    apply_filters,
    apply_keyword_search,
    get_unique_values,
    col as db_col,
)

# ── Constantes de matching ────────────────────────────────────────────────────

# Modèle léger : 22 MB, pas de GPU requis, ~50ms/requête
DEFAULT_MODEL = "all-MiniLM-L6-v2"

# Score cosine minimum pour inclure un résultat en mode sémantique
SEMANTIC_THRESHOLD = 0.15

# Seuil fuzzy pour la reconnaissance de tags (0-100)
FUZZY_TAG_THRESHOLD    = 58
FUZZY_TYPE_THRESHOLD   = 45
FUZZY_COUNTRY_THRESHOLD = 70

# Plage des scores affichés à l'utilisateur (55–97 %)
DISPLAY_SCORE_MIN = 55
DISPLAY_SCORE_MAX = 97

# Colonnes utilisées pour construire le corpus d'embedding
CORPUS_KEYS = [
    "name", "one_liner", "tags", "quantum_field",
    "tech_focus", "core_expertise", "secondary_exp",
]

# Heuristiques : mots-clés → catégorie d'entité (avant fuzzy-match sur les vraies valeurs)
ENTITY_TYPE_HINTS: dict[str, list[str]] = {
    "academia":    ["research", "lab", "laboratory", "university", "academic",
                    "institute", "professor", "phd", "scholar", "study",
                    "science", "fundamental", "theoretical"],
    "startup":     ["startup", "start-up", "early stage", "seed", "series a",
                    "spin-off", "spinoff", "venture", "deep tech", "founded"],
    "industry":    ["company", "corporate", "industry", "manufacturer",
                    "enterprise", "firm", "group", "corporation", "supplier"],
    "facilitator": ["fund", "funding", "investor", "incubator", "accelerator",
                    "facilitator", "legal", "ip", "patent", "foundation",
                    "agency", "grant", "support", "hub"],
}

# Heuristiques : mots-clés → niveau TRL indicatif
TRL_HINTS: dict[str, list[str]] = {
    "low":  ["fundamental", "basic research", "theoretical", "conceptual",
             "exploratory", "trl 1", "trl 2", "trl 3", "early research"],
    "mid":  ["prototype", "proof of concept", "poc", "demo", "pilot",
             "validation", "demonstrator", "breadboard",
             "trl 4", "trl 5", "trl 6"],
    "high": ["production", "deployment", "commercial", "market ready",
             "product", "operational", "system", "trl 7", "trl 8", "trl 9"],
}

# Mots qui signalent une préférence pour la collaboration ouverte
COLLAB_WORDS = [
    "collaborate", "collaboration", "partner", "partners", "partnering",
    "looking for", "seeking", "open to", "co-develop", "joint", "together",
]

# Stop-words pour la tokenisation simple (fallback sans RAKE)
STOPWORDS = {
    "a", "an", "the", "for", "to", "of", "in", "with", "and", "or", "we",
    "our", "my", "their", "is", "are", "by", "that", "this", "can", "need",
    "want", "looking", "using", "based", "use", "uses", "have", "has", "be",
    "on", "at", "from", "into", "through", "which", "who", "what", "how",
    "new", "some", "such", "it", "its", "we're", "i'm", "not", "but",
}


# ── Singleton module-level (évite de recharger le modèle à chaque appel) ─────
_singleton: Optional["NLPMatcher"] = None


def get_matcher(df: pd.DataFrame, model_name: str = DEFAULT_MODEL) -> "NLPMatcher":
    """
    Retourne un singleton NLPMatcher partagé pour toute la session.
    Appeler depuis Streamlit : matcher = get_matcher(df)
    """
    global _singleton
    if _singleton is None:
        _singleton = NLPMatcher(df, model_name=model_name)
    return _singleton


# ── Classe principale ─────────────────────────────────────────────────────────

class NLPMatcher:
    """
    Moteur NLP de matching pour QuantAct.

    Attributs publics :
      NLP_MODE    : "semantic" | "keyword"   — mode actif selon les dépendances
      model_name  : nom du modèle chargé (ou None)

    Méthodes principales :
      extract_keywords(query)  → list[str]
      extract_filters(query)   → dict   (compatible apply_filters)
      semantic_search(query)   → pd.DataFrame  (avec colonne _nlp_score)
      match(query)             → tuple(df, filters, explanation)
    """

    def __init__(self, df: pd.DataFrame, model_name: str = DEFAULT_MODEL):
        self.df          = df
        self.model_name  = model_name
        self.model       = None
        self._embeddings: Optional[np.ndarray] = None

        # Valeurs connues de la BD (chargées une fois)
        self._known: dict[str, list[str]] = {}
        self._load_known_values()

        # Chargement du modèle sémantique (si disponible)
        if _ST_AVAILABLE:
            self._load_model(model_name)
            self.NLP_MODE = "semantic"
        else:
            self.NLP_MODE = "keyword"

        # Téléchargement NLTK si RAKE disponible
        if _RAKE_AVAILABLE:
            for resource, path in [
                ("stopwords",  "corpora/stopwords"),
                ("punkt_tab",  "tokenizers/punkt_tab"),   # NLTK >= 3.9
                ("punkt",      "tokenizers/punkt"),        # NLTK < 3.9 fallback
            ]:
                try:
                    nltk.data.find(path)
                except LookupError:
                    nltk.download(resource, quiet=True)

    # ── Chargement interne ─────────────────────────────────────────────────────

    def _load_known_values(self) -> None:
        """Pré-charge toutes les valeurs uniques de chaque filtre."""
        for f in FILTERS:
            self._known[f["key"]] = get_unique_values(
                self.df, f["column"], f["multi_value"]
            )

    def _load_model(self, model_name: str) -> None:
        """Charge le modèle sentence-transformers et pré-calcule les embeddings."""
        self.model = SentenceTransformer(model_name)
        corpus = self._build_corpus()
        self._embeddings = self.model.encode(
            corpus,
            convert_to_numpy=True,
            show_progress_bar=False,
            batch_size=64,
        ).astype(np.float32)

    def _build_corpus(self) -> list[str]:
        """Construit un texte représentatif pour chaque entité de la BD."""
        corpus = []
        for _, row in self.df.iterrows():
            parts = []
            for key in CORPUS_KEYS:
                col_name = db_col(key)
                if col_name not in row.index:
                    continue
                val = str(row[col_name]).strip()
                if val.lower() in ("nan", "none", ""):
                    continue
                # Remplace le séparateur multi-valeur par un espace
                val = val.replace(MULTI_VALUE_SEP, " ")
                parts.append(val)
            corpus.append(". ".join(parts) if parts else "")
        return corpus

    # ── Extraction de mots-clés ────────────────────────────────────────────────

    def extract_keywords(self, query: str) -> list[str]:
        """
        Extrait les mots-clés de la requête.
        Utilise RAKE si disponible, sinon tokenisation simple.
        """
        if _RAKE_AVAILABLE:
            r = Rake(min_length=1, max_length=4)
            r.extract_keywords_from_text(query)
            phrases = r.get_ranked_phrases()
            # Ajoute aussi les tokens individuels pour ne pas rater des mots isolés
            single = [w.lower() for w in query.split()
                      if w.lower() not in STOPWORDS and len(w) > 2]
            seen: set[str] = set()
            result = []
            for p in phrases + single:
                if p not in seen:
                    seen.add(p)
                    result.append(p)
            return result[:15]
        else:
            tokens = [w.lower().strip(".,;:!?()-\"'")
                      for w in query.split()
                      if w.lower() not in STOPWORDS and len(w) > 2]
            return list(dict.fromkeys(tokens))[:15]

    # ── Extraction de filtres ──────────────────────────────────────────────────

    def extract_filters(self, query: str) -> dict[str, list[str]]:
        """
        Analyse la requête et retourne un dict de filtres
        directement compatible avec apply_filters() de database.py.

        Exemple :
          {"entity_type": ["Academia"], "tags": ["Quantum Sensing"], "trl": ["TRL 3"], ...}
        """
        q = query.lower()
        keywords = self.extract_keywords(query)
        result = {f["key"]: [] for f in FILTERS}

        # ── 1. Entity Type ────────────────────────────────────────────────────
        known_types = self._known.get("entity_type", [])
        for category, hints in ENTITY_TYPE_HINTS.items():
            if not any(h in q for h in hints):
                continue
            if not _FUZZY_AVAILABLE or not known_types:
                continue
            match = rfprocess.extractOne(
                category, known_types,
                scorer=fuzz.WRatio,
                score_cutoff=FUZZY_TYPE_THRESHOLD,
            )
            if match:
                result["entity_type"].append(match[0])
        result["entity_type"] = list(dict.fromkeys(result["entity_type"]))

        # ── 2. Tags ───────────────────────────────────────────────────────────
        known_tags = self._known.get("tags", [])
        matched_tags: set[str] = set()

        # a) Correspondance exacte tag ⊂ requête
        for tag in known_tags:
            if tag.lower() in q:
                matched_tags.add(tag)

        # b) Fuzzy match de chaque keyword contre tous les tags
        if _FUZZY_AVAILABLE and known_tags:
            for kw in keywords:
                if len(kw) < 3:
                    continue
                hits = rfprocess.extract(
                    kw, known_tags,
                    scorer=fuzz.WRatio,
                    limit=2,
                    score_cutoff=FUZZY_TAG_THRESHOLD,
                )
                for h in hits:
                    matched_tags.add(h[0])

        result["tags"] = list(matched_tags)[:6]

        # ── 3. Quantum Field ──────────────────────────────────────────────────
        known_qf = self._known.get("quantum_field", [])
        matched_qf: set[str] = set()

        for qf in known_qf:
            if qf.lower() in q:
                matched_qf.add(qf)

        if _FUZZY_AVAILABLE and known_qf:
            for kw in keywords:
                hits = rfprocess.extract(
                    kw, known_qf,
                    scorer=fuzz.WRatio,
                    limit=2,
                    score_cutoff=FUZZY_TAG_THRESHOLD,
                )
                for h in hits:
                    matched_qf.add(h[0])

        result["quantum_field"] = list(matched_qf)[:4]

        # ── 4. TRL ────────────────────────────────────────────────────────────
        known_trl = self._known.get("trl", [])
        if known_trl:
            for category, hints in TRL_HINTS.items():
                if not any(h in q for h in hints):
                    continue
                # Cherche dans les vraies valeurs TRL de la BD
                # (ex: "TRL 1-3", "research", "prototype"…)
                anchor = {"low": "1", "mid": "5", "high": "8"}[category]
                if _FUZZY_AVAILABLE:
                    hits = rfprocess.extract(
                        anchor, known_trl,
                        scorer=fuzz.partial_ratio,
                        limit=3,
                        score_cutoff=20,
                    )
                    for h in hits:
                        result["trl"].append(h[0])
                else:
                    result["trl"].extend(known_trl[:2])
            result["trl"] = list(dict.fromkeys(result["trl"]))[:4]

        # ── 5. Collaboration ──────────────────────────────────────────────────
        known_collab = self._known.get("open_to_collab", [])
        if any(w in q for w in COLLAB_WORDS) and known_collab:
            for val in known_collab:
                if val.lower() in ("yes", "oui", "true", "1"):
                    result["open_to_collab"] = [val]
                    break

        # ── 6. Country ────────────────────────────────────────────────────────
        known_countries = self._known.get("country", [])
        for country in known_countries:
            if country and len(country) > 2 and country.lower() in q:
                result["country"].append(country)
        result["country"] = list(dict.fromkeys(result["country"]))[:2]

        return result

    # ── Recherche sémantique ───────────────────────────────────────────────────

    def semantic_search(
        self, query: str, top_k: int = 20
    ) -> pd.DataFrame:
        """
        Retourne les top_k entités les plus similaires sémantiquement.
        Ajoute la colonne _nlp_score (float 0–1) au dataframe retourné.

        Si sentence-transformers n'est pas disponible, utilise
        apply_keyword_search() comme fallback.
        """
        if self.model is None or self._embeddings is None:
            result = apply_keyword_search(self.df, query).copy()
            result["_nlp_score"] = 0.70
            return result.head(top_k)

        # Embedding de la requête
        q_emb = self.model.encode(
            [query], convert_to_numpy=True, show_progress_bar=False
        )[0].astype(np.float32)

        # Similarité cosine vectorisée
        q_norm    = q_emb / (np.linalg.norm(q_emb) + 1e-8)
        ent_norms = self._embeddings / (
            np.linalg.norm(self._embeddings, axis=1, keepdims=True) + 1e-8
        )
        scores = ent_norms @ q_norm   # shape (n_entities,)

        df_copy = self.df.copy()
        df_copy["_nlp_score"] = scores.astype(float)

        return (
            df_copy[df_copy["_nlp_score"] >= SEMANTIC_THRESHOLD]
            .sort_values("_nlp_score", ascending=False)
            .head(top_k)
        )

    # ── Pipeline complet ───────────────────────────────────────────────────────

    def match(
        self,
        query: str,
        top_k: int = 12,
    ) -> tuple[pd.DataFrame, dict[str, list], dict]:
        """
        Pipeline principal.

        Retourne :
          result_df    : DataFrame top_k avec colonnes _nlp_score et _match_pct
          filters      : dict des filtres extraits (compatible apply_filters)
          explanation  : dict lisible par l'humain (pour l'UI)
        """
        # Étape 1 — extraction de filtres
        filters = self.extract_filters(query)

        # Étape 2 — recherche sémantique large
        semantic_df = self.semantic_search(query, top_k=min(len(self.df), top_k * 4))

        # Étape 3 — filtre les résultats sémantiques avec les filtres extraits
        active_filters = {k: v for k, v in filters.items() if v}
        if active_filters:
            filtered = apply_filters(semantic_df, active_filters)
        else:
            filtered = semantic_df

        # Étape 4 — si trop peu de résultats après filtrage, on relaxe
        if len(filtered) < max(3, top_k // 3):
            filtered = semantic_df

        result = filtered.head(top_k).copy()

        # Étape 5 — normalisation des scores en pourcentage lisible (55–97 %)
        if "_nlp_score" in result.columns and len(result) > 1:
            s        = result["_nlp_score"].values.astype(float)
            s_min, s_max = s.min(), s.max()
            span     = max(s_max - s_min, 1e-8)
            normalized = (s - s_min) / span
            result["_match_pct"] = (
                DISPLAY_SCORE_MIN + normalized * (DISPLAY_SCORE_MAX - DISPLAY_SCORE_MIN)
            ).astype(int)
        elif "_nlp_score" in result.columns and len(result) == 1:
            result["_match_pct"] = 76
        else:
            result["_match_pct"] = 70

        # Construction de l'explication pour l'UI
        explanation: dict = {
            "entity_types":    filters.get("entity_type", []),
            "tags":            filters.get("tags", []),
            "quantum_fields":  filters.get("quantum_field", []),
            "trl":             filters.get("trl", []),
            "collab":          filters.get("open_to_collab", []),
            "country":         filters.get("country", []),
            "mode":            self.NLP_MODE,
            "model":           self.model_name if self.model else None,
            "n_filters_active": len(active_filters),
            "n_results":        len(result),
            "relaxed":         len(filtered) < max(3, top_k // 3),
        }

        return result, filters, explanation

    # ── Utilitaires ────────────────────────────────────────────────────────────

    def status(self) -> dict:
        """Retourne l'état des composants pour diagnostic."""
        return {
            "sentence_transformers": _ST_AVAILABLE,
            "rake_nltk":             _RAKE_AVAILABLE,
            "rapidfuzz":             _FUZZY_AVAILABLE,
            "model_loaded":          self.model is not None,
            "embeddings_shape":      (
                self._embeddings.shape if self._embeddings is not None else None
            ),
            "n_entities":            len(self.df),
            "n_known_tags":          len(self._known.get("tags", [])),
            "n_known_entity_types":  len(self._known.get("entity_type", [])),
            "NLP_MODE":              self.NLP_MODE,
        }


# ── Indicateur public d'availability ─────────────────────────────────────────

NLP_AVAILABLE = True   # Ce module est importable → True
                       # find_partners.py gère le cas ImportError séparément


# ── CLI de test ───────────────────────────────────────────────────────────────

def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="QuantAct NLP Matcher — test CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python nlp_matcher.py "quantum sensors for biometric monitoring in wearables"
  python nlp_matcher.py --query "startup quantum computing Geneva" --top 5
  python nlp_matcher.py --status
        """,
    )
    parser.add_argument("query", nargs="?", default=None, help="Requête en texte libre")
    parser.add_argument("--query", "-q", dest="query_opt", default=None)
    parser.add_argument("--top",   "-n", type=int, default=8)
    parser.add_argument("--status",      action="store_true",
                        help="Affiche l'état des composants et quitte")
    args = parser.parse_args()

    query_text = args.query or args.query_opt

    # Chargement de la BD
    print("⏳ Chargement de la base de données…")
    from database_old import load_data
    df = load_data()
    print(f"   {len(df)} entités chargées.\n")

    # Instanciation
    print("⏳ Initialisation du NLPMatcher…")
    t0 = time.time()
    matcher = NLPMatcher(df)
    elapsed = time.time() - t0
    print(f"   Prêt en {elapsed:.1f}s  [mode: {matcher.NLP_MODE}]\n")

    if args.status:
        print("── STATUS ──────────────────────────────────────")
        for k, v in matcher.status().items():
            print(f"  {k:<28} {v}")
        sys.exit(0)

    if not query_text:
        print("Aucune requête fournie. Utilisez : python nlp_matcher.py \"votre requête\"")
        sys.exit(1)

    print(f"── REQUÊTE ─────────────────────────────────────")
    print(f"  \"{query_text}\"\n")

    # Extraction de mots-clés
    kw = matcher.extract_keywords(query_text)
    print(f"── MOTS-CLÉS EXTRAITS ({len(kw)}) ─────────────────")
    print(f"  {kw}\n")

    # Extraction de filtres
    filters = matcher.extract_filters(query_text)
    print("── FILTRES DÉTECTÉS ────────────────────────────")
    for k, v in filters.items():
        if v:
            print(f"  {k:<20} {v}")
    print()

    # Pipeline complet
    print(f"⏳ Recherche des {args.top} meilleurs résultats…")
    t1 = time.time()
    result_df, _, explanation = matcher.match(query_text, top_k=args.top)
    elapsed = time.time() - t1
    print(f"   Terminé en {elapsed:.2f}s\n")

    print(f"── RÉSULTATS ({len(result_df)}) ──────────────────────────")
    name_col  = "Entity_Name"
    type_col  = "Entity_Type"
    score_col = "_match_pct"

    for i, (_, row) in enumerate(result_df.iterrows(), 1):
        name  = str(row.get(name_col,  "?"))[:45]
        etype = str(row.get(type_col,  "?"))[:18]
        score = int(row.get(score_col, 0))
        print(f"  {i:2}. [{score:3d}%] {etype:<20} {name}")

    print()
    print(f"── EXPLICATION ─────────────────────────────────")
    for k, v in explanation.items():
        if v:
            print(f"  {k:<22} {v}")


if __name__ == "__main__":
    _cli()
