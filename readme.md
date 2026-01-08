# ATS-IA – Plateforme d'analyse et de scoring de CV

Plateforme web d'ATS (Applicant Tracking System) intégrant un module d'Intelligence Artificielle pour l'extraction, l'analyse et le scoring de CV par rapport à des offres d'emploi.

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

#Seed database
docker exec -it ats-ia-backend-1 python seed_database.py
```
