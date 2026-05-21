# Deployment Guide

## Local development

1. Create `.env` from `.env.example`.
2. Install Python dependencies.
3. Seed the database.
4. Run Flask.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m server.seed
python app.py
```

## Docker

```bash
docker compose up --build
```

The app will run on `http://localhost:5000` and PostgreSQL on port `5432`.

## Production checklist

- Replace `SECRET_KEY` and `JWT_SECRET_KEY`.
- Use PostgreSQL with backups enabled.
- Serve behind HTTPS.
- Set secure cookie flags when using HTTPS.
- Configure real email delivery for password reset and notifications.
- Restrict admin account creation.
