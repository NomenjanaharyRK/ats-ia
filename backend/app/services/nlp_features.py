import spacy
from functools import lru_cache

@lru_cache(maxsize=1)
def get_nlp():
    return spacy.load("fr_core_news_md")

def extract_skills(text: str, skills_list: list[str]) -> set[str]:
    nlp = get_nlp()
    doc = nlp(text.lower())
    tokens = {t.lemma_ for t in doc if not t.is_stop}
    return {s for s in skills_list if s.lower() in tokens}

def years_of_experience(text: str) -> int:
    # heuristique simple, à améliorer
    import re
    matches = re.findall(r"(\d+)\s+ans? d'expérience", text.lower())
    return max((int(m) for m in matches), default=0)
