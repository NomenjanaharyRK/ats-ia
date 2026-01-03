"""Service de parsing de CV utilisant spaCy pour extraction d'informations"""
import re
import spacy
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)

# Charger le modèle français de spaCy
try:
    nlp = spacy.load("fr_core_news_md")
except OSError:
    logger.error("Modèle spaCy fr_core_news_md non trouvé. Installer avec: python -m spacy download fr_core_news_md")
    raise


class CVParser:
    """Parser de CV pour extraire les informations structurées"""
    
    # Mots-clés pour identifier les sections
    EXPERIENCE_KEYWORDS = ["expérience", "experience", "professionnelle", "emploi", "poste"]
    EDUCATION_KEYWORDS = ["formation", "éducation", "education", "diplôme", "diplome", "études", "etudes"]
    SKILLS_KEYWORDS = ["compétences", "competences", "skills", "技能", "技術", "technical skills"]
    LANGUAGES_KEYWORDS = ["langues", "languages", "idiomas"]
    
    # Patterns regex
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    PHONE_PATTERN = r'(?:\+?\d{1,3}[-\s]?)?(?:\(\d{1,4}\)[-\s]?)?\d{1,4}[-\s]?\d{1,4}[-\s]?\d{1,9}'
    
    # Liste de compétences techniques communes
    TECH_SKILLS = [
        "python", "java", "javascript", "c++", "c#", "php", "ruby", "go", "rust",
        "react", "angular", "vue", "nodejs", "django", "flask", "fastapi", "spring",
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
        "git", "ci/cd", "jenkins", "gitlab", "github",
        "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
        "data science", "pandas", "numpy", "matplotlib"
    ]

    def __init__(self):
        self.nlp = nlp

    def parse(self, text: str) -> Dict:
        """
        Parse le texte du CV et extrait les informations structurées
        
        Args:
            text: Texte brut du CV
            
        Returns:
            Dict avec les informations extraites
        """
        try:
            doc = self.nlp(text.lower())
            
            return {
                "full_name": self.extract_name(text),
                "email": self.extract_email(text),
                "phone": self.extract_phone(text),
                "skills": self.extract_skills(text),
                "experience_years": self.extract_experience_years(text),
                "education": self.extract_education(text),
                "languages": self.extract_languages(text)
            }
        except Exception as e:
            logger.error(f"Erreur lors du parsing du CV: {str(e)}")
            return self._empty_result()

    def extract_name(self, text: str) -> Optional[str]:
        """Extrait le nom complet (généralement dans les premières lignes)"""
        try:
            lines = text.strip().split('\n')
            # Le nom est souvent dans les 3 premières lignes
            for line in lines[:3]:
                line = line.strip()
                # Ignorer les lignes trop courtes ou avec des symboles
                if 5 <= len(line) <= 50 and not re.search(r'[0-9@]', line):
                    doc = self.nlp(line)
                    # Chercher des entités PERSON
                    for ent in doc.ents:
                        if ent.label_ == "PER":
                            return ent.text.title()
                    # Si pas d'entité, prendre la première ligne valide
                    if len(line.split()) >= 2:
                        return line.title()
            return None
        except Exception as e:
            logger.warning(f"Erreur extraction nom: {str(e)}")
            return None

    def extract_email(self, text: str) -> Optional[str]:
        """Extrait l'adresse email"""
        match = re.search(self.EMAIL_PATTERN, text)
        return match.group(0) if match else None

    def extract_phone(self, text: str) -> Optional[str]:
        """Extrait le numéro de téléphone"""
        matches = re.findall(self.PHONE_PATTERN, text)
        if matches:
            # Prendre le premier qui ressemble à un numéro valide
            for match in matches:
                # Filtrer les numéros trop courts
                digits = re.sub(r'\D', '', match)
                if len(digits) >= 9:
                    return match
        return None

    def extract_skills(self, text: str) -> List[str]:
        """Extrait les compétences techniques"""
        skills = []
        text_lower = text.lower()
        
        # Chercher les compétences connues
        for skill in self.TECH_SKILLS:
            if skill in text_lower:
                skills.append(skill.title())
        
        # Chercher dans une section dédiée
        skills_section = self._extract_section(text, self.SKILLS_KEYWORDS)
        if skills_section:
            # Extraire les mots pertinents
            doc = self.nlp(skills_section.lower())
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2:
                    skill_text = token.text.title()
                    if skill_text not in skills and not token.is_stop:
                        skills.append(skill_text)
        
        return list(set(skills))[:20]  # Limiter à 20 compétences

    def extract_experience_years(self, text: str) -> Optional[int]:
        """Estime les années d'expérience"""
        # Chercher des patterns comme "5 ans d'expérience", "3 years"
        patterns = [
            r'(\d+)\s*(?:ans?|years?)\s*(?:d\')?(?:expérience|experience)',
            r'(?:expérience|experience)\s*:?\s*(\d+)\s*(?:ans?|years?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        # Compter les dates d'expérience (approche alternative)
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        if len(years) >= 2:
            # Calculer l'écart entre la plus ancienne et la plus récente
            years_int = [int(y) for y in years]
            return max(years_int) - min(years_int)
        
        return None

    def extract_education(self, text: str) -> List[str]:
        """Extrait les diplômes et formations"""
        education = []
        
        # Mots-clés de diplômes
        degree_keywords = [
            "master", "licence", "bachelor", "doctorat", "phd", "mba",
            "ingénieur", "ingenieur", "bts", "dut", "deug"
        ]
        
        text_lower = text.lower()
        for keyword in degree_keywords:
            if keyword in text_lower:
                # Trouver le contexte autour du mot-clé
                idx = text_lower.find(keyword)
                context = text[max(0, idx-10):min(len(text), idx+50)]
                education.append(context.strip())
        
        # Chercher dans la section éducation
        edu_section = self._extract_section(text, self.EDUCATION_KEYWORDS)
        if edu_section:
            lines = [l.strip() for l in edu_section.split('\n') if l.strip()]
            education.extend(lines[:5])  # Prendre les 5 premières lignes
        
        return list(set(education))[:5]  # Limiter à 5 formations

    def extract_languages(self, text: str) -> List[str]:
        """Extrait les langues parlées"""
        languages = []
        
        common_languages = [
            "français", "francais", "anglais", "english", "espagnol", "spanish",
            "allemand", "german", "italien", "italian", "portugais", "portuguese",
            "chinois", "chinese", "arabe", "arabic", "japonais", "japanese"
        ]
        
        text_lower = text.lower()
        for lang in common_languages:
            if lang in text_lower:
                # Normaliser le nom
                lang_normalized = {
                    "français": "Français", "francais": "Français",
                    "anglais": "Anglais", "english": "Anglais",
                    "espagnol": "Espagnol", "spanish": "Espagnol",
                    "allemand": "Allemand", "german": "Allemand",
                    "italien": "Italien", "italian": "Italien",
                    "portugais": "Portugais", "portuguese": "Portugais",
                    "chinois": "Chinois", "chinese": "Chinois",
                    "arabe": "Arabe", "arabic": "Arabe",
                    "japonais": "Japonais", "japanese": "Japonais"
                }.get(lang, lang.title())
                
                if lang_normalized not in languages:
                    languages.append(lang_normalized)
        
        return languages

    def _extract_section(self, text: str, keywords: List[str]) -> Optional[str]:
        """Extrait une section du CV basée sur des mots-clés"""
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                start_idx = text_lower.find(keyword)
                # Trouver la fin de la section (prochain titre ou 500 caractères)
                end_idx = start_idx + 500
                
                # Chercher le prochain titre de section
                next_section_keywords = self.EXPERIENCE_KEYWORDS + self.EDUCATION_KEYWORDS + \
                                      self.SKILLS_KEYWORDS + self.LANGUAGES_KEYWORDS
                
                for next_keyword in next_section_keywords:
                    if next_keyword != keyword:
                        next_idx = text_lower.find(next_keyword, start_idx + len(keyword))
                        if next_idx != -1 and next_idx < end_idx:
                            end_idx = next_idx
                
                return text[start_idx:end_idx]
        
        return None

    def _empty_result(self) -> Dict:
        """Retourne un résultat vide en cas d'erreur"""
        return {
            "full_name": None,
            "email": None,
            "phone": None,
            "skills": [],
            "experience_years": None,
            "education": [],
            "languages": []
        }
