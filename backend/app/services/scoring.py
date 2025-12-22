import math
import re
from collections import Counter
from typing import Tuple


WORD_RE = re.compile(r"\w+", re.UNICODE)


def _normalize(text: str) -> list[str]:
    """
    Normalise un texte : minuscule, extraction de tokens alphanumériques.
    """
    text = text.lower()
    return WORD_RE.findall(text)


def keyword_overlap_score(job_text: str, cv_text: str) -> int:
    """
    Scoring v1 :
    - calcule l'intersection de mots entre description d'offre et CV
    - renvoie un score entre 0 et 100 (borné).
    """
    if not job_text or not cv_text:
        return 0

    job_tokens = _normalize(job_text)
    cv_tokens = _normalize(cv_text)

    if not job_tokens or not cv_tokens:
        return 0

    job_counts = Counter(job_tokens)
    cv_counts = Counter(cv_tokens)

    # somme des min(count_job, count_cv) pour chaque mot de l’offre
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

    # bornage 0–100
    return max(0, min(score, 100))
