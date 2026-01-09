#!/usr/bin/env python3
"""
Script de seed pour initialiser la base de données avec des données de test.

Features:
- Crée automatiquement les tables si elles n'existent pas
- Nettoie la base avec TRUNCATE CASCADE (safe pour FK)
- Crée 5 utilisateurs (1 admin + 4 recruteurs)
- Crée 100 offres d'emploi réalistes et détaillées
- Retry automatique si PostgreSQL est en recovery mode
"""

import sys
from pathlib import Path
import logging
import time
from typing import List

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from passlib.context import CryptContext

# -------------------------------------------------------------------
# PYTHON PATH
# -------------------------------------------------------------------
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# -------------------------------------------------------------------
# LOGGING
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# IMPORTS APP - ORDRE IMPORTANT !
# -------------------------------------------------------------------
from app.db.base import Base
from app.core.config import settings

# Importer TOUS les modèles dans le bon ordre pour éviter les erreurs de relation
from app.models.user import User, UserRole
from app.models.offer import Offer
from app.models.candidate import Candidate
from app.models.cv_file import CVFile
from app.models.cv_text import CVText
from app.models.parsed_cv import ParsedCV
from app.models.application import Application

# -------------------------------------------------------------------
# PASSWORD HASH
# -------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# -------------------------------------------------------------------
# DATABASE CONNECTION HELPER
# -------------------------------------------------------------------
def wait_for_db(engine, max_retries=30, delay=2):
    """Attend que PostgreSQL soit prêt (gère le recovery mode)"""
    logger.info("⏳ Attente de la connexion PostgreSQL...")
    
    for attempt in range(max_retries):
        try:
            conn = engine.connect()
            conn.close()
            logger.info("✅ PostgreSQL est prêt!")
            return True
        except OperationalError as e:
            error_msg = str(e)
            if "recovery mode" in error_msg or "starting up" in error_msg:
                logger.info(f"  Tentative {attempt + 1}/{max_retries} - PostgreSQL en recovery mode, attente...")
                time.sleep(delay)
            else:
                logger.error(f"❌ Erreur de connexion: {error_msg}")
                raise
    
    raise Exception("❌ Impossible de se connecter à PostgreSQL après plusieurs tentatives")

# -------------------------------------------------------------------
# DATA GENERATORS
# -------------------------------------------------------------------

USERS_DATA = [
    {
        "email": "admin@ats-ia.com",
        "password": "Admin@123",
        "role": UserRole.ADMIN,
        "name": "Administrateur Principal"
    },
    {
        "email": "sophie.martin@ats-ia.com",
        "password": "Sophie@123",
        "role": UserRole.RECRUITER,
        "name": "Sophie Martin"
    },
    {
        "email": "thomas.dubois@ats-ia.com",
        "password": "Thomas@123",
        "role": UserRole.RECRUITER,
        "name": "Thomas Dubois"
    },
    {
        "email": "marie.laurent@ats-ia.com",
        "password": "Marie@123",
        "role": UserRole.RECRUITER,
        "name": "Marie Laurent"
    },
    {
        "email": "pierre.bernard@ats-ia.com",
        "password": "Pierre@123",
        "role": UserRole.RECRUITER,
        "name": "Pierre Bernard"
    },
]

# 100 offres d'emploi réalistes
OFFERS_DATA = [
    # Tech - Développement (25 offres)
    {
        "title": "Développeur Python Senior - FinTech",
        "description": """Rejoignez notre équipe FinTech innovante en tant que Développeur Python Senior.

**Responsabilités:**
- Développer des APIs REST avec FastAPI et Django
- Optimiser les performances des systèmes de trading
- Implémenter des solutions de microservices
- Mentorer les développeurs juniors

**Stack Technique:**
- Python 3.11+, FastAPI, Django, Celery
- PostgreSQL, Redis, RabbitMQ
- Docker, Kubernetes, AWS
- Git, CI/CD (GitLab CI)

**Profil:**
- 5+ ans d'expérience en Python
- Expertise en architecture microservices
- Connaissance des systèmes financiers
- Anglais professionnel

**Ce que nous offrons:**
- Salaire: 55-75k€
- Remote flexible (2j/semaine bureau)
- Stock-options
- Budget formation 3k€/an""",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        "nice_to_have_skills": ["Kubernetes", "Redis", "RabbitMQ"],
        "min_experience_years": 5,
        "required_education": ["Master Informatique", "École d'Ingénieur"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Développeur Full Stack React/Node.js",
        "description": """Startup en hypercroissance cherche un Développeur Full Stack passionné.

**Mission:**
- Développer de nouvelles features produit
- Créer des interfaces utilisateur modernes
- Maintenir l'API Node.js/Express
- Participer aux décisions d'architecture

**Technologies:**
- Frontend: React 18, TypeScript, TailwindCSS, Next.js
- Backend: Node.js, Express, TypeScript
- Database: MongoDB, Redis
- Tools: Git, Docker, Jest, Cypress

**Vous êtes:**
- Passionné par le JavaScript/TypeScript
- Autonome et proactif
- Soucieux de la qualité du code
- 3+ ans d'expérience

**Package:**
- 45-60k€ selon expérience
- BSPCE (early employee)
- Remote 100% possible
- Matériel au choix""",
        "required_skills": ["React", "Node.js", "TypeScript", "MongoDB"],
        "nice_to_have_skills": ["Next.js", "Docker", "AWS"],
        "min_experience_years": 3,
        "required_education": ["Licence Informatique"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Développeur Mobile Flutter - E-commerce",
        "description": """Leader du e-commerce recherche un Développeur Mobile Flutter.

**Votre rôle:**
- Développer l'app mobile iOS/Android
- Implémenter les nouvelles features
- Optimiser les performances
- Travailler avec les designers UX

**Stack:**
- Flutter, Dart
- Firebase, REST APIs
- State management (Bloc/Riverpod)
- Git, CI/CD

**Profil recherché:**
- 2+ ans Flutter en production
- Apps publiées sur stores
- Sens du détail UI/UX
- Esprit d'équipe

**Avantages:**
- 42-55k€
- RTT + congés illimités
- Budget hardware
- Formation continue""",
        "required_skills": ["Flutter", "Dart", "Firebase", "REST API"],
        "nice_to_have_skills": ["Bloc", "Riverpod", "GraphQL"],
        "min_experience_years": 2,
        "required_education": ["Bac+3 Informatique"],
        "required_languages": ["Français"],
        "status": "PUBLISHED"
    },
    {
        "title": "Ingénieur DevOps - Cloud Native",
        "description": """Scale-up tech cherche un Ingénieur DevOps pour sa plateforme cloud.

**Missions:**
- Gérer l'infrastructure Kubernetes
- Automatiser les déploiements
- Monitorer et optimiser les performances
- Assurer la sécurité et compliance

**Technologies:**
- Kubernetes, Docker, Helm
- Terraform, Ansible
- AWS (EKS, RDS, S3, CloudWatch)
- GitLab CI/CD, ArgoCD
- Prometheus, Grafana, ELK

**Profil:**
- 4+ ans en DevOps/SRE
- Expertise Kubernetes en production
- Culture Infrastructure as Code
- Certifications AWS appréciées

**Package:**
- 50-70k€
- Astreintes rémunérées
- Remote jusqu'à 3j/semaine
- Conférences payées""",
        "required_skills": ["Kubernetes", "Docker", "Terraform", "AWS", "CI/CD"],
        "nice_to_have_skills": ["Ansible", "Prometheus", "Grafana"],
        "min_experience_years": 4,
        "required_education": ["Ingénieur", "Master"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Data Engineer - Big Data & ML",
        "description": """Nous recherchons un Data Engineer pour construire notre data platform.

**Responsabilités:**
- Concevoir et maintenir les pipelines data
- Optimiser le stockage et traitement des données
- Collaborer avec les Data Scientists
- Implémenter des solutions de ML en production

**Stack Technique:**
- Python, Spark, Airflow
- AWS (S3, EMR, Glue, Redshift)
- SQL, PostgreSQL, Snowflake
- Docker, Kubernetes
- dbt, Kafka

**Vous avez:**
- 3+ ans en Data Engineering
- Maîtrise de SQL et Python
- Expérience avec des volumes importants
- Connaissances en ML ops

**Rémunération:**
- 48-65k€
- Bonus annuel 10-15%
- Remote 2-3j/semaine
- Environnement data-driven""",
        "required_skills": ["Python", "Spark", "SQL", "AWS", "Airflow"],
        "nice_to_have_skills": ["Kafka", "dbt", "Snowflake"],
        "min_experience_years": 3,
        "required_education": ["Master", "École d'Ingénieur"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Architecte Solutions Cloud - AWS",
        "description": """Cabinet de conseil recherche un Architecte Solutions Cloud.

**Mission:**
- Concevoir des architectures cloud scalables
- Accompagner les clients dans leur migration
- Préconiser les best practices AWS
- Former les équipes techniques

**Expertises:**
- AWS (Certified Solutions Architect)
- Microservices, Serverless, Containers
- Infrastructure as Code
- Sécurité et compliance cloud

**Profil:**
- 6+ ans d'expérience IT dont 3+ en cloud
- Certification AWS Solution Architect Pro
- Excellentes capacités de communication
- Expérience en conseil appréciée

**Offre:**
- 60-85k€
- Voiture de fonction
- Mobilité nationale
- Formation continue""",
        "required_skills": ["AWS", "Architecture", "Terraform", "Microservices"],
        "nice_to_have_skills": ["Kubernetes", "Serverless", "Azure"],
        "min_experience_years": 6,
        "required_education": ["Ingénieur", "Master"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Développeur Backend Java/Spring",
        "description": """Éditeur logiciel cherche Développeur Backend Java expérimenté.

**Vos missions:**
- Développer des APIs REST robustes
- Optimiser les performances applicatives
- Maintenir le code legacy
- Participer aux code reviews

**Stack:**
- Java 17, Spring Boot, Spring Security
- PostgreSQL, MongoDB
- Maven, Git
- JUnit, Mockito
- Docker, Jenkins

**Profil:**
- 4+ ans en Java/Spring
- Maîtrise des design patterns
- Expérience en architecture hexagonale
- Clean Code advocate

**Package:**
- 45-60k€
- Télétravail 3j/semaine
- Tickets restaurant
- Mutuelle premium""",
        "required_skills": ["Java", "Spring Boot", "PostgreSQL", "REST API"],
        "nice_to_have_skills": ["MongoDB", "Docker", "Kubernetes"],
        "min_experience_years": 4,
        "required_education": ["Bac+5 Informatique"],
        "required_languages": ["Français"],
        "status": "PUBLISHED"
    },
    {
        "title": "Tech Lead Frontend - React",
        "description": """Scale-up SaaS recherche son futur Tech Lead Frontend.

**Responsabilités:**
- Leader technique de l'équipe frontend (4 devs)
- Définir l'architecture front
- Code reviews et mentoring
- Choix technologiques stratégiques

**Technologies:**
- React 18, TypeScript, Next.js 14
- TailwindCSS, Radix UI
- React Query, Zustand
- Vite, Vitest, Playwright
- Git, GitHub Actions

**Vous êtes:**
- Expert React avec 5+ ans d'XP
- Leadership technique confirmé
- Pédagogue et collaboratif
- Passionné par la performance web

**Ce qu'on offre:**
- 55-75k€
- Equity package
- Remote first
- Budget confs/formations""",
        "required_skills": ["React", "TypeScript", "Leadership", "Architecture"],
        "nice_to_have_skills": ["Next.js", "Performance", "Testing"],
        "min_experience_years": 5,
        "required_education": ["Bac+5"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Ingénieur Sécurité - DevSecOps",
        "description": """Fintech réglementée cherche Ingénieur Sécurité DevSecOps.

**Missions:**
- Intégrer la sécurité dans le CI/CD
- Auditer le code et l'infrastructure
- Gérer les vulnérabilités
- Former les équipes aux bonnes pratiques

**Compétences:**
- SAST/DAST (SonarQube, Snyk)
- Kubernetes security
- OWASP Top 10
- Pen testing
- AWS security

**Profil:**
- 3+ ans en cybersécurité
- Certifications (OSCP, CEH) appréciées
- Culture DevOps
- Veille technologique active

**Rémunération:**
- 50-68k€
- Prime sécurité
- Certifications financées
- Remote 2j/semaine""",
        "required_skills": ["Sécurité", "DevSecOps", "Kubernetes", "OWASP"],
        "nice_to_have_skills": ["Pen Testing", "AWS", "SAST"],
        "min_experience_years": 3,
        "required_education": ["Master Cybersécurité"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "SRE - Site Reliability Engineer",
        "description": """Plateforme e-commerce recherche un SRE pour garantir la fiabilité.

**Votre rôle:**
- Garantir 99.9% de disponibilité
- Automatiser les opérations
- Gérer les incidents production
- Améliorer l'observabilité

**Stack:**
- Kubernetes, Docker
- Terraform, Ansible
- Prometheus, Grafana, Datadog
- Python, Go
- GCP ou AWS

**Vous maîtrisez:**
- SLI/SLO/SLA
- Incident management
- Chaos engineering
- 4+ ans en ops/SRE

**Package:**
- 52-72k€
- Astreintes bien rémunérées
- Remote flexible
- Budget outils""",
        "required_skills": ["SRE", "Kubernetes", "Monitoring", "Python", "Cloud"],
        "nice_to_have_skills": ["Go", "Chaos Engineering", "Terraform"],
        "min_experience_years": 4,
        "required_education": ["Ingénieur"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    
    # Data Science & IA (15 offres)
    {
        "title": "Data Scientist - NLP & IA Générative",
        "description": """Startup IA recherche Data Scientist spécialisé NLP.

**Projets:**
- Développer des modèles NLP de pointe
- Fine-tuner des LLMs (GPT, LLaMA)
- Créer des pipelines ML robustes
- Publier des articles de recherche

**Stack:**
- Python, PyTorch, Hugging Face
- LangChain, Vector DBs
- MLflow, Weights & Biases
- AWS SageMaker

**Profil:**
- PhD ou 3+ ans en NLP
- Publications appréciées
- Expérience avec les LLMs
- Anglais courant

**Offre:**
- 50-70k€
- Equity significative
- Budget recherche
- Conférences internationales""",
        "required_skills": ["Python", "NLP", "Machine Learning", "PyTorch"],
        "nice_to_have_skills": ["LLM", "Hugging Face", "Research"],
        "min_experience_years": 3,
        "required_education": ["PhD", "Master Data Science"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "ML Engineer - Computer Vision",
        "description": """Développez des solutions de Computer Vision révolutionnaires.

**Missions:**
- Créer des modèles de détection d'objets
- Optimiser les modèles pour le edge
- Déployer sur mobile/embarqué
- Améliorer la précision des algos

**Technologies:**
- PyTorch, TensorFlow, YOLO, SAM
- OpenCV, Albumentations
- TensorRT, ONNX
- Docker, Kubernetes

**Vous avez:**
- 2+ ans en Computer Vision
- Portfolio de projets
- Connaissances en deep learning
- Passion pour l'innovation

**Rémunération:**
- 45-62k€
- Bonus sur objectifs
- Hardware haut de gamme
- Remote 100% possible""",
        "required_skills": ["Computer Vision", "PyTorch", "Deep Learning", "OpenCV"],
        "nice_to_have_skills": ["YOLO", "TensorRT", "Edge AI"],
        "min_experience_years": 2,
        "required_education": ["Master IA"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Lead Data Scientist - Recommandation",
        "description": """Plateforme de streaming cherche Lead Data Scientist.

**Responsabilités:**
- Diriger l'équipe DS (5 personnes)
- Améliorer les algorithmes de recommandation
- A/B testing et expérimentation
- Collaborer avec le produit

**Expertises:**
- ML/DL, Recommender Systems
- Python, Spark, TensorFlow
- A/B testing, causalité
- Data-driven decision making

**Profil:**
- 6+ ans en Data Science
- Expérience en management
- Track record de projets impactants
- Vision produit forte

**Package:**
- 65-90k€
- Equity
- Remote first
- Budget équipe""",
        "required_skills": ["Data Science", "Machine Learning", "Leadership", "Python"],
        "nice_to_have_skills": ["Recommender Systems", "Spark", "A/B Testing"],
        "min_experience_years": 6,
        "required_education": ["PhD", "Master"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "MLOps Engineer - Platform",
        "description": """Construisez la plateforme ML de demain.

**Mission:**
- Développer la plateforme MLOps
- Automatiser le training et déploiement
- Gérer le feature store
- Monitorer les modèles en production

**Stack:**
- Kubernetes, Kubeflow
- MLflow, Feast
- Airflow, Argo Workflows
- AWS/GCP, Terraform

**Vous maîtrisez:**
- ML Ops best practices
- CI/CD pour le ML
- Infrastructure as Code
- 3+ ans en ML/Data Engineering

**Offre:**
- 48-65k€
- Challenges techniques
- Équipe internationale
- Croissance rapide""",
        "required_skills": ["MLOps", "Kubernetes", "Python", "CI/CD"],
        "nice_to_have_skills": ["Kubeflow", "MLflow", "Airflow"],
        "min_experience_years": 3,
        "required_education": ["Master"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Data Analyst - Product Analytics",
        "description": """Product company cherche Data Analyst pour piloter la croissance.

**Vos missions:**
- Analyser le comportement utilisateurs
- Créer des dashboards Tableau/Looker
- Définir les KPIs produit
- Supporter la stratégie business

**Outils:**
- SQL (expert), Python (bases)
- Tableau, Looker, Metabase
- Google Analytics, Amplitude
- Excel, Google Sheets

**Profil:**
- 2+ ans en analyse de données
- SQL avancé impératif
- Mindset product-oriented
- Excellent communicant

**Package:**
- 38-52k€
- Prime variable
- Formation continue
- Remote 2j/semaine""",
        "required_skills": ["SQL", "Tableau", "Analytics", "Excel"],
        "nice_to_have_skills": ["Python", "Looker", "Amplitude"],
        "min_experience_years": 2,
        "required_education": ["Master", "École de Commerce"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },

    # Product & Design (15 offres)
    {
        "title": "Product Manager - B2B SaaS",
        "description": """Scale-up SaaS B2B cherche Product Manager passionné.

**Responsabilités:**
- Définir la roadmap produit
- Gérer le backlog et prioriser
- Travailler avec engineering & design
- Analyser les métriques produit

**Compétences:**
- Product discovery (user research)
- Roadmapping, OKRs
- Agilité (Scrum/Kanban)
- Data-driven decisions

**Vous êtes:**
- 3+ ans en Product Management
- B2B SaaS experience
- Tech-savvy
- Excellent communicant

**Offre:**
- 50-65k€
- Equity
- Impact fort sur le produit
- Remote flexible""",
        "required_skills": ["Product Management", "B2B", "SaaS", "Agile"],
        "nice_to_have_skills": ["User Research", "Data Analysis", "Roadmapping"],
        "min_experience_years": 3,
        "required_education": ["Master", "École"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Designer UX/UI - Product-focused",
        "description": """Nous cherchons un Designer UX/UI talentueux pour façonner l'expérience utilisateur de nos produits innovants.

**Responsabilités:**
- Concevoir des interfaces utilisateur intuitives et belles
- Conduire des user research et tests utilisateurs
- Créer des prototypes interactifs haute-fidélité
- Collaborer avec les product managers et engineers
- Itérer rapidement basé sur les feedbacks

**Vous maîtrisez:**
- Figma (ou Sketch)
- Design system & component libraries
- Prototyping interactif
- User research & usability testing
- Design thinking & problem solving

**Votre profil:**
- Portfolio solide montrant votre processus
- Expérience avec des produits mobiles ET web
- Mindset user-centric
- Communication excellente
- Autonomie & proactivité

**Équipe:**
- Design team de 4 designers
- Product-first culture
- Liberté créative
- Influence directe sur la stratégie produit

**Localisation & Flexible:**
- Paris (1-2 jours/semaine au bureau)
- Ou 100% remote (EU)

**Compensation:**
- Salaire: 42-55k€ (selon expérience)
- Bonus à la performance
- Setup complet (M2 MacBook, monitor, etc.)""",
        "required_skills": ["Figma", "UX Design", "UI Design", "Prototyping"],
        "nice_to_have_skills": ["User Research", "Design System", "Animation"],
        "min_experience_years": 3,
        "required_education": ["École de Design", "Bac+3"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Product Designer - Mobile App",
        "description": """App mobile leader cherche Product Designer senior.

**Mission:**
- Designer l'expérience mobile iOS/Android
- Créer des animations et micro-interactions
- Travailler sur le design system
- Collaborer étroitement avec les devs

**Skills:**
- Figma expert, Protopie
- Motion design (After Effects)
- iOS & Android guidelines
- Accessibilité (WCAG)

**Profil:**
- 4+ ans en Product Design
- Apps publiées dans votre portfolio
- Maîtrise de l'animation
- Détail-oriented

**Package:**
- 45-58k€
- Stock-options
- Derniers devices
- Remote 100%""",
        "required_skills": ["Figma", "Mobile Design", "Prototyping", "Animation"],
        "nice_to_have_skills": ["After Effects", "Accessibility", "Motion Design"],
        "min_experience_years": 4,
        "required_education": ["École de Design"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "UX Researcher - Qualitative",
        "description": """Nous recherchons un UX Researcher pour guider nos décisions produit.

**Responsabilités:**
- Conduire des entretiens utilisateurs
- Organiser des tests d'usabilité
- Analyser le comportement utilisateurs
- Présenter les insights à l'équipe

**Méthodes:**
- User interviews
- Usability testing
- Card sorting, tree testing
- Journey mapping
- Surveys & analytics

**Profil:**
- 2+ ans en UX Research
- Maîtrise des méthodes qualitatives
- Excellent storytelling
- Empathie naturelle

**Offre:**
- 40-54k€
- Impact direct produit
- Équipe bienveillante
- Remote 3j/semaine""",
        "required_skills": ["UX Research", "User Testing", "Interviews", "Analysis"],
        "nice_to_have_skills": ["Analytics", "Surveys", "Figma"],
        "min_experience_years": 2,
        "required_education": ["Master Ergonomie", "Psychologie"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Head of Product - Fintech",
        "description": """Fintech en croissance cherche Head of Product visionnaire.

**Mission:**
- Définir la vision produit long-terme
- Manager l'équipe produit (3 PMs)
- Collaborer avec le C-level
- Piloter la stratégie go-to-market

**Expertises:**
- Product leadership confirmé
- Fintech / Payments
- B2C & B2B
- Growth hacking

**Vous avez:**
- 7+ ans dont 3+ en leadership
- Track record de succès
- Vision stratégique
- Management bienveillant

**Package:**
- 70-95k€
- Equity significative
- Voiture de fonction
- Comité de direction""",
        "required_skills": ["Product Leadership", "Strategy", "Fintech", "Management"],
        "nice_to_have_skills": ["Growth", "B2B", "B2C"],
        "min_experience_years": 7,
        "required_education": ["Grande École"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },

    # Marketing & Growth (10 offres)
    {
        "title": "Growth Hacker - Acquisition",
        "description": """Startup SaaS cherche Growth Hacker pour accélérer la croissance.

**Missions:**
- Optimiser les canaux d'acquisition
- A/B testing et expérimentation
- SEO/SEA, Social Ads
- Analyser les métriques de croissance

**Compétences:**
- Google Ads, Facebook Ads
- SEO technique & content
- Analytics (GA4, Mixpanel)
- SQL bases

**Profil:**
- 2+ ans en growth/digital marketing
- Data-driven mindset
- Créativité & rigueur
- Startup spirit

**Offre:**
- 38-52k€
- Variable sur objectifs
- Budgets marketing conséquents
- Remote 2j/semaine""",
        "required_skills": ["Growth Hacking", "SEO", "Google Ads", "Analytics"],
        "nice_to_have_skills": ["SQL", "A/B Testing", "Facebook Ads"],
        "min_experience_years": 2,
        "required_education": ["École de Commerce", "Master Marketing"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Content Marketing Manager",
        "description": """Scale-up B2B cherche Content Marketing Manager créatif.

**Responsabilités:**
- Définir la stratégie de contenu
- Produire du contenu (blog, ebooks, videos)
- Gérer les réseaux sociaux
- SEO & growth organique

**Skills:**
- Excellent rédacteur
- SEO content
- Social media
- Notion, Figma (bases)

**Vous êtes:**
- 3+ ans en content marketing
- Créatif et analytique
- Autonome
- B2B SaaS experience

**Package:**
- 42-56k€
- Remote first
- Budget créatif
- Formation continue""",
        "required_skills": ["Content Marketing", "SEO", "Copywriting", "Social Media"],
        "nice_to_have_skills": ["Video", "B2B", "Analytics"],
        "min_experience_years": 3,
        "required_education": ["Bac+5 Marketing"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Performance Marketing Manager",
        "description": """E-commerce leader recrute Performance Marketing Manager.

**Mission:**
- Gérer les campagnes paid (Google, Meta, TikTok)
- Optimiser le ROAS
- Tracking & attribution
- Budget 500k€/mois

**Expertises:**
- Google Ads certified
- Meta Ads expert
- GA4, GTM
- Excel/Sheets avancé

**Profil:**
- 4+ ans en performance marketing
- E-commerce experience
- ROI-obsessed
- Analytique

**Rémunération:**
- 45-60k€
- Bonus variable 20%
- Gros budgets
- Équipe dynamique""",
        "required_skills": ["Performance Marketing", "Google Ads", "Meta Ads", "Analytics"],
        "nice_to_have_skills": ["TikTok Ads", "Attribution", "GTM"],
        "min_experience_years": 4,
        "required_education": ["Marketing Digital"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "CMO - Chief Marketing Officer",
        "description": """Startup Serie A recherche son CMO pour structurer le marketing.

**Responsabilités:**
- Définir la stratégie marketing globale
- Construire l'équipe marketing (0→10)
- Gérer le budget marketing
- Collaborer avec Sales & Product

**Expertises:**
- B2B SaaS marketing
- Brand positioning
- Demand generation
- Marketing ops

**Vous avez:**
- 8+ ans en marketing dont 3+ en leadership
- Expérience startup scale-up
- Track record de croissance
- Vision stratégique

**Package:**
- 75-100k€
- Equity importante
- Budget illimité
- Comex""",
        "required_skills": ["Marketing Leadership", "Strategy", "B2B", "Team Building"],
        "nice_to_have_skills": ["SaaS", "Demand Gen", "Brand"],
        "min_experience_years": 8,
        "required_education": ["Grande École"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Marketing Automation Specialist",
        "description": """Éditeur SaaS cherche spécialiste Marketing Automation.

**Mission:**
- Implémenter les workflows automatisés
- Gérer HubSpot/Marketo
- Lead nurturing & scoring
- Optimiser le funnel

**Outils:**
- HubSpot, Marketo, Pardot
- Zapier, Make
- SQL (bases)
- Email design

**Profil:**
- 2+ ans en marketing automation
- Certifications HubSpot
- Data-driven
- Process-oriented

**Offre:**
- 38-50k€
- Remote 100%
- Formation certifications
- Outils modernes""",
        "required_skills": ["Marketing Automation", "HubSpot", "Lead Nurturing", "Email Marketing"],
        "nice_to_have_skills": ["SQL", "Zapier", "Marketo"],
        "min_experience_years": 2,
        "required_education": ["Bac+3 Marketing"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },

    # Sales & Business (10 offres)
    {
        "title": "Account Executive - B2B SaaS",
        "description": """Scale-up SaaS recherche AE pour closer des deals enterprise.

**Responsabilités:**
- Gérer le cycle de vente complet
- Closer des contrats 20-100k€
- Collaborer avec les SDRs et CSMs
- Atteindre les quotas

**Compétences:**
- Sales B2B
- Négociation
- Salesforce
- Solution selling

**Profil:**
- 3+ ans en vente B2B SaaS
- Track record de surperformance
- Hunter mentality
- Excellent relationnel

**Package:**
- Fixe: 40k€
- Variable: 40k€ (OTE 80k€)
- Equity
- Voiture de fonction""",
        "required_skills": ["Sales B2B", "Closing", "SaaS", "Salesforce"],
        "nice_to_have_skills": ["Enterprise Sales", "Négociation"],
        "min_experience_years": 3,
        "required_education": ["École de Commerce"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Sales Development Representative",
        "description": """Rejoignez notre équipe sales en tant que SDR.

**Mission:**
- Prospecter par email, LinkedIn, phone
- Qualifier les leads entrants
- Booker des démos pour les AEs
- Atteindre les objectifs (50+ meetings/mois)

**Outils:**
- Salesforce, Outreach, Apollo
- LinkedIn Sales Navigator
- Slack, Zoom

**Vous êtes:**
- Première expérience en sales
- Persévérant et résilient
- Excellent communicant
- Ambition de devenir AE

**Offre:**
- 30k€ fixe + 15k€ variable
- Formation intensive
- Évolution rapide
- Ambiance startup""",
        "required_skills": ["Prospection", "Cold Calling", "LinkedIn", "Qualification"],
        "nice_to_have_skills": ["Salesforce", "B2B"],
        "min_experience_years": 0,
        "required_education": ["Bac+3"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Head of Sales - France",
        "description": """Leader SaaS européen cherche Head of Sales France.

**Responsabilités:**
- Construire l'équipe sales (0→15)
- Définir la stratégie go-to-market
- Gérer les comptes stratégiques
- Reporting au VP Sales Europe

**Expertises:**
- Leadership sales confirmé
- B2B enterprise
- Recrutement & coaching
- Forecasting

**Profil:**
- 7+ ans en sales dont 3+ en management
- Track record de croissance
- Network solide
- Leadership inspirant

**Package:**
- 70-90k€ fixe
- Variable 60-80k€
- Equity
- Carte blanche""",
        "required_skills": ["Sales Leadership", "Management", "B2B", "Enterprise"],
        "nice_to_have_skills": ["SaaS", "Coaching", "Strategy"],
        "min_experience_years": 7,
        "required_education": ["Grande École"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Customer Success Manager",
        "description": """Nous cherchons un CSM passionné par la réussite client.

**Mission:**
- Onboarder les nouveaux clients
- Assurer l'adoption produit
- Identifier les opportunités d'upsell
- Réduire le churn

**Compétences:**
- Relation client excellence
- Gestion de portefeuille
- Product knowledge
- Data analysis

**Profil:**
- 2+ ans en CS ou account management
- SaaS B2B
- Proactif et empathique
- Orienté résultats

**Offre:**
- 38-48k€
- Variable sur renewal/upsell
- Remote 2j/semaine
- Formation produit""",
        "required_skills": ["Customer Success", "Account Management", "SaaS", "Onboarding"],
        "nice_to_have_skills": ["Upselling", "Churn Reduction"],
        "min_experience_years": 2,
        "required_education": ["Bac+5"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Business Developer - Partenariats",
        "description": """Développez notre réseau de partenaires stratégiques.

**Responsabilités:**
- Identifier et closer des partenariats
- Négocier les accords
- Gérer la relation partenaires
- Co-selling

**Skills:**
- Business development
- Négociation complexe
- Networking
- Strategic thinking

**Vous avez:**
- 4+ ans en BD/partenariats
- Network tech/SaaS
- Deals significatifs fermés
- Autonomie

**Package:**
- 45-60k€
- Variable attractif
- Frais illimités
- Remote flexible""",
        "required_skills": ["Business Development", "Partenariats", "Négociation", "Networking"],
        "nice_to_have_skills": ["SaaS", "Tech", "Channel Sales"],
        "min_experience_years": 4,
        "required_education": ["École de Commerce"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },

    # Operations & Finance (10 offres)
    {
        "title": "Chief of Staff - CEO Office",
        "description": """Startup Serie B cherche Chief of Staff pour son CEO.

**Mission:**
- Assister le CEO sur les sujets stratégiques
- Gérer des projets transverses
- Préparer le board
- Coordonner les équipes

**Compétences:**
- Strategic thinking
- Project management
- Business analysis
- Communication excellente

**Profil:**
- 3-5 ans en conseil ou ops
- Grande école
- Hyper polyvalent
- Discrétion

**Package:**
- 50-65k€
- Equity
- Vision 360° de l'entreprise
- Évolution rapide""",
        "required_skills": ["Strategy", "Project Management", "Analysis", "Communication"],
        "nice_to_have_skills": ["Consulting", "Startup"],
        "min_experience_years": 3,
        "required_education": ["Grande École"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Financial Controller",
        "description": """Scale-up recherche Financial Controller pour structurer la finance.

**Responsabilités:**
- Clôtures comptables mensuelles
- Reporting financier
- Budget & forecast
- Relations banques/investisseurs

**Compétences:**
- Comptabilité générale
- Consolidation
- Excel expert
- ERP (NetSuite, Sage)

**Profil:**
- 4+ ans en contrôle de gestion
- Startup/scale-up experience
- DSCG ou équivalent
- Rigueur & autonomie

**Offre:**
- 45-58k€
- Challenges
- Croissance forte
- Remote 2j/semaine""",
        "required_skills": ["Comptabilité", "Contrôle de Gestion", "Excel", "Reporting"],
        "nice_to_have_skills": ["NetSuite", "Consolidation", "DSCG"],
        "min_experience_years": 4,
        "required_education": ["Master Finance", "DSCG"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Operations Manager - Supply Chain",
        "description": """E-commerce leader cherche Operations Manager.

**Mission:**
- Optimiser la supply chain
- Gérer les stocks et flux
- Coordonner avec les 3PLs
- Améliorer les process

**Expertises:**
- Supply chain management
- Lean / Six Sigma
- Excel/SQL
- Project management

**Profil:**
- 3+ ans en ops/supply chain
- E-commerce ou retail
- Process-oriented
- Leadership

**Package:**
- 42-55k€
- Bonus performance
- Évolution rapide
- Impact direct""",
        "required_skills": ["Operations", "Supply Chain", "Excel", "Process"],
        "nice_to_have_skills": ["Lean", "SQL", "E-commerce"],
        "min_experience_years": 3,
        "required_education": ["Ingénieur", "Supply Chain"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "HR Business Partner",
        "description": """Scale-up tech recherche HRBP pour accompagner la croissance.

**Responsabilités:**
- Partenaire RH des managers
- Recrutement & talent acquisition
- People development
- Employee experience

**Compétences:**
- Recrutement tech
- Coaching managers
- SIRH (Workday, BambooHR)
- Employee engagement

**Profil:**
- 4+ ans en RH dont 2+ en HRBP
- Startup/tech experience
- Hands-on
- Bienveillant & exigeant

**Offre:**
- 42-55k€
- Equity
- Remote 2j/semaine
- Culture forte""",
        "required_skills": ["RH", "Recrutement", "Coaching", "Employee Experience"],
        "nice_to_have_skills": ["SIRH", "Tech", "Startup"],
        "min_experience_years": 4,
        "required_education": ["Master RH"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Legal Counsel - Tech & Data",
        "description": """Nous cherchons un juriste spécialisé tech pour notre équipe legal.

**Mission:**
- Rédiger et négocier les contrats
- Conseiller sur le RGPD
- IP & tech law
- M&A support

**Expertises:**
- Droit des contrats
- RGPD / data protection
- Propriété intellectuelle
- Droit des sociétés

**Profil:**
- 3+ ans en cabinet ou in-house
- Tech/SaaS experience
- CIPP/E apprécié
- Anglais juridique

**Package:**
- 50-65k€
- Remote 2j/semaine
- Formations continues
- Sujets variés""",
        "required_skills": ["Droit", "Contrats", "RGPD", "Tech Law"],
        "nice_to_have_skills": ["IP", "M&A", "CIPP"],
        "min_experience_years": 3,
        "required_education": ["Master 2 Droit", "DJCE"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },

    # Autres métiers (15 offres supplémentaires)
    {
        "title": "QA Engineer - Automation",
        "description": """Rejoignez notre équipe QA pour garantir la qualité produit.

**Responsabilités:**
- Créer des tests automatisés
- Tester les nouvelles features
- CI/CD integration
- Améliorer la couverture de tests

**Stack:**
- Selenium, Cypress, Playwright
- Jest, Pytest
- CI/CD (GitHub Actions, GitLab)
- API testing (Postman, Rest Assured)

**Profil:**
- 2+ ans en QA automation
- Coding skills (Python/JS)
- Mindset qualité
- Autonome

**Offre:**
- 38-50k€
- Remote 3j/semaine
- Formation
- Équipe bienveillante""",
        "required_skills": ["QA", "Automation", "Selenium", "Python"],
        "nice_to_have_skills": ["Cypress", "CI/CD", "API Testing"],
        "min_experience_years": 2,
        "required_education": ["Bac+3 Informatique"],
        "required_languages": ["Français"],
        "status": "PUBLISHED"
    },
    {
        "title": "Technical Writer - Documentation",
        "description": """Créez la meilleure documentation technique du marché.

**Mission:**
- Rédiger la documentation API
- Créer des guides utilisateurs
- Maintenir le knowledge base
- Collaborer avec product & engineering

**Skills:**
- Excellent rédacteur technique
- Markdown, Git
- Notion, Confluence
- Bases de code (lecture)

**Profil:**
- 2+ ans en technical writing
- Background tech
- Pédagogue
- Souci du détail

**Package:**
- 35-48k€
- Remote 100%
- Outils modernes
- Impact utilisateurs""",
        "required_skills": ["Technical Writing", "Documentation", "API", "Markdown"],
        "nice_to_have_skills": ["Git", "Developer Tools"],
        "min_experience_years": 2,
        "required_education": ["Bac+3"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Scrum Master / Agile Coach",
        "description": """Accompagnez nos équipes dans leur agilité.

**Responsabilités:**
- Animer les cérémonies Scrum
- Coacher les équipes
- Lever les blocages
- Amélioration continue

**Compétences:**
- Scrum Master certifié
- Facilitation
- Coaching
- Kanban

**Profil:**
- 3+ ans en Scrum Master
- PSM II ou équivalent
- Servant leadership
- Bienveillant

**Offre:**
- 45-58k€
- Remote flexible
- Certifications payées
- Équipes motivées""",
        "required_skills": ["Scrum", "Agile", "Coaching", "Facilitation"],
        "nice_to_have_skills": ["Kanban", "SAFe", "PSM"],
        "min_experience_years": 3,
        "required_education": ["Bac+5"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Community Manager - Social Media",
        "description": """Développez notre présence sur les réseaux sociaux.

**Mission:**
- Animer les communautés (Twitter, LinkedIn, Discord)
- Créer du contenu engageant
- Gérer les relations influenceurs
- Analyser les performances

**Compétences:**
- Social media management
- Création de contenu
- Canva, Figma (bases)
- Analytics

**Vous êtes:**
- 2+ ans en community management
- Créatif & réactif
- Excellent rédacteur
- Passion pour le digital

**Package:**
- 32-42k€
- Remote 100%
- Budget créatif
- Formation""",
        "required_skills": ["Community Management", "Social Media", "Content Creation", "Copywriting"],
        "nice_to_have_skills": ["Canva", "Analytics", "Influencer Marketing"],
        "min_experience_years": 2,
        "required_education": ["Bac+3 Communication"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
    {
        "title": "Office Manager - Paris",
        "description": """Nous cherchons un Office Manager pour nos bureaux parisiens.

**Responsabilités:**
- Gérer le quotidien du bureau
- Organiser les events
- Relation fournisseurs
- Accueil & onboarding

**Compétences:**
- Organisation impeccable
- Multitasking
- Outils bureautiques
- Sens du service

**Profil:**
- 2+ ans en office management
- Débrouillard
- Excellent relationnel
- Startup mindset

**Offre:**
- 32-40k€
- CDI
- Tickets restaurant
- Ambiance cool""",
        "required_skills": ["Office Management", "Organisation", "Events", "Communication"],
        "nice_to_have_skills": ["HR", "Facilities"],
        "min_experience_years": 2,
        "required_education": ["Bac+3"],
        "required_languages": ["Français", "Anglais"],
        "status": "PUBLISHED"
    },
]

# Compléter jusqu'à 100 offres avec des variations
def generate_all_offers() -> List[dict]:
    """Génère les 100 offres (base + variantes)"""
    all_offers = OFFERS_DATA.copy()
    
    # Variantes pour atteindre 100 offres
    variants = [
        ("Junior", 0, "Débutez votre carrière"),
        ("Senior", 2, "Expertise confirmée"),
        ("Lead", 3, "Leadership technique"),
    ]
    
    # Prendre les 8 premières offres tech pour créer des variantes
    base_offers_for_variants = OFFERS_DATA[:8]
    
    for offer in base_offers_for_variants:
        for variant_name, exp_add, prefix in variants:
            if len(all_offers) >= 100:
                break
                
            variant_offer = offer.copy()
            variant_offer["title"] = f"{variant_name} {offer['title']}"
            variant_offer["min_experience_years"] = max(0, offer.get("min_experience_years", 2) + exp_add - 2)
            
            # Ajuster description pour le niveau
            desc_prefix = f"**Niveau:** {prefix}\n\n"
            variant_offer["description"] = desc_prefix + offer["description"]
            
            all_offers.append(variant_offer)
        
        if len(all_offers) >= 100:
            break
    
    return all_offers[:100]

# -------------------------------------------------------------------
# CLEAN DATABASE
# -------------------------------------------------------------------
def truncate_tables(session: Session):
    """Nettoie toutes les tables avec TRUNCATE CASCADE"""
    logger.info("🗑️  Nettoyage de la base de données...")
    
    tables = [
        "parsed_cvs",
        "cv_texts",
        "cv_files",
        "applications",
        "candidates",
        "offers",
        "users",
    ]
    
    try:
        for table in tables:
            session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
        session.commit()
        logger.info("✅ Base de données nettoyée")
    except Exception as e:
        logger.error(f"❌ Erreur lors du nettoyage: {e}")
        session.rollback()
        raise

# -------------------------------------------------------------------
# SEED DATABASE
# -------------------------------------------------------------------
def seed_database():
    logger.info("🚀 Démarrage du seeding...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    # Attendre que PostgreSQL soit prêt
    wait_for_db(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # -------------------------------------------------------------------
        # CREATE TABLES
        # -------------------------------------------------------------------
        logger.info("📦 Création des tables...")
        Base.metadata.create_all(bind=engine)
        
        # -------------------------------------------------------------------
        # CLEAN
        # -------------------------------------------------------------------
        truncate_tables(session)
        
        # -------------------------------------------------------------------
        # USERS (5 utilisateurs)
        # -------------------------------------------------------------------
        logger.info("👤 Création des utilisateurs...")
        
        users = []
        for user_data in USERS_DATA:
            user = User(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"],
                is_active=True,
            )
            users.append(user)
        
        session.add_all(users)
        session.commit()
        
        for user in users:
            session.refresh(user)
        
        logger.info(f"  ✓ {len(users)} utilisateurs créés")
        
        # -------------------------------------------------------------------
        # OFFERS (100 offres)
        # -------------------------------------------------------------------
        logger.info("📋 Création des offres...")
        
        all_offers_data = generate_all_offers()
        recruiters = [u for u in users if u.role == UserRole.RECRUITER]
        admin = [u for u in users if u.role == UserRole.ADMIN][0]
        
        offers = []
        for i, offer_data in enumerate(all_offers_data):
            # Alterner entre les recruteurs
            owner = recruiters[i % len(recruiters)] if i % 5 != 0 else admin
            
            offer = Offer(
                title=offer_data["title"],
                description=offer_data["description"],
                status=offer_data.get("status", "PUBLISHED"),
                deleted=False,
                owner_id=owner.id,
                required_skills=offer_data.get("required_skills", []),
                nice_to_have_skills=offer_data.get("nice_to_have_skills", []),
                min_experience_years=offer_data.get("min_experience_years", 0),
                required_education=offer_data.get("required_education", []),
                required_languages=offer_data.get("required_languages", ["Français"]),
            )
            offers.append(offer)
        
        # Bulk insert en batch de 50 pour éviter les timeouts
        batch_size = 50
        for i in range(0, len(offers), batch_size):
            batch = offers[i:i+batch_size]
            session.add_all(batch)
            session.commit()
            logger.info(f"  → {min(i+batch_size, len(offers))}/{len(offers)} offres créées")
        
        # -------------------------------------------------------------------
        # DONE
        # -------------------------------------------------------------------
        logger.info("=" * 80)
        logger.info("✅ SEED TERMINÉ AVEC SUCCÈS")
        logger.info("=" * 80)
        
        logger.info("\n🔐 Comptes de test:")
        logger.info("-" * 80)
        for user_data in USERS_DATA:
            role = "ADMIN" if user_data["role"] == UserRole.ADMIN else "RECRUTEUR"
            logger.info(f"{role:10} → {user_data['email']:30} / {user_data['password']}")
        
        logger.info("\n📊 Statistiques:")
        logger.info(f"  • Utilisateurs: {len(users)}")
        logger.info(f"  • Offres: {len(offers)}")
        logger.info(f"  • Offres publiées: {sum(1 for o in offers if o.status == 'PUBLISHED')}")
        
        logger.info("\n📘 Documentation API:")
        logger.info("  • Swagger UI: http://localhost:8000/docs")
        logger.info("  • ReDoc: http://localhost:8000/redoc")
        
    except Exception as e:
        session.rollback()
        logger.exception("❌ Échec du seeding")
        raise
    finally:
        session.close()
        logger.info("\n🔌 Connexion DB fermée")

# -------------------------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("⚠️  ATTENTION : ce script SUPPRIME toutes les données existantes")
    logger.info("=" * 80)
    input("Appuyez sur ENTRÉE pour continuer...")
    seed_database()
