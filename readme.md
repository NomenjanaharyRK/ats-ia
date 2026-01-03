# ATS-IA – Plateforme d'analyse et de scoring de CV

Plateforme web d'ATS (Applicant Tracking System) intégrant un module d'Intelligence Artificielle pour l'extraction, l'analyse et le scoring de CV par rapport à des offres d'emploi.

---

## 🎉 Nouveautés (Sprints 1-2)

### Sprint 1 : Sécurité 🔒
- ✅ Secrets externalisés (JWT_SECRET via .env)
- ✅ JWT avec expiration (1h access, 7j refresh)
- ✅ Refresh token endpoint
- ✅ CORS dynamique
- ✅ Health checks (/health, /ping)
- ✅ Logs version au démarrage

### Sprint 2 : Stabilité Celery 🔧
- ✅ Tâches idémpotentes (safe retry)
- ✅ Auto-retry avec backoff exponentiel
- ✅ Logs structurés (JSON + task_id)
- ✅ Dead Letter Queue pour échecs
- ✅ Celery Flower monitoring (:5555)
- ✅ Machine à états robuste (UPLOADED→EXTRACTING→EXTRACTED)

---

## 1. Installation rapide

### Prérequis
- Docker & Docker Compose
- Port 8000, 5432, 6379, 5555 libres

### Setup

```bash
# 1. Cloner le dépôt
git clone <URL_DU_DEPOT>
cd ats-ia

# 2. Créer .env depuis le template
cp .env.example .env

# 3. Générer un JWT_SECRET sécurisé
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copier le résultat dans .env

# 4. Lancer l'environnement
docker compose up -d --build

# 5. Appliquer les migrations
docker exec -it ats-ia-backend-1 alembic upgrade head
```

### Vérification

```bash
# Health check
curl http://localhost:8000/health

# Ping
curl http://localhost:8000/ping

# Swagger UI
open http://localhost:8000/docs

# Celery Flower (monitoring)
open http://localhost:5555
```

---

## 2. Architecture

### Composants
- **Backend** : FastAPI + SQLAlchemy + JWT auth
- **Worker** : Celery + Redis (extraction CV)
- **DB** : PostgreSQL 15
- **Monitoring** : Celery Flower
- **Frontend** : React/TypeScript (développé séparément)

### Flux
1. Recruteur login → JWT (access + refresh)
2. Création offre → DB
3. Candidat upload CV → API enregistre + déclenche task Celery
4. Worker extrait texte (PDF/DOCX/OCR) + calcule quality_score
5. Recruteur consulte scoring (TF-IDF + SBERT + qualité)

---

## 3. Commandes utiles

### Containers
```bash
# Logs
docker compose logs -f backend worker

# Rebuild après modif dépendances
docker compose up -d --build

# Redémarrer worker
docker compose restart worker

# Arrêter tout
docker compose down
```

### Base de données
```bash
# Shell psql
docker exec -it ats-ia-db-1 psql -U ats_user -d ats

# Nouvelle migration
docker exec -it ats-ia-backend-1 alembic revision --autogenerate -m "description"

# Appliquer migrations
docker exec -it ats-ia-backend-1 alembic upgrade head
```

### Monitoring Celery
```bash
# Flower UI
open http://localhost:5555

# Logs worker
docker compose logs -f worker

# Stats Redis
docker exec -it ats-ia-redis-1 redis-cli INFO
```

---

## 4. API Endpoints

### Auth
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=adminpassword"

# Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<REFRESH_TOKEN>"}'
```

### Offres
```bash
# Créer offre
curl -X POST http://localhost:8000/api/v1/offers \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dev Python",
    "description": "CDI backend FastAPI",
    "status": "OPEN"
  }'

# Lister offres
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/v1/offers
```

### Candidatures
```bash
# Upload CV
curl -X POST http://localhost:8000/api/v1/offers/1/applications \
  -H "Authorization: Bearer <TOKEN>" \
  -F "full_name=Jean Dupont" \
  -F "email=jean@example.com" \
  -F "phone=+261320000000" \
  -F "file=@cv.pdf"

# Scoring
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/v1/offers/1/applications/scoring
```

---

## 5. Développement

### Tests (Sprint 3)
```bash
# Installer dépendances dev
pip install -r backend/requirements-dev.txt

# Lancer tests (disponible Sprint 3)
pytest --cov

# Lint
ruff check backend/

# Format
black backend/
```

---

## 6. Production

### Checklist sécurité
- ☑️ JWT_SECRET unique et aléatoire (32+ chars)
- ☑️ ALLOWED_ORIGINS configuré pour domaine prod
- ☐ HTTPS forcé (reverse proxy nginx/traefik)
- ☐ Rate limiting (via nginx ou middleware)
- ☐ Scan antivirus uploads (optionnel)
- ☑️ Health checks activés

---

## 7. Roadmap

### ✅ Sprint 1 : Sécurité
- Secrets externalisés
- JWT expiration + refresh
- CORS dynamique

### ✅ Sprint 2 : Stabilité Celery
- Idémpotence
- Retries auto
- Logs structurés
- Monitoring Flower

### 🚧 Sprint 3 : Tests + CI/CD
- Tests unitaires (extraction, scoring, API)
- GitHub Actions (lint, test, scan)
- Coverage ≥70%

### 🚧 Sprint 4 : Optimisation DB
- Indexes sur FK
- Pagination
- Tests perf

### 🚧 Sprint 5 : Observabilité
- Logs JSON + request_id
- Métriques Prometheus
- Dashboard Grafana

---

## 8. Support

Pour toute question : [GitHub Issues](https://github.com/NomenjanaharyRK/ats-ia/issues)
