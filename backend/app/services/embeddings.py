from functools import lru_cache

from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache(maxsize=1)
def get_sbert_model():
    # Import ici pour éviter des problèmes d'import au démarrage
    from sentence_transformers import SentenceTransformer

    # Forcer CPU
    return SentenceTransformer(MODEL_NAME, device="cpu")


def sbert_similarity(job_text: str, cv_text: str) -> float:
    if not job_text or not cv_text:
        return 0.0

    try:
        model = get_sbert_model()
        vectors = model.encode(
            [job_text, cv_text],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return float(max(0.0, min(sim, 1.0)))
    except Exception as e:
        # IMPORTANT: ne jamais faire tomber l'API
        print("SBERT ERROR (fallback to 0.0):", repr(e))
        return 0.0
