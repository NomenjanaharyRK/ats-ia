"""
Module de scoring entre une offre d'emploi (job_text) et un CV (cv_text).

- TF-IDF + cosinus
- Overlap de mots (historique)
- SBERT (embeddings)
- Pondération par quality_score
"""

import math
import re
from collections import Counter
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# SBERT : on garde l'import, mais la fonction elle-même doit être "safe"



WORD_RE = re.compile(r"\w+", re.UNICODE)

# Sprint 5: SBERT Similarity Function
from sentence_transformers import SentenceTransformer, util
import logging

# Charger le modèle SBERT une seule fois au démarrage du module
try:
    _sbert_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    _model_loaded = True
    logging.info("SBERT model loaded successfully")
except Exception as e:
    logging.error(f"Failed to load SBERT model: {e}")
    _sbert_model = None
    _model_loaded = False


def sbert_similarity(text1: str, text2: str) -> float:
    """
    Calcule la similarité sémantique entre deux textes en utilisant SBERT.
    
    Args:
        text1: Premier texte (description de poste)
        text2: Deuxième texte (texte du CV)
    
    Returns:
        float: Score de similarité entre 0.0 et 1.0
               Retourne 0.0 en cas d'erreur ou si le modèle n'est pas chargé
    """
    if not _model_loaded or not _sbert_model:
        logging.warning("SBERT model not loaded, returning 0.0")
        return 0.0
    
    if not text1 or not text2:
        logging.warning("Empty text provided to sbert_similarity")
        return 0.0
    
    try:
        # Encoder les deux textes en embeddings
        embedding1 = _sbert_model.encode(text1, convert_to_tensor=True)
        embedding2 = _sbert_model.encode(text2, convert_to_tensor=True)
        
        # Calculer la similarité cosinus entre les embeddings
        similarity = util.cos_sim(embedding1, embedding2)
        
        # Convertir en float et s'assurer que le score est entre 0 et 1
        score = float(similarity[0][0])
        score = max(0.0, min(score, 1.0))
        
        logging.debug(f"SBERT similarity calculated: {score:.4f}")
        return score
        
    except Exception as e:
        logging.error(f"Error in sbert_similarity: {e}")
        return 0.0



def _normalize(text: str) -> list[str]:
    text = text.lower()
    return WORD_RE.findall(text)


def keyword_overlap_score(job_text: str, cv_text: str) -> int:
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

    ratio = common / total_job
    score = math.floor(ratio * 100)
    return max(0, min(score, 100))


def _build_tfidf_vectorizer() -> TfidfVectorizer:
    stop_words = None
    return TfidfVectorizer(
        stop_words=stop_words,
        max_features=5000,
        ngram_range=(1, 2),
    )


def tfidf_cosine_scores(job_text: str, cv_texts: List[str]) -> List[float]:
    if not job_text or not cv_texts:
        return [0.0 for _ in cv_texts]

    documents = [job_text] + list(cv_texts)

    vectorizer = _build_tfidf_vectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    job_vec = tfidf_matrix[0:1]
    cv_vecs = tfidf_matrix[1:]

    sims = cosine_similarity(job_vec, cv_vecs)[0]
    return sims.tolist()


def combined_score(
    job_text: str,
    cv_text: str,
    quality_score: float | None = None,
    alpha: float = 0.5,
    sbert_weight: float = 0.6,
) -> float:
    # 1) TF-IDF (0..1)
    tfidf_scores = tfidf_cosine_scores(job_text, [cv_text])
    tfidf = tfidf_scores[0] if tfidf_scores else 0.0

    # 2) Overlap (0..1)
    overlap_raw = keyword_overlap_score(job_text, cv_text)
    overlap = overlap_raw / 100.0

    # 3) SBERT (0..1) - IMPORTANT: sbert_similarity doit renvoyer 0.0 si erreur
    semantic_sim = sbert_similarity(job_text, cv_text)

    # Logs
    print("DEBUG SCORING")
    print("TFIDF:", tfidf)
    print("OVERLAP_RAW:", overlap_raw)
    print("SBERT:", semantic_sim)
    print("QUALITY:", quality_score)

    # 4) Combinaison
    base_no_sbert = alpha * tfidf + (1.0 - alpha) * overlap
    base = sbert_weight * semantic_sim + (1.0 - sbert_weight) * base_no_sbert

    # 5) Pondération qualité
    if quality_score is not None:
        qs = max(0.0, min(quality_score, 1.0))
        factor = 0.9 + 0.1 * qs
        base = base * factor

    # 6) 0..100
    final = max(0.0, min(base * 100.0, 100.0))
    return final
