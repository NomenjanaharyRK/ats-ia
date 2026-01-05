# Sprint 6 - Quick Deploy Guide

## 3 Commandes a executer (Copy-Paste)

Ouvre un terminal dans le dossier du projet et execute ces 3 commandes dans l'ordre:

---

## 1. Git Pull

```bash
git pull origin main
```

**Attend**: Download des fichiers (2-3 secondes)
**Output attendu**: "X files changed, Y insertions, Z deletions"

---

## 2. Docker Rebuild

```bash
docker compose up -d --build
```

**Attend**: Construction des images (30-60 secondes)
**Output attendu**: "Building backend service" puis "Container ats-ia-backend-1 created/updated"

---

## 3. Migration Database

```bash
docker exec -it ats-ia-backend-1 alembic revision --autogenerate -m "Add AuditLog table" && docker exec -it ats-ia-backend-1 alembic upgrade head
```

**Attend**: Migration (5-10 secondes)
**Output attendu**: "Running migration" puis "Create table audit_logs" puis "Done"

---

## Apres les 3 commandes

Une fois termine:

1. **Ouvrir VSCode** et modifier `backend/app/main.py`
   - Ajouter apres les imports: `from app.api.v1 import admin`
   - Ajouter dans le code: `app.include_router(admin.router)`
   - Sauvegarder (le backend redemarrera automatiquement)

2. **Verifier** que tout fonctionne:
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Swagger docs
   open http://localhost:8000/docs
   ```

---

## Fichiers crees par Sprint 6

✅ `backend/app/models/auditlog.py` - Modele pour tracker les actions
✅ `backend/app/schemas/user_schema.py` - Schemas Pydantic pour users
✅ `backend/app/core/permissions.py` - Decorators pour RBAC
✅ `backend/app/api/v1/admin.py` - Endpoints admin (6 endpoints)
✅ `SPRINT6_GUIDE.md` - Documentation complete
✅ `SPRINT6_COMPLETION_STATUS.md` - Status de completion

---

## Endpoints Admin disponibles

Au lieu de `<access_token>`, utilise le token obtenu apres login

```bash
# 1. Login admin
curl -X POST http://localhost:8000/api/v1/auth/login \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=admin@example.com&password=adminpassword"

# 2. Lister tous les users (ADMIN ONLY)
curl http://localhost:8000/api/v1/admin/users \\
  -H "Authorization: Bearer <access_token>"

# 3. Creer nouvel user (ADMIN ONLY)
curl -X POST http://localhost:8000/api/v1/admin/users \\
  -H "Authorization: Bearer <access_token>" \\
  -H "Content-Type: application/json" \\
  -d '{"email":"recruiter@example.com", "password":"pass123", "role":"RECRUITER"}'

# 4. Changer role d'un user (ADMIN ONLY)
curl -X PATCH http://localhost:8000/api/v1/admin/users/2/role \\
  -H "Authorization: Bearer <access_token>" \\
  -H "Content-Type: application/json" \\
  -d '{"new_role":"ADMIN"}'

# 5. Recuperer audit logs (ADMIN ONLY)
curl http://localhost:8000/api/v1/admin/audit-logs?limit=50 \\
  -H "Authorization: Bearer <access_token>"
```

---

## Si erreur

**Erreur: "Cannot find auditlog"**
- Assure-toi que tu as fait `git pull` correctement
- Verifie que les fichiers sont dans `backend/app/models/` et `backend/app/schemas/`

**Erreur: "RBAC table doesn't exist"**
- C'est normal si tu relances Docker
- Refais les 2 commandes de migration (step 3)

**Erreur: "Module admin not found"**
- Tu as oublie d'ajouter l'import dans `backend/app/main.py`
- Verifie que tu as ajoute: `from app.api.v1 import admin` et `app.include_router(admin.router)`

---

## Contact

Si probleme: Consulte `DEPLOYMENT_COMMANDS.sh` pour plus de details
