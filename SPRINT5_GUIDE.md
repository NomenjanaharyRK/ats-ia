SPRINT5_GUIDE.md# 🚀 SPRINT 5: IA - SCORING & MATCHING INTELLIGENT

## 📋 Vue d'ensemble

**Objectif**: Transformer votre ATS en un système intelligent qui parse automatiquement les CV et calcule un score de compatibilité avec chaque offre.

**Valeur Business**: ⭐⭐⭐ CRITIQUE - C'est le cœur de votre différenciation concurrentielle!

**Durée estimée**: 2-3 jours

**Technologies**: 
- spaCy (NLP français)
- Algorithme de scoring personnalisé
- PostgreSQL pour stockage structuré

---

## 🎯 Fonctionnalités

- ✅ Extraction automatique: nom, email, téléphone, compétences, années d'expérience, éducation, langues
- ✅ Score de compatibilité 0-100% basé sur les critères de l'offre
- ✅ Breakdown détaillé du score (compétences 40%, expérience 30%, éducation 20%, langues 10%)
- ✅ API endpoint pour trier les candidatures par score
- ✅ Intégration avec le pipeline Celery existant

---

## 📦 ÉTAPE 1: Installation des dépendances

### 1.1 Mettre à jour `backend/requirements.txt`

Ajoutez ces lignes à la fin du fichier:

```txt
# Sprint 5: IA Scoring & Matching
spacy==3.7.2
https://github.com/explosion/spacy-models/releases/download/fr_core_news_md-3.7.0/fr_core_news_md-3.7.0-py3-none-any.whl
python-Levenshtein==0.25.0
fuzzywuzzy==0.18.0
```

### 1.2 Installer les dépendances

```bash
cd backend
docker-compose exec backend pip install spacy==3.7.2 python-Levenshtein==0.25.0 fuzzywuzzy==0.18.0
docker-compose exec backend python -m spacy download fr_core_news_md
```

**⏱️ Temps**: ~3 minutes

---

## ✅ CHECKLIST D'IMPLÉMENTATION

- [ ] Installer les dépendances (spaCy, Levenshtein)
- [ ] Créer le modèle ParsedCV
- [ ] Créer les services cv_parser.py et cv_scorer.py  
- [ ] Modifier le worker Celery pour ajouter le scoring
- [ ] Créer la migration Alembic
- [ ] Appliquer la migration
- [ ] Tester avec un CV réel
- [ ] Vérifier les scores dans la base de données

---

## 📝 FICHIERS À CRÉER

1. `backend/app/models/parsed_cv.py` - Modèle de données
2. `backend/app/services/cv_parser.py` - Service de parsing
3. `backend/app/services/cv_scorer.py` - Algorithme de scoring
4. `backend/app/schemas/parsed_cv.py` - Schémas Pydantic
5. `backend/alembic/versions/xxxxx_add_parsed_cv.py` - Migration DB

---

## 🧪 TESTS DE VALIDATION

### Test 1: Vérifier que spaCy est installé

```bash
docker-compose exec backend python -c "import spacy; nlp = spacy.load('fr_core_news_md'); print('✅ spaCy OK')"
```

### Test 2: Vérifier la table parsed_cvs

```bash
docker-compose exec db psql -U ats_user -d ats -c "\d parsed_cvs"
```

### Test 3: Uploader un CV et vérifier le score

1. Créez une offre avec des critères
2. Uploadez un CV
3. Vérifiez dans la DB:

```sql
SELECT full_name, matching_score, skills, experience_years 
FROM parsed_cvs 
ORDER BY matching_score DESC;
```

---

## 🎓 PROCHAINES ÉTAPES

Après Sprint 5, vous pourrez:
- **Sprint 6**: Augmenter la couverture de tests à 80%
- **Sprint 7**: Créer le dashboard recruteur avec visualisations
- **Sprint 8**: Ajouter ElasticSearch pour recherche avancée

---

## 📚 RESSOURCES

- [spaCy Documentation](https://spacy.io/usage)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)

---

**Auteur**: Sprint 5 - IA Scoring & Matching
**Date**: 2026-01-03
**Priorité**: 🔥 CRITIQUE (différenciateur principal)
