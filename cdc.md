Plateforme Applicant Tracking System avec IA pour scoring automatique CV/offres

🎯 CONTEXTE & OBJECTIFS
Problématique : Les recruteurs passent 23h/semaine à trier CV manuellement. ATS-IA automatise l'extraction, l'analyse et le scoring IA des CV vs offres d'emploi.

Objectifs :

✅ 80% temps gagné sur le screening CV

✅ Matching sémantique (NLP + embeddings)

✅ Interface moderne recruteur (React + Shadcn)

✅ Scalable (Docker + Celery + PostgreSQL)

✅ Sécurisé (JWT + ClamAV + quarantaine)

MVP : 3 semaines | V1.0 : 8 semaines

👥 UTILISATEURS & RÔLES
text
ADMIN (super admin)
├── Gestion utilisateurs (CRUD recruteurs)
├── Audit logs
├── Config système (quotas, rétention)
└── Dashboard global

RECRUTEUR (user principal)
├── Créer/éditer/supprimer offres
├── Upload CV candidats (drag&drop)
├── Dashboard scoring temps réel
├── Tableau candidatures filtrable
├── Export Excel/PDF
└── Stats personnelles
📊 FONCTIONNALITÉS DÉTAILLÉES
1. AUTHENTIFICATION & SÉCURITÉ
text
✅ JWT Access (1h) + Refresh (7j)
✅ Login form-urlencoded (username=email)
✅ Refresh token automatique
✅ Protected routes (RBAC)
✅ Rate limiting (5 req/min IP)
✅ CORS dynamique (.env)
✅ HTTPS forcé (prod)
✅ Audit logs (toutes actions)
2. GESTION OFFRES D'EMPLOI
text
Statuts : DRAFT | PUBLISHED | ARCHIVED
Champs :
├── title (string, 100c max)
├── description (text, 5000c)
├── requirements (array string)
├── nice_to_have (array string)
├── status (enum)
├── owner_id (FK User)
└── deleted (soft delete)

API :
├── POST /api/v1/offers           # Créer
├── GET /api/v1/offers            # Lister (paginé)
├── GET /api/v1/offers/{id}       # Détail
├── PATCH /api/v1/offers/{id}     # Update
└── DELETE /api/v1/offers/{id}    # Archive
3. UPLOAD & EXTRACTION CV ⭐ CŒUR IA
text
Formats : PDF, DOCX, TXT (max 10Mo)
Flux :
1. Upload → Quarantaine (S3/local)
2. ClamAV scan → Virus ? → Reject
3. OCR/Textract → Texte brut
4. Chunking → Paragraphes/sentences
5. Stockage → cv_files + cv_texts

États Celery :
UPLOADED → SCANNING → CLEAN → EXTRACTING → EXTRACTED → SCORING → SCORED

API :
├── POST /api/v1/offers/{offer_id}/applications
│   ├── multipart: fullname, email, phone, file
│   └── → 202 Accepted + task_id
├── GET /api/v1/applications/{id}/status  # Polling
└── GET /api/v1/offers/{id}/scoring      # Tableau scores
4. SCORING IA ⭐ DIFFÉRENCIATEUR
text
Algorithmes hybrides :
1. **TF-IDF** (keywords exacts) → 40%
2. **SBERT embeddings** (sémantique) → 40%
3. **Qualité CV** (structure, complétude) → 20%

Score final : 0-100% (vert 80+, orange 60-79, rouge <60)

Highlights :
├── Mots-clés matchés (surbrillance)
├── Sections détectées (exp, skills...)
└── Recommandations (manque X skill)
5. DASHBOARD RECRUTEUR
text
KPI Cards :
├── Offres actives/publiées
├── CV en attente/analysés
├── Score moyen / Top score
└── Conversion rate

Quick Actions :
├── Drag&drop CV (multi 10 max)
├── Nouvelle offre (modal)
└── Export sélection (Excel)

Tableau candidatures :
| Nom | Email | Score | Status | Upload | Actions ↓
├── Tri toutes colonnes
├── Filtres (score >80, status NEW...)
├── Pagination (25/50/100)
└── Bulk actions (export/archiver)
6. ADMIN PANEL
text
✅ Users CRUD (rôles, active/inactif)
✅ Audit logs (qui/fait quoi/quand)
✅ Config quotas (upload/jour/user)
✅ Rétention CV (30j auto-delete)
✅ Stats globales (export CSV)
🛠️ TECHNOLOGIES
text
BACKEND :
├── FastAPI 0.115+ (Python 3.12)
├── SQLAlchemy 2.0 + Alembic
├── PostgreSQL 16 (indexes GIN fulltext)
├── Redis 7 (Celery broker + cache)
├── Celery 5.4 (workers async)
├── Pydantic v2 (validation stricte)

IA/ML :
├── sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
├── PyMuPDF/pypdf (PDF)
├── python-docx (DOCX)
├── Tesseract OCR (images)

FRONTEND :
├── React 18.3 + Vite 5.4
├── TypeScript 5.8
├── TailwindCSS 3.4 + Shadcn UI
├── TanStack Query 5 + Zustand
├── React Hook Form + Zod
├── Sonner (toasts) + Lucide icons
├── react-dropzone + react-pdf

INFRA :
├── Docker Compose (dev/prod)
├── nginx (reverse proxy HTTPS)
├── ClamAV (antivirus)
├── Flower (Celery monitoring)
└── MinIO/S3 (quarantaine CV)
🔧 CONTRAINTES TECHNIQUES
text
Sécurité :
├── Upload max 10Mo, 5 formats
├── Quarantaine 24h (scan auto)
├── JWT HS256 (secret 32+ chars)
├── Rate limit 100req/h/user
├── CORS http://localhost:5173,prod.com

Performance :
├── Indexing PostgreSQL (fulltext + GIN)
├── Cache Redis (scores 1h)
├── Celery concurrency 4 (CPU-bound)
├── Pagination 25 défaut

UX :
├── Temps réponse API <500ms
├── Upload progressif (WebSocket?)
├── Skeleton loading
├── Mobile-first responsive
├── Dark/Light theme
├── PWA ready
📈 INDICATEURS DE SUCCÈS (KPI)
text
Technique :
├── 95% uptime (health checks)
├── <2s temps scoring CV
├── 99% CV extractés sans erreur
├── Bundle frontend <1MB gzip

Business :
├── 80% CV score >60% (qualité)
├── <2min screening/offre
├── 90% satisfaction recruteurs
🗓️ ROADMAP SPRINTS (8 SEMAINES)
text
Sprint 1 (1s) : 🔐 Auth + Users + Offres CRUD
Sprint 2 (1s) : 📤 Upload CV + Extraction basique
Sprint 3 (1s) : 🤖 Scoring IA TF-IDF + SBERT
Sprint 4 (1s) : 📊 Dashboard + Tableau candidatures
Sprint 5 (1s) : 🛡️ Sécurité (ClamAV + quotas)
Sprint 6 (1s) : 🎨 Frontend polish + mobile
Sprint 7 (1s) : 👨‍💼 Admin panel + exports
Sprint 8 (1s) : 🚀 Prod (Docker + monitoring)
💰 COÛTS ESTIMÉS
text
Dev Fullstack : 8 sem @ 50h/sem = 400h
Dev Frontend : 80h (UI/UX pro)
Infra cloud : 50€/mois (Hetzner 4vCPU 8Go)

Total : ~12k€ (dev) + 600€/an (infra)
ROI : 1 recruteur = 23h/sem * 50€/h = 5k€/mois économisé
Ce cahier des charges est :

✅ Complet (fonctionnalités + tech + UX)

✅ Réaliste (MVP 3 sem, V1 8 sem)

✅ Mesurable (KPI + roadmap)

✅ Scalable (Docker + Celery)

Prochaine étape : Valider les priorités Sprint 1 → Implémentation immédiate ! 🚀