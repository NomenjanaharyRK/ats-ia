# 📚 Instructions pour Seeder la Base de Données

## ⚠️ ATTENTION

**Ce script supprime TOUTES les données existantes dans la base de données !**

Utilisez-le uniquement pour:
- Initialiser une nouvelle base de données
- Réinitialiser complètement l'application pour les tests
- Développement local

**NE JAMAIS** l'utiliser en production !

---

## 🎯 Ce que fait le script

### Suppression des données
Le script supprime toutes les données dans l'ordre correct pour respecter les contraintes de clés étrangères:
1. `parsed_cvs` - CV analysés
2. `cv_texts` - Textes extraits des CV
3. `cv_files` - Fichiers CV
4. `applications` - Candidatures
5. `candidates` - Candidats
6. `offers` - Offres d'emploi
7. `users` - Utilisateurs

### Création des données de test

#### 👥 Utilisateurs (2)
| Rôle | Email | Mot de passe |
|------|-------|-------------|
| **Admin** | `admin@ats-ia.com` | `Admin@123` |
| **Recruteur** | `recruteur@ats-ia.com` | `Recruteur@123` |

#### 📋 Offres d'emploi (5)

1. **Développeur Python Senior** (PUBLISHED)
   - Stack: Python, FastAPI, PostgreSQL, Docker, ML
   - Propriétaire: Recruteur

2. **Data Scientist** (PUBLISHED)
   - Stack: Python, ML/DL, TensorFlow, NLP
   - Propriétaire: Recruteur

3. **Ingénieur DevOps** (PUBLISHED)
   - Stack: Docker, Kubernetes, AWS/GCP/Azure, CI/CD
   - Propriétaire: Admin

4. **Développeur Full Stack** (PUBLISHED)
   - Stack: React, TypeScript, FastAPI, PostgreSQL
   - Propriétaire: Recruteur

5. **Product Manager** (DRAFT)
   - Compétences: Agile, Product Management, métriques
   - Propriétaire: Admin

---

## 🚀 Utilisation

### Prérequis

1. **Docker doit être lancé** avec la base de données PostgreSQL:
   ```bash
   docker-compose up -d postgres
   ```

2. **Les migrations Alembic doivent être appliquées**:
   ```bash
   cd backend
   alembic upgrade head
   ```

### Exécution du script

#### Option 1: Depuis le dossier backend
```bash
cd backend
python seed_database.py
```

#### Option 2: Depuis Docker (si backend en conteneur)
```bash
docker-compose exec backend python seed_database.py
```

#### Option 3: Depuis la racine du projet
```bash
python backend/seed_database.py
```

---

## 📊 Résultat attendu

Vous devriez voir un output similaire à:

```
============================================================
⚠️  ATTENTION: Ce script va SUPPRIMER toutes les données!
============================================================

2026-01-05 01:00:00 - __main__ - INFO - 🚀 Démarrage du seeding de la base de données...
2026-01-05 01:00:00 - __main__ - INFO - 🗑️  Suppression de toutes les données existantes...
2026-01-05 01:00:00 - __main__ - INFO - ✅ Toutes les données ont été supprimées

2026-01-05 01:00:00 - __main__ - INFO - 👤 Création des utilisateurs...
2026-01-05 01:00:00 - __main__ - INFO -   ✓ Admin créé: admin@ats-ia.com / Admin@123
2026-01-05 01:00:00 - __main__ - INFO -   ✓ Recruteur créé: recruteur@ats-ia.com / Recruteur@123

2026-01-05 01:00:00 - __main__ - INFO - 📋 Création des offres d'emploi...
2026-01-05 01:00:00 - __main__ - INFO -   ✓ Offre créée: Développeur Python Senior
2026-01-05 01:00:00 - __main__ - INFO -   ✓ Offre créée: Data Scientist
2026-01-05 01:00:00 - __main__ - INFO -   ✓ Offre créée: Ingénieur DevOps
2026-01-05 01:00:00 - __main__ - INFO -   ✓ Offre créée: Développeur Full Stack
2026-01-05 01:00:00 - __main__ - INFO -   ✓ Offre créée: Product Manager (brouillon)

============================================================
✅ SEED TERMINÉ AVEC SUCCÈS!
============================================================

📝 INFORMATIONS DE CONNEXION:

👤 Administrateur:
   Email    : admin@ats-ia.com
   Password : Admin@123
   Role     : ADMIN

👤 Recruteur:
   Email    : recruteur@ats-ia.com
   Password : Recruteur@123
   Role     : RECRUITER

📋 Offres créées: 5 (4 publiées, 1 brouillon)

🔗 API Docs: http://localhost:8000/docs
============================================================

🔌 Connexion à la base de données fermée
```

---

## 🧪 Tester la connexion

Après le seeding, testez la connexion:

### Via l'API Swagger UI
1. Ouvrir: http://localhost:8000/docs
2. Tester l'endpoint `/auth/login`
3. Utiliser les credentials ci-dessus

### Via curl
```bash
# Test connexion Admin
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@ats-ia.com&password=Admin@123"

# Test connexion Recruteur
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=recruteur@ats-ia.com&password=Recruteur@123"
```

### Lister les offres
```bash
# Obtenir le token d'abord
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=recruteur@ats-ia.com&password=Recruteur@123" \
  | jq -r '.access_token')

# Lister les offres
curl -X GET "http://localhost:8000/api/v1/offers" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🐛 Dépannage

### Erreur: "ModuleNotFoundError: No module named 'app'"
**Solution**: Assurez-vous d'être dans le dossier `backend/` ou ajoutez-le au PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

### Erreur: "could not connect to server"
**Solution**: Vérifiez que PostgreSQL est lancé:
```bash
docker-compose ps postgres
# Si arrêté:
docker-compose up -d postgres
```

### Erreur: "relation does not exist"
**Solution**: Appliquez les migrations Alembic:
```bash
cd backend
alembic upgrade head
```

### Erreur de clé étrangère lors de la suppression
**Solution**: Le script gère déjà l'ordre correct, mais si le problème persiste:
1. Arrêtez tous les conteneurs: `docker-compose down`
2. Supprimez les volumes: `docker-compose down -v`
3. Relancez: `docker-compose up -d`
4. Appliquez les migrations: `alembic upgrade head`
5. Relancez le seed: `python seed_database.py`

---

## 📝 Notes importantes

1. **Environnement**: Le script utilise les variables d'environnement de `app/core/config.py`
2. **Mots de passe**: Les mots de passe sont hashés avec bcrypt
3. **Transaction**: Toutes les opérations sont dans une transaction avec rollback en cas d'erreur
4. **Logging**: Le script log toutes les opérations pour faciliter le debugging

---

## 🔄 Réinitialisation complète

Pour une réinitialisation complète du système:

```bash
# 1. Arrêter tous les services
docker-compose down

# 2. Supprimer les volumes (ATTENTION: supprime TOUTES les données!)
docker-compose down -v

# 3. Relancer les services
docker-compose up -d

# 4. Attendre que PostgreSQL soit prêt (environ 5-10 secondes)
sleep 10

# 5. Appliquer les migrations
cd backend
alembic upgrade head

# 6. Seeder la base
python seed_database.py

# 7. Tester
curl http://localhost:8000/docs
```

---

## 📞 Support

En cas de problème:
1. Vérifiez les logs: `docker-compose logs backend`
2. Vérifiez PostgreSQL: `docker-compose logs postgres`
3. Consultez la documentation Alembic pour les migrations
4. Vérifiez les variables d'environnement dans `.env`
