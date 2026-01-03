# 🚀 SPRINT 4 : Optimisation DB + Pagination API

## 📋 Objectif
Améliorer les performances de l'API et de la base de données pour gérer efficacement des milliers de candidatures.

---

## ✅ Changements à implémenter

### 1. Pagination API (backend/app/api/v1/applications.py)

#### Ligne 127 : Modifier le response_model
```python
@router.get(
    "/{offer_id}/applications",
    response_model=dict,  # Changé de List[ApplicationRead]
)
```

#### Ligne 129-133 : Ajouter paramètres de pagination
```python
def list_applications_for_offer(
    offer_id: int,
    skip: int = 0,        # NOUVEAU
    limit: int = 100,     # NOUVEAU
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
```

#### Ligne 143-154 : Remplacer la query complète par
```python
    # Count total
    total = db.query(Application).filter(Application.offer_id == offer_id).count()
    
    # Query avec pagination
    apps = (
        db.query(Application)
        .filter(Application.offer_id == offer_id)
        .options(joinedload(Application.candidate))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return {
        "items": apps,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

---

### 2. Migration Alembic pour Indexes DB

#### Étape 1 : Créer la migration
```bash
docker exec -it ats-ia-backend-1 alembic revision -m "add_indexes_applications_offer_candidate"
```

#### Étape 2 : Éditer le fichier généré dans `backend/alembic/versions/`

```python
"""add indexes applications offer candidate

Revision ID: xxxxx
Revises: yyyyy
Create Date: 2026-01-03
"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    # Indexes pour améliorer performances des requêtes
    op.create_index('idx_applications_offer_id', 'applications', ['offer_id'])
    op.create_index('idx_applications_candidate_id', 'applications', ['candidate_id'])
    op.create_index('idx_cv_texts_application_id', 'cv_texts', ['application_id'])


def downgrade():
    op.drop_index('idx_cv_texts_application_id', 'cv_texts')
    op.drop_index('idx_applications_candidate_id', 'applications')
    op.drop_index('idx_applications_offer_id', 'applications')
```

#### Étape 3 : Appliquer la migration
```bash
docker exec -it ats-ia-backend-1 alembic upgrade head
```

---

## 🧪 Tests de Validation

### Test 1 : Pagination fonctionne
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  "http://localhost:8000/api/v1/offers/1/applications?skip=0&limit=10"

# Réponse attendue :
{
  "items": [...],
  "total": 50,
  "skip": 0,
  "limit": 10
}
```

### Test 2 : Indexes sont utilisés
```sql
docker exec -it ats-ia-db-1 psql -U ats_user -d ats

EXPLAIN ANALYZE SELECT * FROM applications WHERE offer_id = 1;

-- Doit afficher :
-- Index Scan using idx_applications_offer_id on applications
```

### Test 3 : Performance améliorée
Avant : ~500ms pour 10k candidatures  
Après : ~50ms avec indexes  
**(10x plus rapide !)**

---

## 📊 Impact Attendu

| Métrique | Avant | Après | Gain |
|----------|-------|-------|------|
| Temps requête (10k rows) | 500ms | 50ms | **10x** |
| Mémoire utilisée | 100% résultats | 10% (limit=100) | **90% réduit** |
| Scalabilité | 10k max | 100k+ | **10x** |

---

## ✅ Checklist d'Implémentation

- [ ] Modifier `applications.py` (pagination)
- [ ] Créer migration Alembic (indexes)
- [ ] Appliquer migration (`alembic upgrade head`)
- [ ] Tester pagination via curl
- [ ] Vérifier indexes avec EXPLAIN ANALYZE
- [ ] Mesurer amélioration performance
- [ ] Commit + Push sur branche `sprint4-optimiser-db`
- [ ] Créer PR #6

---

## 🎯 Critères d'Acceptation

✅ GET `/offers/1/applications?skip=0&limit=50` retourne 50 items max  
✅ Réponse JSON contient `{items, total, skip, limit}`  
✅ EXPLAIN ANALYZE montre "Index Scan using idx_applications_offer_id"  
✅ Requête <100ms même avec 50k candidatures  
✅ Tests passent (si ajoutés)  

---

## 📚 Ressources

- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)
- [SQLAlchemy Pagination](https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.limit)
- [Alembic Migrations](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostgreSQL Indexes](https://www.postgresql.org/docs/current/indexes.html)

---

**Auteur** : Sprint 4 - Optimisation DB + Pagination  
**Date** : 2026-01-03  
**Priorité** : Haute (avant production)
