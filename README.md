# Backend CSI Sakaraha

Backend FastAPI + SQLAlchemy 2.x pour PostgreSQL. Le frontend Next.js est hors de ce dépôt. Aucun Docker ni PHP n’est requis.

## Installation locale

Python 3.9+ et PostgreSQL 17+ sont nécessaires.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Adapter `DATABASE_URL`, `SECRET_KEY` et les paramètres SMTP dans `.env`. Le service SMTP est nécessaire pour envoyer réellement les liens de réinitialisation ; sans lui, l’API garde une réponse non-divulgatrice mais aucun e-mail ne part.

Créer une base de développement PostgreSQL si nécessaire :

```sql
CREATE ROLE csi_user LOGIN PASSWORD 'csi_password';
CREATE DATABASE csi_sakaraha OWNER csi_user;
```

Puis appliquer les migrations :

```powershell
alembic upgrade head
alembic check
```

Lancer l’API :

```powershell
uvicorn app.main:app --reload
```

Documentation OpenAPI : `http://127.0.0.1:8000/docs`. Vérification rapide : `GET /health`.

## Modèle et décisions de conception

Les neuf tables finales sont `utilisateurs`, `courriers_arrivee`, `courriers_depart`, `plaintes`, `proces_verbaux`, `services_courants`, `situations_prise_arme`, `documents` et `historique_actions`. Les identifiants techniques sont des BIGINT PostgreSQL avec identité ; `matricule`, `numero_ordre`, `ref`, `reference_message` et `numero_pv` restent des références métier séparées.

`documents` est le modèle commun d’archivage. Les fichiers sont écrits sous `PRIVATE_STORAGE_PATH`, hors des routes statiques. `table_source` + `id_source` est une référence polymorphe bornée aux registres connus, sans fausse FK entre tables métier. La FK réelle est `documents.importe_par_id -> utilisateurs.id`; l’audit conserve également une FK nullable vers l’utilisateur.

La catégorie A et la catégorie B sont contrôlées séparément. Un utilisateur ordinaire n’a pas les permissions plaintes, PV, audit ou catégorie B. Les endpoints vérifient l’autorisation à chaque requête, y compris pour la consultation et le téléchargement. Les fichiers sont renommés avec un UUID, inspectés par contenu, limités en taille et les extensions exécutables sont refusées.

## Authentification et audit

- Connexion avec `email` ou `nom_utilisateur` et mot de passe.
- Les réponses ne contiennent jamais `mot_de_passe_hash`.
- Le reset par e-mail stocke seulement le hash SHA-256 du jeton, avec expiration et usage unique.
- Les connexions réussies/échouées, consultations sensibles, téléchargements, créations, modifications, suppressions et changements de rôle sont audités.
- Les mots de passe, JWT, jetons de reset et contenus complets de documents sont exclus de `details`.

Les significations de `FM`, `TO`, `INFO`, `REF`, `/2`, `/3`, `/3S` et `/4` n’ont pas été déduites : leurs libellés sont conservés dans le modèle. La nécessité de rendre `date_reception` et `date_envoi` obligatoires, ainsi que la signification opérationnelle des champs non documentés, doit être validée par les responsables du CSI Sakaraha.

## Tests

Tests unitaires et de sécurité :

```powershell
python -m pytest -q
```

Le test PostgreSQL réel est désactivé par défaut. Après `alembic upgrade head`, l’exécuter avec :

```powershell
$env:DATABASE_URL = 'postgresql+asyncpg://csi_user:csi_password@localhost:5432/csi_sakaraha'
$env:RUN_POSTGRES_TESTS = '1'
python -m pytest -q app/tests/test_postgres_smoke.py
```

Ce smoke test crée uniquement deux comptes préfixés `smoke-`, vérifie connexion, refus d’accès aux plaintes pour le rôle ordinaire et validation d’une catégorie invalide, puis nettoie ses données.

Les tests exécutés dans cet environnement doivent être interprétés avec leur sortie réelle ; la présence du code ou de la migration seule ne constitue pas une déclaration de sécurité complète.
