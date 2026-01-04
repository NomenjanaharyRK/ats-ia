from functools import lru_cache
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Chargement lazy du modèle - ne bloque pas le démarrage si HuggingFace est inaccessible
_model_cache = None

def get_sbert_model():
    """Charge le modèle sentence-transformer (avec gestion d'erreur réseau)"""
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    
    try:
        from sentence_transformers import SentenceTransformer
        _model_cache = SentenceTransformer(MODEL_NAME, device="cpu")
        print(f"✓ Modèle {MODEL_NAME} chargé avec succès")
        return _model_cache
    except Exception as e:
        print(f"⚠ Impossible de charger sentence-transformers: {e}")
        print("  Le scoring IA utilisera fuzzywuzzy uniquement")
        return None


def sbert_similarity(job_text: str, cv_text: str) -> float:
    if not job_text or not cv_text:
        return 0.0
    
    try:
        model = get_sbert_model()
        if model is None:
            # Fallback: pas de similarité sémantique disponible
            return 0.0
            
        vectors = model.encode(
            [job_text, cv_text],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return float(max(0.0, min(sim, 1.0)))
    except Exception as e:
        print("SBERT ERROR (fallback to 0.0):", repr(e))
        return 0.0
