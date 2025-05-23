## 🔥 What's Changed

This version of **FilmPoint** is a complete upgrade over the original:

- **Switched from Django to Flask** — Lightweight, API-first architecture for faster backend responses and easier scaling.
- **Frontend rebuilt with Vue.js** — Decoupled single-page app for better UI performance and modularity.
- **External APIs integrated** — Improved movie recommendations via third-party data sources.
- **Dockerized everything** — Zero local setup needed. Just clone, `.env`, and `docker-compose up`.
- **Environment variables support** — Configurable secrets and DB options through `.env`.
- **Cleaner codebase** — Frontend and backend are separated, making it easier to maintain or extend.


## 🐳 Docker Setup (Recommended)

### 1. Clone the repository

```bash
git clone https://github.com/your_username/filmpoint.git
cd filmpoint
```

### 2. Create your `.env` file

```env
# .env
SECRET_KEY=your_secret_key
DEBUG=True
DB_ENGINE=django.db.backends.mysql  # or postgresql
DB_NAME=filmpoint
DB_USER=filmpoint_user
DB_PASSWORD=filmpoint_pass
DB_HOST=db
DB_PORT=3306  # use 5432 for PostgreSQL
```

### 3. Build and start all services

```bash
docker-compose up --build
```

### 4. (Optional) Apply migrations and create superuser (for Django backend)

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py loaddata fixtures.json
```
