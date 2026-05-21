# Digital Footprint Tracker

A complete Flask DBMS project that tracks digital exposure, privacy risk, consent history, alerts, deletion requests, analytics, audit logs, and admin review workflows.

## Tech stack

- Frontend: HTML, CSS, JavaScript, Chart.js
- Backend: Python Flask
- Database: SQLite for easy local demo, PostgreSQL-ready for production
- Security: bcrypt password hashing, JWT APIs, role-based access, session protection, validation, audit logs
- DBMS deliverables: Prisma schema, SQL migration, relationships, indexes, cascade deletion

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m server.seed
python app.py
```

Open `http://localhost:5000`.

Demo accounts:

- User: `spoorthi123@gmail.com` / `Password1`
- Admin: `admin@privacy.local` / `Admin@12345`

## Folder structure

```text
client/
  static/css/styles.css
  static/js/app.js
  templates/
server/
  routes/
  middleware/
  services/
  utils/
  models.py
prisma/
  schema.prisma
  migrations/001_init.sql
docs/
  API.md
  DEPLOYMENT.md
```

The `components`, `hooks`, and `lib` folders are included for future React-style expansion, while this implementation follows the requested HTML/CSS frontend.

## Main features

- Register, login, logout, forgot password simulation
- bcrypt password hashing
- JWT login endpoint for REST API access
- User dashboard with risk, footprint, consent, alert, deletion, and analytics cards
- Digital footprint tracker for platforms, apps, phone-related data, permissions, retention, breaches, and public profiles
- Risk scoring engine with Low, Medium, and High levels
- Consent grant/revoke workflow
- Deletion request tracking
- Alert center with notification and email simulation records
- Analytics dashboard with trend, consent, and platform charts
- Admin dashboard for users, risks, deletion requests, and audit logs
- PostgreSQL schema with foreign keys, indexes, timestamps, and cascade deletion
- Docker support

## ER diagram explanation

`User` is the central entity. Each user has one `Profile`, many `SocialAccount` rows, many `ConnectedPlatform` rows, many `Consent` rows, many `RiskAssessment` snapshots, many `Alert` rows, many `DeletionRequest` rows, many `Notification` rows, and many monthly `Analytics` rows. `AuditLog` references a user with `ON DELETE SET NULL` so security history remains even if the user is deleted. `Admin` is a one-to-one extension of `User` for admin privileges.

Relationship summary:

- `User 1--1 Profile`
- `User 1--N SocialAccount`
- `User 1--N ConnectedPlatform`
- `User 1--N Consent`
- `User 1--N RiskAssessment`
- `User 1--N Alert`
- `User 1--N DeletionRequest`
- `User 1--N Notification`
- `User 1--N Analytics`
- `User 1--0..1 Admin`
- `User 1--N AuditLog`, with logs preserved by setting `user_id` to null on delete

## Risk scoring rules

The risk engine adds points for public profiles, too many connected apps, weak privacy settings, sensitive data storage, breach flags, retention longer than 24 months, and expired granted consents. Scores are capped at 100.

- Low: `0-34`
- Medium: `35-69`
- High: `70-100`

## API docs

See [docs/API.md](docs/API.md).

## Docker

```bash
docker compose up --build
```

Then seed the database inside the web container if needed:

```bash
docker compose exec web python -m server.seed
```
