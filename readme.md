# ATS-IA – Plateforme d'analyse et de scoring de CV

Plateforme web d'ATS (Applicant Tracking System) intégrant un module d'Intelligence Artificielle pour l'extraction, l'analyse et le scoring de CV par rapport à des offres d'emploi.

## 📋 Table des matières

- [Architecture](#architecture)
- [Installation rapide](#installation-rapide)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [API Documentation](#api-documentation)
- [Tests](#tests)
- [Roadmap](#roadmap)
- [Contribution](#contribution)

---

## 🏗️ Architecture

### Stack Technique

- **Backend**: FastAPI 0.104+ (Python 3.11)
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Worker**: Celery 5.3
- **Frontend**: React 18 + TypeScript + Vite
- **UI**: Shadcn UI + TailwindCSS
- **Monitoring**: Celery Flower, Prometheus

### Composants Principaux

```
┌─────────────────┐      ┌──────────────────┐      ┌───────────────┐
│   React UI      │─────▶│  FastAPI API     │─────▶│  PostgreSQL   │
│  (Port 5173)    │      │  (Port 8000)     │      │  (Port 5432)  │
└─────────────────┘      └──────────────────┘      └───────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  Celery Worker         │
                    │  Redis Broker          │
                    │  (Port 6379)           │
                    └────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            ┌───────────────┐        ┌───────────────┐
            │ PDF Extractor │        │ Flower Monit. │
            │ OCR Processing│        │ (Port 5555)   │
            └───────────────┘        └───────────────┘
```

### Flux de Traitement CV

1. **Authentification** → Recruteur login via JWT (access + refresh token)
2. **Création offre** → Recruteur crée une offre d'emploi
3. **Upload CV** → Candidat upload CV → API enregistre et déclenche task Celery
4. **Extraction** → Worker extrait texte (PDF/DOCX/OCR/Images)
5. **Scoring IA** → Calcul score de correspondance (TF-IDF + SBERT + quality_score)
6. **Résultats** → Recruteur consulte candidatures avec scores rangés

---

## 🚀 Installation rapide

### Prérequis

- Docker & Docker Compose (version 20.10+)
- Ports libres: 8000, 5432, 6379, 5555, 5173

### Setup en 5 étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/NomenjanaharyRK/ats-ia.git
cd ats-ia

# 2. Créer .env depuis le template
cp .env.example .env

# 3. Générer un JWT_SECRET sécurisé
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copier le résultat dans .env sous JWT_SECRET=...

# 4. Démarrer l'environnement complet
docker compose up -d --build

# 5. Appliquer les migrations de base de données
docker exec -it ats-ia-backend-1 alembic upgrade head
```

### Vérification de l'installation

```bash
# Health check API
curl http://localhost:8000/health

# Ping
curl http://localhost:8000/ping

# Swagger UI (Documentation API interactive)
open http://localhost:8000/docs

# Celery Flower (Monitoring des workers)
open http://localhost:5555

# Frontend React
open http://localhost:5173
```

---

## ⚙️ Configuration

### Variables d'environnement (.env)

```bash
# Environment
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://ats_user:ats_password@db:5432/ats_ia

# Security
JWT_SECRET=your_generated_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=30

# Cors
CORS_ORIGINS=["http://localhost:5173", "http://localhost:8000"]

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Redis
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO
STRUCTLOG_ENABLED=true

# AI Models
SBERT_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
SBERT_DEVICE=cpu  # ou 'cuda' si GPU disponible
```

---

## 📖 Utilisation

### Commandes Docker

```bash
# Afficher les logs en temps réel
docker compose logs -f backend worker

# Logs spécifiques
docker compose logs -f backend  # Backend uniquement
docker compose logs -f worker   # Worker uniquement

# Rebuild après modifications des dépendances
docker compose up -d --build

# Redémarrer un service
docker compose restart worker
docker compose restart backend

# Arrêter tous les services
docker compose down

# Arrêter et supprimer les volumes (WARNING: perte de données)
docker compose down -v

# Seed la base de données avec des données de test
docker exec -it ats-ia-backend-1 python seed_database.py
```

### Démarrer l'application complète

```bash
# 1. Démarrer tous les services avec docker-compose
docker compose up -d

# 2. Vérifier que tous les services sont en cours d'exécution
docker compose ps

# 3. Appliquer les migrations de base de données
docker compose exec -it ats-ia-backend-1 alembic upgrade head

# 4. Seeder la base de données (données de test)
docker compose exec -it ats-ia-backend-1 python seed_database.py

# 5. Accéder à l'application
# Frontend:    http://localhost:5173
# Backend API: http://localhost:8000
# Swagger UI:  http://localhost:8000/docs
# Base de données: localhost:5432 (PostgreSQL)

# 6. Arrêter l'application
docker compose down

# 7. Arrêter et supprimer les volumes (ATTENTION: supprime les données)
docker compose down -v
```

### Commandes Utiles

```bash
# Executer les migrations
docker exec -it ats-ia-backend-1 alembic upgrade head

# Créer une nouvelle migration
docker exec -it ats-ia-backend-1 alembic revision --autogenerate -m "Description"

# Rollback d'une migration
docker exec -it ats-ia-backend-1 alembic downgrade -1

# Accéder au shell Python du backend
docker exec -it ats-ia-backend-1 python

# Accéder au shell PostgreSQL
docker exec -it ats-ia-db-1 psql -U ats_user -d ats_ia
```

---

## 📚 API Documentation

L'API est documentée avec Swagger/OpenAPI. Consultez la documentation interactive à: **http://localhost:8000/docs**

### Endpoints Principaux

#### Authentication
- `POST /api/v1/auth/register` - Créer un compte
- `POST /api/v1/auth/login` - Se connecter
- `POST /api/v1/auth/refresh` - Rafraîchir le token
- `POST /api/v1/auth/logout` - Se déconnecter

#### Job Offers (Offres d'emploi)
- `GET /api/v1/offers` - Lister les offres
- `POST /api/v1/offers` - Créer une offre
- `GET /api/v1/offers/{id}` - Détails d'une offre
- `PUT /api/v1/offers/{id}` - Modifier une offre
- `DELETE /api/v1/offers/{id}` - Supprimer une offre

#### Applications (Candidatures)
- `GET /api/v1/offers/{offer_id}/applications` - Lister les candidatures
- `POST /api/v1/offers/{offer_id}/applications` - Soumettre une candidature
- `GET /api/v1/applications/{id}` - Détails d'une candidature
- `GET /api/v1/applications/{id}/score` - Score détaillé

#### CV Files (Fichiers CV)
- `POST /api/v1/cv/upload` - Upload un CV
- `GET /api/v1/cv/{id}` - Récupérer les infos d'un CV
- `GET /api/v1/cv/{id}/text` - Texte extrait du CV
- `DELETE /api/v1/cv/{id}` - Supprimer un CV

---

## 🧪 Tests

### Exécuter les tests

```bash
# Tous les tests
docker exec -it ats-ia-backend-1 pytest tests/ -v

# Avec coverage
docker exec -it ats-ia-backend-1 pytest tests/ --cov=app --cov-report=html

# Tests spécifiques
docker exec -it ats-ia-backend-1 pytest tests/test_auth.py -v
docker exec -it ats-ia-backend-1 pytest tests/test_scoring.py -v

# Tests avec markers
docker exec -it ats-ia-backend-1 pytest -m integration
docker exec -it ats-ia-backend-1 pytest -m unit
```

### Structure des tests

```
backend/tests/
├── conftest.py           # Fixtures pytest
├── test_auth.py          # Tests authentification
├── test_applications.py  # Tests candidatures
├── test_scoring.py       # Tests scoring IA
├── test_extraction.py    # Tests extraction CV
└── test_workers.py       # Tests Celery tasks
```

---

## 🗺️ Roadmap

### Phase 1: MVP (En cours)
- ✅ Backend API (FastAPI + PostgreSQL)
- ✅ Authentification JWT
- ✅ Extraction CV (PDF, DOCX, OCR)
- ✅ Scoring basique (TF-IDF)
- ⏳ Frontend React (En développement)
- ⏳ Tests complets (80% coverage)

### Phase 2: Optimisation & Production
- [ ] Pagination API + caching Redis
- [ ] Indexes PostgreSQL
- [ ] Monitoring Prometheus
- [ ] Logs centralisés (ELK)
- [ ] Rate limiting
- [ ] Healthchecks avancés

### Phase 3: Features Avancées
- [ ] Recherche full-text
- [ ] Export candidatures (PDF/Excel)
- [ ] Notifications email
- [ ] Analytics dashboard
- [ ] Matching en temps réel
- [ ] Machine learning avancé

---

## 🤝 Contribution

Les contributions sont bienvenues! Voici le workflow:

### 1. Créer une branche feature
```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

### 2. Commits conventionnels
```bash
git commit -m "feat: ajouter scoring SBERT"
git commit -m "fix: résoudre bug extraction DOCX"
git commit -m "docs: documenter API"
git commit -m "test: ajouter tests unitaires"
```

### 3. Tests obligatoires
```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing
```

### 4. Pull Request
- Description claire du changement
- Référencer les issues associées
- Screenshot/vidéo si changement UI
- Tests passants (coverage ≥ 80%)

---

## 📞 Support

Pour des questions ou problèmes:
- 📧 Email: support@ats-ia.example.com
- 🐛 Issues: https://github.com/NomenjanaharyRK/ats-ia/issues
- 📖 Wiki: https://github.com/NomenjanaharyRK/ats-ia/wiki

---

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour détails.

---

**Mainteneur**: [@NomenjanaharyRK](https://github.com/NomenjanaharyRK)
