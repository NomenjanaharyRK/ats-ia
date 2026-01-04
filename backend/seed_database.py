#!/usr/bin/env python3
"""Script de seed pour initialiser la base de données avec des données de test.

Ce script:
- Supprime toutes les données existantes (ATTENTION: destructif!)
- Crée des utilisateurs de test (admin et recruteur)
- Crée des offres d'emploi
- Affiche les informations de connexion

Utilisation:
    python seed_database.py
"""
import sys
import os
from pathlib import Path

# Ajouter le dossier backend au PYTHONPATH
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import des modèles
from app.models.user import User, UserRole
from app.models.offer import Offer
from app.models.candidate import Candidate
from app.models.application import Application
from app.models.cv_file import CVFile
from app.models.cv_text import CVText
from app.models.parsed_cv import ParsedCV
from app.db.base import Base
from app.core.config import settings

# Context pour hasher les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hashe un mot de passe."""
    return pwd_context.hash(password)


def delete_all_data(session):
    """Supprime toutes les données dans l'ordre correct (respect des contraintes FK)."""
    logger.info("🗑️  Suppression de toutes les données existantes...")
    
    try:
        # Ordre important: supprimer d'abord les enfants, puis les parents
        session.execute(text("DELETE FROM parsed_cvs"))
        session.execute(text("DELETE FROM cv_texts"))
        session.execute(text("DELETE FROM cv_files"))
        session.execute(text("DELETE FROM applications"))
        session.execute(text("DELETE FROM candidates"))
        session.execute(text("DELETE FROM offers"))
        session.execute(text("DELETE FROM users"))
        
        session.commit()
        logger.info("✅ Toutes les données ont été supprimées")
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Erreur lors de la suppression: {e}")
        raise


def seed_database():
    """Initialise la base de données avec des données de test."""
    logger.info("🚀 Démarrage du seeding de la base de données...")
    
    # Créer la connexion
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Supprimer toutes les données existantes
        delete_all_data(session)
        
        logger.info("\n👤 Création des utilisateurs...")
        
        # Créer un administrateur
        admin = User(
            email="admin@ats-ia.com",
            hashed_password=get_password_hash("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        session.add(admin)
        logger.info("  ✓ Admin créé: admin@ats-ia.com / Admin@123")
        
        # Créer un recruteur
        recruiter = User(
            email="recruteur@ats-ia.com",
            hashed_password=get_password_hash("Recruteur@123"),
            role=UserRole.RECRUITER,
            is_active=True
        )
        session.add(recruiter)
        logger.info("  ✓ Recruteur créé: recruteur@ats-ia.com / Recruteur@123")
        
        session.commit()
        session.refresh(admin)
        session.refresh(recruiter)
        
        logger.info("\n📋 Création des offres d'emploi...")
        
        # Offre 1: Développeur Python Senior
        offer1 = Offer(
            title="Développeur Python Senior",
            description="""Nous recherchons un développeur Python senior pour rejoindre notre équipe.

Missions:
- Développer des applications web avec FastAPI
- Concevoir et optimiser des bases de données PostgreSQL
- Mettre en place des pipelines CI/CD
- Travailler avec des technologies IA et Machine Learning

Compétences requises:
- Python (5+ ans d'expérience)
- FastAPI, Django ou Flask
- PostgreSQL, Redis
- Docker, Kubernetes
- Git, CI/CD
- Expérience en Machine Learning (scikit-learn, TensorFlow)

Compétences appréciées:
- NLP et traitement de texte
- Celery, RabbitMQ
- React, TypeScript
- Anglais courant
""",
            status="PUBLISHED",
            deleted=False,
            owner_id=recruiter.id
        )
        session.add(offer1)
        logger.info("  ✓ Offre créée: Développeur Python Senior")
        
        # Offre 2: Data Scientist
        offer2 = Offer(
            title="Data Scientist",
            description="""Rejoignez notre équipe data science pour développer des modèles d'IA innovants.

Missions:
- Développer des modèles de Machine Learning
- Analyser et visualiser des données complexes
- Mettre en production des modèles ML
- Collaborer avec les équipes produit et engineering

Compétences requises:
- Python (pandas, numpy, scikit-learn)
- Machine Learning et Deep Learning
- SQL et bases de données
- Statistiques et mathématiques
- Jupyter, Git

Compétences appréciées:
- TensorFlow, PyTorch
- NLP et Computer Vision
- Big Data (Spark, Hadoop)
- MLOps (MLflow, Kubeflow)
- Anglais professionnel
""",
            status="PUBLISHED",
            deleted=False,
            owner_id=recruiter.id
        )
        session.add(offer2)
        logger.info("  ✓ Offre créée: Data Scientist")
        
        # Offre 3: Ingénieur DevOps
        offer3 = Offer(
            title="Ingénieur DevOps",
            description="""Nous recherchons un ingénieur DevOps pour automatiser et optimiser notre infrastructure.

Missions:
- Gérer l'infrastructure cloud (AWS/GCP/Azure)
- Mettre en place et maintenir les pipelines CI/CD
- Automatiser les déploiements avec Docker et Kubernetes
- Monitorer et optimiser les performances
- Assurer la sécurité et la fiabilité des systèmes

Compétences requises:
- Docker, Kubernetes
- CI/CD (GitLab CI, GitHub Actions, Jenkins)
- Cloud (AWS, GCP ou Azure)
- Linux, Bash, Python
- Terraform, Ansible

Compétences appréciées:
- Monitoring (Prometheus, Grafana)
- ELK Stack
- Sécurité et conformité
- PostgreSQL, Redis
- Anglais technique
""",
            status="PUBLISHED",
            deleted=False,
            owner_id=admin.id
        )
        session.add(offer3)
        logger.info("  ✓ Offre créée: Ingénieur DevOps")
        
        # Offre 4: Full Stack Developer
        offer4 = Offer(
            title="Développeur Full Stack",
            description="""Rejoignez notre équipe pour développer des applications web modernes.

Missions:
- Développer le frontend avec React et TypeScript
- Créer des APIs REST avec FastAPI ou Node.js
- Gérer les bases de données PostgreSQL
- Participer à la conception UX/UI
- Assurer la qualité du code (tests, code review)

Compétences requises:
- React, TypeScript, HTML/CSS
- FastAPI, Node.js ou Django
- PostgreSQL, MongoDB
- Git, REST APIs
- 3+ ans d'expérience

Compétences appréciées:
- Next.js, TailwindCSS
- GraphQL
- Docker
- Tests automatisés (Jest, Pytest)
- Expérience en design UX/UI
""",
            status="PUBLISHED",
            deleted=False,
            owner_id=recruiter.id
        )
        session.add(offer4)
        logger.info("  ✓ Offre créée: Développeur Full Stack")
        
        # Offre 5: Product Manager
        offer5 = Offer(
            title="Product Manager",
            description="""Nous cherchons un Product Manager pour piloter le développement de nos produits.

Missions:
- Définir la vision et la roadmap produit
- Gérer le backlog et prioriser les features
- Coordonner les équipes tech, design et business
- Analyser les métriques et le feedback utilisateurs
- Réaliser des études de marché et veille concurrentielle

Compétences requises:
- 5+ ans d'expérience en Product Management
- Méthodologies Agile/Scrum
- Analyse de données et métriques
- Communication et leadership
- Outils de gestion de projet (Jira, Notion)

Compétences appréciées:
- Expérience en tech/SaaS
- Connaissance en UX/UI design
- Notions techniques (APIs, databases)
- Expérience en IA/ML
- Anglais courant
""",
            status="DRAFT",
            deleted=False,
            owner_id=admin.id
        )
        session.add(offer5)
        logger.info("  ✓ Offre créée: Product Manager (brouillon)")
        
        session.commit()
        
        logger.info("\n" + "="*60)
        logger.info("✅ SEED TERMINÉ AVEC SUCCÈS!")
        logger.info("="*60)
        logger.info("\n📝 INFORMATIONS DE CONNEXION:\n")
        logger.info("👤 Administrateur:")
        logger.info("   Email    : admin@ats-ia.com")
        logger.info("   Password : Admin@123")
        logger.info("   Role     : ADMIN\n")
        logger.info("👤 Recruteur:")
        logger.info("   Email    : recruteur@ats-ia.com")
        logger.info("   Password : Recruteur@123")
        logger.info("   Role     : RECRUITER\n")
        logger.info("📋 Offres créées: 5 (4 publiées, 1 brouillon)\n")
        logger.info("🔗 API Docs: http://localhost:8000/docs")
        logger.info("="*60)
        
    except Exception as e:
        session.rollback()
        logger.error(f"\n❌ ERREUR lors du seeding: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    finally:
        session.close()
        logger.info("\n🔌 Connexion à la base de données fermée")


if __name__ == "__main__":
    logger.info("\n" + "="*60)
    logger.info("⚠️  ATTENTION: Ce script va SUPPRIMER toutes les données!")
    logger.info("="*60 + "\n")
    
    try:
        seed_database()
    except Exception as e:
        logger.error(f"Échec du seeding: {e}")
        sys.exit(1)
