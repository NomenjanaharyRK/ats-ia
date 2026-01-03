"""Service de scoring pour calculer la compatibilité entre CV et offres"""
from typing import Dict, List, Optional
from fuzzywuzzy import fuzz
import structlog

logger = structlog.get_logger(__name__)


class CVScorer:
    """Calcule le score de compatibilité entre un CV parsé et une offre"""
    
    # Pondérations pour le calcul du score final
    WEIGHTS = {
        "skills": 0.40,      # 40% - Le plus important
        "experience": 0.30,  # 30%
        "education": 0.20,   # 20%
        "languages": 0.10    # 10%
    }
    
    # Seuil de similarité pour fuzzy matching
    SIMILARITY_THRESHOLD = 70

    def calculate_score(self, parsed_cv: Dict, offer: Dict) -> Dict:
        """
        Calcule le score de compatibilité global
        
        Args:
            parsed_cv: CV parsé avec les informations extraites
            offer: Offre d'emploi avec les critères
            
        Returns:
            Dict avec le score global et les détails par catégorie
        """
        try:
            # Calculer les scores par catégorie
            skills_score = self._score_skills(
                parsed_cv.get("skills", []),
                offer.get("required_skills", [])
            )
            
            experience_score = self._score_experience(
                parsed_cv.get("experience_years"),
                offer.get("min_experience_years", 0)
            )
            
            education_score = self._score_education(
                parsed_cv.get("education", []),
                offer.get("required_education", [])
            )
            
            languages_score = self._score_languages(
                parsed_cv.get("languages", []),
                offer.get("required_languages", [])
            )
            
            # Calculer le score global pondéré
            matching_score = (
                skills_score * self.WEIGHTS["skills"] +
                experience_score * self.WEIGHTS["experience"] +
                education_score * self.WEIGHTS["education"] +
                languages_score * self.WEIGHTS["languages"]
            )
            
            return {
                "matching_score": round(matching_score, 2),
                "skills_score": round(skills_score, 2),
                "experience_score": round(experience_score, 2),
                "education_score": round(education_score, 2),
                "language_score": round(languages_score, 2),
                "scoring_details": {
                    "weights": self.WEIGHTS,
                    "cv_skills": parsed_cv.get("skills", []),
                    "required_skills": offer.get("required_skills", []),
                    "cv_experience": parsed_cv.get("experience_years"),
                    "required_experience": offer.get("min_experience_years", 0)
                }
            }
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score: {str(e)}")
            return self._empty_score()

    def _score_skills(self, cv_skills: List[str], required_skills: List[str]) -> float:
        """
        Score les compétences (40% du score total)
        Utilise le fuzzy matching pour gérer les variations
        """
        if not required_skills:
            return 100.0  # Si pas de compétences requises, score parfait
        
        if not cv_skills:
            return 0.0
        
        # Normaliser (lowercase)
        cv_skills_lower = [s.lower() for s in cv_skills]
        required_skills_lower = [s.lower() for s in required_skills]
        
        matched_skills = 0
        total_required = len(required_skills_lower)
        
        for required_skill in required_skills_lower:
            # Chercher une correspondance exacte d'abord
            if required_skill in cv_skills_lower:
                matched_skills += 1
                continue
            
            # Sinon, utiliser fuzzy matching
            best_match_score = 0
            for cv_skill in cv_skills_lower:
                similarity = fuzz.token_sort_ratio(required_skill, cv_skill)
                if similarity > best_match_score:
                    best_match_score = similarity
            
            # Si similarité suffisante, compter comme correspondance partielle
            if best_match_score >= self.SIMILARITY_THRESHOLD:
                matched_skills += (best_match_score / 100)
        
        # Calculer le score en pourcentage
        score = (matched_skills / total_required) * 100
        return min(score, 100.0)

    def _score_experience(self, cv_years: Optional[int], required_years: int) -> float:
        """
        Score l'expérience (30% du score total)
        """
        if required_years == 0:
            return 100.0  # Pas d'expérience requise
        
        if cv_years is None:
            return 50.0  # Score neutre si expérience non spécifiée
        
        if cv_years >= required_years:
            # Score parfait si expérience suffisante
            return 100.0
        else:
            # Score proportionnel si expérience insuffisante
            # Ex: 2 ans sur 5 requis = 40%
            score = (cv_years / required_years) * 100
            return min(score, 100.0)

    def _score_education(self, cv_education: List[str], required_education: List[str]) -> float:
        """
        Score l'éducation (20% du score total)
        """
        if not required_education:
            return 100.0  # Pas de formation requise
        
        if not cv_education:
            return 30.0  # Score faible si pas de formation spécifiée
        
        # Normaliser
        cv_education_lower = [e.lower() for e in cv_education]
        required_education_lower = [e.lower() for e in required_education]
        
        matched_count = 0
        total_required = len(required_education_lower)
        
        for required_edu in required_education_lower:
            best_match_score = 0
            
            for cv_edu in cv_education_lower:
                # Utiliser fuzzy matching pour les diplômes
                similarity = fuzz.partial_ratio(required_edu, cv_edu)
                if similarity > best_match_score:
                    best_match_score = similarity
            
            if best_match_score >= self.SIMILARITY_THRESHOLD:
                matched_count += (best_match_score / 100)
        
        score = (matched_count / total_required) * 100
        return min(score, 100.0)

    def _score_languages(self, cv_languages: List[str], required_languages: List[str]) -> float:
        """
        Score les langues (10% du score total)
        """
        if not required_languages:
            return 100.0  # Pas de langue requise
        
        if not cv_languages:
            return 0.0
        
        # Normaliser
        cv_languages_lower = [l.lower() for l in cv_languages]
        required_languages_lower = [l.lower() for l in required_languages]
        
        matched_count = 0
        total_required = len(required_languages_lower)
        
        for required_lang in required_languages_lower:
            if required_lang in cv_languages_lower:
                matched_count += 1
            else:
                # Fuzzy matching pour variations (ex: "anglais" vs "english")
                for cv_lang in cv_languages_lower:
                    if fuzz.ratio(required_lang, cv_lang) >= 80:
                        matched_count += 1
                        break
        
        score = (matched_count / total_required) * 100
        return min(score, 100.0)

    def _empty_score(self) -> Dict:
        """Retourne un score vide en cas d'erreur"""
        return {
            "matching_score": 0.0,
            "skills_score": 0.0,
            "experience_score": 0.0,
            "education_score": 0.0,
            "language_score": 0.0,
            "scoring_details": {}
        }


def score_cv_for_offer(parsed_cv: Dict, offer: Dict) -> Dict:
    """
    Fonction helper pour scorer un CV pour une offre
    
    Args:
        parsed_cv: CV parsé
        offer: Offre d'emploi
        
    Returns:
        Dict avec les scores
    """
    scorer = CVScorer()
    return scorer.calculate_score(parsed_cv, offer)
