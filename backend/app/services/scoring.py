"""
Module de scoring entre une offre d'emploi (job_text) et un CV (cv_text).

Améliorations :
- Utilisation de TF-IDF pour la similarité sémantique (cosinus).
- Conservation du scoring historique par overlap de mots.
- Combinaison des deux scores + pondération par la qualité d'extraction.
"""

import math
import re
from collections import Counter
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Regex simple pour extraire des tokens alphanumériques (mots)
WORD_RE = re.compile(r"\w+", re.UNICODE)


# ---------------------------------------------------------------------------
# Fonctions utilitaires : normalisation & overlap (scoring v1)
# ---------------------------------------------------------------------------

def _normalize(text: str) -> list[str]:
    """
    Normalise un texte :
    - Passage en minuscules.
    - Extraction de tokens alphanumériques via une regex simple.

    Cette forme normalisée est utilisée pour le scoring v1
    (overlap de mots exacts entre l'offre et le CV).
    """
    text = text.lower()
    return WORD_RE.findall(text)


def keyword_overlap_score(job_text: str, cv_text: str) -> int:
    """
    Scoring v1 (historique) basé sur l'intersection de mots.

    Principe :
    - On tokenize l'offre et le CV.
    - On compte, pour chaque mot de l'offre, combien de fois il apparaît aussi dans le CV.
    - On calcule un ratio common / total_job, puis on le ramène à 0..100.

    Retour :
    - Entier entre 0 et 100.
    """
    if not job_text or not cv_text:
        return 0

    job_tokens = _normalize(job_text)
    cv_tokens = _normalize(cv_text)

    if not job_tokens or not cv_tokens:
        return 0

    job_counts = Counter(job_tokens)
    cv_counts = Counter(cv_tokens)

    common = 0
    total_job = 0
    for word, j_count in job_counts.items():
        total_job += j_count
        c_count = cv_counts.get(word, 0)
        common += min(j_count, c_count)

    if total_job == 0:
        return 0

    ratio = common / total_job  # entre 0 et 1
    score = math.floor(ratio * 100)

    # Bornage 0–100
    return max(0, min(score, 100))


# ---------------------------------------------------------------------------
# Nouveau scoring TF-IDF + cosinus (scoring v2)
# ---------------------------------------------------------------------------

def _build_tfidf_vectorizer() -> TfidfVectorizer:
    """
    Construit un TfidfVectorizer adapté à nos textes.

    IMPORTANT :
    - Le paramètre stop_words doit être :
      * une chaîne "english"
      * ou une LISTE de mots
      * ou None

    Pour éviter tout bug de type, on utilise ici stop_words=None,
    ce qui signifie : pas de stopwords filtrés côté scikit-learn.

    Plus tard, si tu veux ajouter des stopwords FR/EN :
    - construis une LISTE (ex: list(ENGLISH_STOP_WORDS) + list(FRENCH_STOP_WORDS))
    - et passe cette liste à stop_words.
    """
    stop_words = None  # TF-IDF brut, pas de filtrage de mots vides

    vectorizer = TfidfVectorizer(
        stop_words=stop_words,
        max_features=5000,
        ngram_range=(1, 2),  # unigrams + bigrams pour mieux capter les expressions
    )
    return vectorizer


def tfidf_cosine_scores(job_text: str, cv_texts: List[str]) -> List[float]:
    """
    Scoring v2 par similarité cosinus sur TF-IDF.

    Paramètres
    ----------
    job_text : str
        Description de l'offre.
    cv_texts : List[str]
        Liste de textes de CV à comparer à l'offre.

    Retour
    ------
    List[float]
        Pour chaque CV, une similarité cosinus entre 0.0 et 1.0
        par rapport à l'offre.
    """
    if not job_text or not cv_texts:
        return [0.0 for _ in cv_texts]

    # On construit la matrice TF-IDF sur [job] + [CV1, CV2, ...]
    documents = [job_text] + list(cv_texts)

    vectorizer = _build_tfidf_vectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Vecteur TF-IDF de l'offre
    job_vec = tfidf_matrix[0:1]
    # Vecteurs TF-IDF des CV
    cv_vecs = tfidf_matrix[1:]

    # Similarité cosinus entre l'offre et chaque CV
    sims = cosine_similarity(job_vec, cv_vecs)[0]
    # sims est un array de float entre 0 et 1
    return sims.tolist()


# ---------------------------------------------------------------------------
# Score combiné (TF-IDF + overlap + qualité)
# ---------------------------------------------------------------------------

def combined_score(
    job_text: str,
    cv_text: str,
    quality_score: float | None = None,
    alpha: float = 0.5,
) -> float:
    """
    Score final pour 1 CV par rapport à une offre.

    Composantes
    -----------
    - tfidf_cosine (principal, 0..1)
    - keyword_overlap_score (v1, converti en 0..1)
    - quality_score : pondération basée sur la qualité de l'extraction (0..1)

    Paramètres
    ----------
    job_text : str
        Texte de l'offre d'emploi.
    cv_text : str
        Texte du CV extrait (PDF/DOCX/image via OCR).
    quality_score : float | None
        Score de qualité d'extraction (0..1). Si None, pas de pondération.
    alpha : float
        Poids de TF-IDF vs overlap (alpha proche de 1 => TF-IDF dominant).

    Retour
    ------
    float
        Score final entre 0 et 100.
    """
    # 1. tf-idf pour ce CV seul (similarité cosinus 0..1)
    tfidf_scores = tfidf_cosine_scores(job_text, [cv_text])
    tfidf = tfidf_scores[0] if tfidf_scores else 0.0

    # 2. ancien score (overlap) normalisé 0..1
    overlap_raw = keyword_overlap_score(job_text, cv_text)
    overlap = overlap_raw / 100.0

    # Logs de debug (à retirer en prod si besoin)
    print("DEBUG SCORING")
    print("TFIDF:", tfidf)
    print("OVERLAP_RAW:", overlap)  # déjà normalisé 0..1
    print("QUALITY:", quality_score)

    # 3. combinaison TF-IDF + overlap
    #    alpha = poids de TF-IDF, (1 - alpha) = poids de l'overlap
    base = alpha * tfidf + (1.0 - alpha) * overlap

    # 4. pondération par quality_score (moins agressive)
    if quality_score is not None:
        # On s'assure que quality_score est dans [0, 1]
        qs = max(0.0, min(quality_score, 1.0))

        # Facteur entre 0.7 et 1.0 :
        # - si qs = 0.0 -> factor = 0.7 (pénalisation modérée)
        # - si qs = 1.0 -> factor = 1.0 (pas de pénalisation)
        factor = 0.9 + 0.1 * qs
        base = base * factor

    # 5. Bornage final en 0..100
    final = max(0.0, min(base * 100.0, 100.0))
    return final
