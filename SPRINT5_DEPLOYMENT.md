# Sprint 5: Déploiement et Tests - Guide Complet

## ✅ État d'Implémentation

### Commits Effectués
1. **5f93c01** - Sprint 5: Complete Celery worker integration (il y a 13 heures)
2. **eb2f33c** - Fix: bcrypt version compatibility with passlib (il y a 1 minute)

### Fichiers Implémentés
- ✅ `backend/app/models/application.py` - Modèle ParsedCV ajouté
- ✅ `backend/app/services/cv_parser.py` - Service de parsing CV
- ✅ `backend/app/services/cv_scorer.py` - Service de scoring IA
- ✅ `backend/app/workers/tasks.py` - Intégration Celery complète
- ✅ `backend/alembic/versions/xxx_add_parsed_cv.py` - Migration base de données
- ✅ `backend/requirements.txt` - Dépendances (bcrypt==3.2.2, spaCy, Levenshtein, fuzzywuzzy)

## 🚀 Déploiement Local

### Étape 1: Récupérer les Derniers Changements

```bash
# Arrêter les conteneurs actuels
docker-compose down

# Récupérer les derniers commits depuis GitHub
git pull origin main
```

### Étape 2: Reconstruire Sans Cache

Le fichier `requirements.txt` a été modifié (bcrypt==3.2.2), il faut rebuild complètement :

```bash
# Rebuild complet sans utiliser le cache Docker
docker-compose build --no-cache

# Alternative: rebuild seulement le backend si nécessaire
docker-compose build --no-cache backend
docker-compose build --no-cache celery_worker
```

### Étape 3: Redémarrer les Services

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### Étape 4: Vérifier le Health Check

```bash
# Le backend doit répondre sans erreur bcrypt
curl http://localhost:8000/health

# Réponse attendue:
# {"status":"healthy","database":"connected","redis":"connected"}
```

### Étape 5: Appliquer la Migration

```bash
# Entrer dans le conteneur backend
docker-compose exec backend bash

# Appliquer la migration ParsedCV
alembic upgrade head

# Vérifier que la table parsed_cv existe
psql $DATABASE_URL -c "\dt"

# Sortir du conteneur
exit
```

## 🧪 Tests Sprint 5

### Test 1: Upload d'un CV

1. Se connecter à l'application: http://localhost:3000
2. Créer ou sélectionner une offre d'emploi
3. Uploader un CV (PDF ou DOCX)
4. Vérifier dans les logs Celery:

```bash
docker-compose logs -f celery_worker
```

Logs attendus:
```
[INFO] Parsing CV: cv_filename.pdf
[INFO] Text extracted: 1234 characters
[INFO] CVParser: Found 3 skills: ['Python', 'React', 'PostgreSQL']
[INFO] CVParser: Experience: 5 years
[INFO] CVScorer: Similarity score: 0.85
[INFO] CVScorer: Skills match: 0.78
[INFO] ParsedCV created with ID: 123
```

### Test 2: Vérifier les Données Parsées

```bash
# Se connecter à PostgreSQL
docker-compose exec db psql -U ats_user -d ats_db

# Vérifier les CVs parsés
SELECT id, application_id, skills_detected, experience_years, similarity_score 
FROM parsed_cv 
ORDER BY created_at DESC 
LIMIT 5;

# Sortir
\q
```

### Test 3: API Endpoints

```bash
# Récupérer les candidatures avec scores
curl http://localhost:8000/api/v1/applications?offer_id=1

# Vérifier que chaque application contient:
# - parsed_cv (objet)
# - similarity_score
# - skills_match_score
```

## 🔍 Résolution des Problèmes

### Problème 1: Erreur bcrypt (RÉSOLU)
**Symptôme:** `AttributeError: module 'bcrypt' has no attribute '__about__'`  
**Solution:** Appliqué dans commit eb2f33c - bcrypt==3.2.2

### Problème 2: structlog manquant
**Symptôme:** `ModuleNotFoundError: No module named 'structlog'`  
**Solution:** 
```bash
docker-compose build --no-cache backend celery_worker
```

### Problème 3: Modèle spaCy non téléchargé
**Symptôme:** `OSError: Can't find model 'fr_core_news_md'`  
**Solution:** Le modèle est dans requirements.txt, rebuild résout le problème

### Problème 4: ParsedCV table n'existe pas
**Symptôme:** `relation "parsed_cv" does not exist`  
**Solution:**
```bash
docker-compose exec backend alembic upgrade head
```

## 📊 Vérifications Finales

### Checklist de Validation

- [ ] Backend démarre sans erreur
- [ ] Celery worker démarre sans erreur
- [ ] Migration appliquée (table parsed_cv existe)
- [ ] Upload de CV fonctionne
- [ ] Parsing extrait le texte
- [ ] Scoring IA calcule la similarité
- [ ] Les données sont sauvegardées dans parsed_cv
- [ ] L'API retourne les scores

### Commandes de Diagnostic

```bash
# Vérifier l'état des conteneurs
docker-compose ps

# Vérifier les logs en temps réel
docker-compose logs -f

# Vérifier l'utilisation des ressources
docker stats

# Tester la connexion Redis
docker-compose exec backend python -c "import redis; r=redis.Redis(host='redis'); print(r.ping())"

# Tester la connexion PostgreSQL
docker-compose exec backend python -c "from sqlalchemy import create_engine; engine=create_engine('postgresql://ats_user:ats_password@db/ats_db'); print(engine.connect())"
```

## 🎯 Fonctionnalités Sprint 5 Complètes

1. ✅ **Parsing CV avec spaCy**
   - Extraction des compétences
   - Détection de l'expérience
   - Support PDF et DOCX

2. ✅ **Scoring IA**
   - Similarité sémantique (sentence-transformers)
   - Matching des compétences (fuzzywuzzy)
   - Calcul du score combiné

3. ✅ **Intégration Celery**
   - Task asynchrone `process_cv_file`
   - Parsing et scoring automatiques
   - Sauvegarde dans ParsedCV

4. ✅ **Migration Database**
   - Table `parsed_cv` créée
   - Relation avec `application`

5. ✅ **Dépendances**
   - spaCy 3.7.2 + modèle français
   - sentence-transformers
   - python-Levenshtein
   - fuzzywuzzy
   - bcrypt 3.2.2 (compatible passlib)

## 📝 Prochaines Étapes (Sprint 6)

- [ ] Interface utilisateur pour visualiser les scores
- [ ] Filtrage des candidatures par score
- [ ] Optimisation des algorithmes de matching
- [ ] Tests unitaires et d'intégration
- [ ] Documentation API complète

---

**Auteur:** Comet AI  
**Date:** 04 Janvier 2026  
**Sprint:** 5 - IA Scoring & Matching  
**Statut:** ✅ COMPLET - Prêt pour déploiement
