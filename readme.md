# ATS-IA – Plateforme d’analyse et de scoring de CV

Plateforme web d’ATS (Applicant Tracking System) intégrant un module d’Intelligence Artificielle pour l’extraction, l’analyse et le scoring de CV par rapport à des offres d’emploi, dans le cadre du mémoire de Master 2 IA – GID à l’ENI Fianarantsoa.

---

## 1. Contexte et objectifs

#### automatisation par email.

Ce projet s’inscrit dans le canevas de rédaction de mémoire en IA Dev de l’ENI Fianarantsoa, dont une partie clé consiste à intégrer un module IA dans une application complète (frontend, backend, base de données).

Objectifs principaux :

- Automatiser la collecte et la gestion des candidatures pour une offre.
- Extraire automatiquement le texte des CV (PDF, DOCX, images) via OCR.
- Calculer un score de pertinence entre CV et offre (matching sémantique + qualité du CV).
- Fournir aux recruteurs une interface de tri et de comparaison des candidats.

---

## 2. Architecture du projet

L’application suit une architecture **backend FastAPI + frontend React** avec une base de données PostgreSQL et un module IA encapsulé sous forme de service Python.

### Composants principaux

- **Backend** : FastAPI, SQLAlchemy, Alembic, authentification JWT, Celery pour les tâches asynchrones.
- **Base de données** : PostgreSQL (offres, candidats, candidatures, textes de CV, fichiers).
- **Message broker** : Redis (gestion des tâches d’extraction).
- **Worker IA** : Celery + services d’extraction (PDF, DOCX, images) + module de scoring.
- **Frontend** : Application React/TypeScript (interfaces recruteur).

### Flux global

1. Le recruteur crée une offre d’emploi.
2. Le candidat dépose un CV via un formulaire public (upload).
3. Le backend enregistre la candidature et déclenche une tâche Celery.
4. Le worker extrait le texte, calcule un score de qualité, sauvegarde les résultats.
5. Le recruteur consulte la liste des candidatures avec leurs scores.

---

## 3. Fonctionnalités

### Côté recruteur

- Authentification et gestion de session.
- Création, modification, suppression logique d’offres.
- Consultation des candidatures d’une offre.
- Visualisation des scores de matching triés par pertinence.

### Côté candidat

- Formulaire de candidature par offre :
  - Nom complet, email, téléphone.
  - Upload de CV au format PDF, DOCX ou image (PNG/JPG).

### Module IA

- Extraction de texte :
  - PDF textuels.
  - DOCX.
  - Images (OCR).
- Calcul d’un score combiné :
  - Similarité texte offre–CV.
  - Score de qualité du CV (lisibilité, longueur, structure).
- Exposition des résultats via un endpoint `/offers/{id}/applications/scoring`.

---

## 4. Prérequis

- **Docker** et **Docker Compose** installés.
- Environnement compatible WSL2 (pour Windows).
- Port `8000` libre (backend), port `5432` pour PostgreSQL, port `6379` pour Redis.

---

## 5. Installation et lancement

#### Cloner le dépôt :

git clone <URL_DU_DEPOT>
cd ats-ia


#### Lancer l’environnement complet :
docker compose up -d

#### Appliquer les migrations de base de données :
docker exec -it ats-ia-backend-1 alembic upgrade head

#### Vérifier que les services tournent :
docker compose ps


---

## 6. Commandes utiles (cheat sheet)

### Containers
Lancer l’environnement
docker compose up -d

Logs backend + worker
docker compose logs -f backend worker

Rebuild après modification des dépendances
docker compose up -d --build

Arrêter et supprimer les containers
docker compose down

Redémarrer un service spécifique
docker compose restart worker


### Base de données
Shell psql dans le container DB
docker exec -it ats-ia-db-1 psql -U ats_user -d ats

Depuis l’hôte (si psql installé)
psql "host=127.0.0.1 port=5432 dbname=ats user=ats_user password=ats_pass"

Nouvelle migration automatique
docker exec -it ats-ia-backend-1 alembic revision --autogenerate -m "description_changement"

Appliquer les migrations
docker exec -it ats-ia-backend-1 alembic upgrade head


---

## 7. API – Endpoints principaux

### Documentation interactive

- Swagger UI : `http://localhost:8000/docs`

### Authentification

curl -X POST http://localhost:8000/api/v1/auth/login
-H "Content-Type: application/x-www-form-urlencoded"
-d "username=admin@example.com&password=adminpassword"

text

La réponse contient un `access_token` (JWT) à utiliser dans `Authorization: Bearer <TOKEN>`.

### Offres

Créer une offre :

curl -X POST http://localhost:8000/api/v1/offers
-H "Authorization: Bearer <TOKEN>"
-H "Content-Type: application/json"
-d '{
"title": "Dev Python",
"description": "CDI développement backend FastAPI / PostgreSQL",
"status": "OPEN",
"location": "Antananarivo",
"company_name": "LaisseTaTrace"
}'

text

Lister les offres :

curl -H "Authorization: Bearer <TOKEN>"
http://localhost:8000/api/v1/offers

text

### Candidatures & CV

Créer une candidature avec CV :

curl -X POST http://localhost:8000/api/v1/offers/1/applications
-H "Authorization: Bearer <TOKEN>"
-F "full_name=Jean Dupont"
-F "email=jean.dupont@example.com"
-F "phone=+261320000000"
-F "file=@cv_jean_dupont.pdf"

#### Lister les candidatures d’une offre :

curl -H "Authorization: Bearer <TOKEN>"
http://localhost:8000/api/v1/offers/1/applications

#### Récupérer le scoring des candidatures :

curl -H "Authorization: Bearer <TOKEN>"
http://localhost:8000/api/v1/offers/1/applications/scoring

#### Réponse attendue :

[
{
"application_id": 1,
"candidate_full_name": "Jean Dupont",
"score": 86.7
}
]

#### ---

## 8. Structure du projet

ats-ia/
├── backend/
│ ├── app/
│ │ ├── api/
│ │ │ └── v1/
│ │ ├── core/ # Config, sécurité, auth
│ │ ├── db/ # Session, base, migrations
│ │ ├── models/ # ORM SQLAlchemy (User, Offer, Candidate, Application, CVText, CVFile)
│ │ ├── schemas/ # Pydantic
│ │ ├── services/ # cv_extraction, scoring, storage
│ │ └── workers/ # Celery tasks
│ └── Dockerfile
├── frontend/
│ └── ... # App React/TypeScript
├── docker-compose.yml
└── README.md

#### ---

## 9. Intégration IA et mémoire ENI

Conformément au canevas ENI, ce projet illustre 

- La **mise en place de l’environnement** (Docker, FastAPI, PostgreSQL, React).
- L’**analyse et conception** (modèle de données, cas d’utilisation, architecture).
- Le **développement du module IA** :
  - Extraction et préparation des données de CV.
  - Calcul de scores de pertinence.
  - Intégration via services backend et worker asynchrone.
- La **validation** :
  - Tests fonctionnels via Swagger et curl.
  - Jeux de CV de formats variés (PDF, DOCX, images).
  - Analyse des résultats de scoring.
