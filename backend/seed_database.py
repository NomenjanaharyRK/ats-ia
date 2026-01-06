#!/usr/bin/env python3
"""
Script de seed pour initialiser la base de données avec des données de test.

- Crée automatiquement les tables si elles n'existent pas
- Nettoie la base avec TRUNCATE CASCADE (safe pour FK)
- Crée des utilisateurs et des offres de test
"""

import sys
from pathlib import Path
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
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
# IMPORTS APP
# -------------------------------------------------------------------
from app.db.base import Base
from app.core.config import settings

from app.models.user import User, UserRole
from app.models.offer import Offer
from app.models.candidate import Candidate
from app.models.application import Application
from app.models.cv_file import CVFile
from app.models.cv_text import CVText
from app.models.parsed_cv import ParsedCV

# -------------------------------------------------------------------
# PASSWORD HASH
# -------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# -------------------------------------------------------------------
# CLEAN DATABASE
# -------------------------------------------------------------------
def truncate_tables(session):
    """
    Nettoie toutes les tables existantes.
    TRUNCATE CASCADE évite les problèmes de FK.
    """
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

    for table in tables:
        session.execute(
            text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
        )

    session.commit()
    logger.info("✅ Base de données nettoyée")


# -------------------------------------------------------------------
# SEED DATABASE
# -------------------------------------------------------------------
def seed_database():
    logger.info("🚀 Démarrage du seeding...")

    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # -------------------------------------------------------------------
        # CREATE TABLES
        # -------------------------------------------------------------------
        logger.info("📦 Création des tables (si inexistantes)...")
        Base.metadata.create_all(bind=engine)

        # -------------------------------------------------------------------
        # CLEAN
        # -------------------------------------------------------------------
        truncate_tables(session)

        # -------------------------------------------------------------------
        # USERS
        # -------------------------------------------------------------------
        logger.info("👤 Création des utilisateurs...")

        admin = User(
            email="admin@ats-ia.com",
            hashed_password=hash_password("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True,
        )

        recruiter = User(
            email="recruteur@ats-ia.com",
            hashed_password=hash_password("Recruteur@123"),
            role=UserRole.RECRUITER,
            is_active=True,
        )

        session.add_all([admin, recruiter])
        session.commit()

        session.refresh(admin)
        session.refresh(recruiter)

        logger.info("  ✓ Admin créé")
        logger.info("  ✓ Recruteur créé")

        # -------------------------------------------------------------------
        # OFFERS
        # -------------------------------------------------------------------
        logger.info("📋 Création des offres...")

        offers = [
            Offer(
                title="Développeur Python Senior",
                description="Développement backend Python / FastAPI / PostgreSQL.",
                status="PUBLISHED",
                deleted=False,
                owner_id=recruiter.id,
            ),
            Offer(
                title="Data Scientist",
                description="Machine Learning, NLP, Python, MLOps.",
                status="PUBLISHED",
                deleted=False,
                owner_id=recruiter.id,
            ),
            Offer(
                title="Ingénieur DevOps",
                description="Docker, Kubernetes, CI/CD, Cloud.",
                status="PUBLISHED",
                deleted=False,
                owner_id=admin.id,
            ),
            Offer(
                title="Développeur Full Stack",
                description="React, TypeScript, FastAPI.",
                status="PUBLISHED",
                deleted=False,
                owner_id=recruiter.id,
            ),
            Offer(
                title="Product Manager",
                description="Roadmap produit, Agile, coordination équipes.",
                status="DRAFT",
                deleted=False,
                owner_id=admin.id,
            ),
        ]

        session.add_all(offers)
        session.commit()

        logger.info("  ✓ 5 offres créées")

        # -------------------------------------------------------------------
        # DONE
        # -------------------------------------------------------------------
        logger.info("=" * 60)
        logger.info("✅ SEED TERMINÉ AVEC SUCCÈS")
        logger.info("=" * 60)

        logger.info("🔐 Comptes de test :")
        logger.info("ADMIN     → admin@ats-ia.com / Admin@123")
        logger.info("RECRUITER → recruteur@ats-ia.com / Recruteur@123")
        logger.info("📘 Swagger → http://localhost:8000/docs")

    except Exception as e:
        session.rollback()
        logger.exception("❌ Échec du seeding")
        raise
    finally:
        session.close()
        logger.info("🔌 Connexion DB fermée")


# -------------------------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("⚠️  ATTENTION : ce script SUPPRIME toutes les données")
    logger.info("=" * 60)
    seed_database()
