# Sprint 6 - RBAC (Role-Based Access Control) Implementation

## Objectif
Implementer un systeme de controle d'acces simplifie avec 2 roles:
- **ADMIN** : Acces complet (gestion users, offres, configuration)
- **RECRUITER** : Acces limite (creer/lire offres, voir candidatures)

## Fichiers crees/modifies

### 1. Modele AuditLog (`backend/app/models/auditlog.py`)
Table pour journaliser les actions sensibles:
- USER_CREATED, USER_UPDATED, USER_DELETED, USER_ROLE_CHANGED
- OFFER_CREATED, OFFER_UPDATED, OFFER_DELETED
- APPLICATION_SUBMITTED
- LOGIN_SUCCESS, LOGIN_FAILED

Champs:
- `actor_id`: User qui a fait l'action
- `action`: Type d'action (enum)
- `resource_type`: "User", "Offer", "Application"
- `resource_id`: ID de la ressource
- `old_values`: Ancien state (JSON)
- `new_values`: Nouveau state (JSON)
- `created_at`: Timestamp

### 2. Schemas Pydantic (`backend/app/schemas/user_schema.py`)
- `UserRoleEnum`: ADMIN, RECRUITER
- `UserCreate`: email, password, role (default RECRUITER)
- `UserUpdate`: email, is_active, role (optionnels)
- `UserResponse`: id, email, role, is_active, created_at
- `UserDetailResponse`: + updated_at, last_login
- `RoleChangeRequest`: new_role
- `AuditLogResponse`: Pour reponses audit logs

### 3. Permissions Decorators (`backend/app/core/permissions.py`)
Fonctions decorators pour restreindre acces:
```python
@require_role(UserRole.ADMIN)
@require_role([UserRole.RECRUITER, UserRole.ADMIN])
@require_admin()  # shortcut
@require_recruiter_or_admin()  # shortcut
```

### 4. Admin Endpoints (`backend/app/api/v1/admin.py`)
Endpoints protege ADMIN:

#### Users Management
- `GET /api/v1/admin/users` - Lister tous les users
- `GET /api/v1/admin/users/{user_id}` - Details d'un user
- `POST /api/v1/admin/users` - Creer nouvel user
- `PATCH /api/v1/admin/users/{user_id}/role` - Changer role
- `DELETE /api/v1/admin/users/{user_id}` - Supprimer user

#### Audit Logs
- `GET /api/v1/admin/audit-logs?limit=100&offset=0` - Recuperer logs

Chaque action loggee automatiquement dans AuditLog.

## Structure RBAC

### Routes protegees

#### ADMIN uniquement
- `/api/v1/admin/**` (gestion users, audit logs)

#### RECRUITER + ADMIN
- `/api/v1/offers` (creer, lister offres)
- `/api/v1/offers/{id}/applications` (soumettre candidature)
- `/api/v1/offers/{id}/applications/scoring` (voir scoring)

#### Tous (connectes)
- `/api/v1/auth/login`
- `/api/v1/auth/refresh`
- `/ping`, `/health`

## Migration DB

Pour creer la table `audit_logs`:
```bash
docker exec -it ats-ia-backend-1 alembic revision --autogenerate -m "Add AuditLog table"
docker exec -it ats-ia-backend-1 alembic upgrade head
```

## Integration dans main.py

Ajouter la route admin dans `backend/app/main.py`:
```python
from app.api.v1 import admin

app.include_router(admin.router)
```

## Tests API

### 1. Login Admin
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=admin@example.com&password=adminpassword"
```
Reponse:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

### 2. Lister tous les users (ADMIN)
```bash
curl -X GET http://localhost:8000/api/v1/admin/users \\
  -H "Authorization: Bearer <access_token>"
```

### 3. Creer nouvel user (ADMIN)
```bash
curl -X POST http://localhost:8000/api/v1/admin/users \\
  -H "Authorization: Bearer <access_token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "recruiter@example.com",
    "password": "securepass123",
    "role": "RECRUITER"
  }'
```

### 4. Changer role d'un user (ADMIN)
```bash
curl -X PATCH http://localhost:8000/api/v1/admin/users/2/role \\
  -H "Authorization: Bearer <access_token>" \\
  -H "Content-Type: application/json" \\
  -d '{"new_role": "ADMIN"}'
```

### 5. Recuperer audit logs (ADMIN)
```bash
curl -X GET http://localhost:8000/api/v1/admin/audit-logs?limit=50 \\
  -H "Authorization: Bearer <access_token>"
```

## Prochaines etapes (Sprint 7+)
- Antivirus sur uploads
- Quotas d'upload par user
- Conformite RGPD (retention donnees)
- UI pour recruiter (filtres, tri)
- MLOps pour optimiser scoring
