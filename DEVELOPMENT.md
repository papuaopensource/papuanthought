# Development Guide

## Prerequisites

- Python 3.13
- [uv](https://docs.astral.sh/uv/) as package manager
- Node.js (required by django-tailwind for CSS compilation)

## Local Setup

Clone the repository and navigate into the project directory.

```bash
git clone <repository-url>
cd papuan-thought-project
```

Install Python dependencies using uv.

```bash
uv sync
```

Copy the environment configuration file.

```bash
cp .env.example .env
```

Adjust `.env` as needed. For local development, the default values are sufficient.

Make sure the following variables are present in `.env`:

```
DJANGO_SETTINGS_MODULE=django_project.settings.development
SECRET_KEY=your-local-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Run database migrations.

```bash
uv run python manage.py migrate
```

Create a superuser account to access the admin panel.

```bash
uv run python manage.py createsuperuser
```

Optionally, seed the database with sample data.

```bash
uv run python manage.py seed_data
```

To reset and reseed from scratch, use the `--flush` flag.

```bash
uv run python manage.py seed_data --flush
```

## Running the Server

The project requires two processes running simultaneously: the Django server and the TailwindCSS compiler.

First terminal — Django server:

```bash
uv run python manage.py runserver
```

Second terminal — Tailwind:

```bash
uv run python manage.py tailwind start
```

The application is available at `http://127.0.0.1:8000`.

The admin panel is available at `http://127.0.0.1:8000/site-manager/`.

## Project Structure

```
accounts/        users, profiles, authentication
posts/           articles, notes, tags, image uploads, public sharing
interactions/    comments, reactions, follow, bookmarks, notifications
commons/         static pages (about, guidelines, privacy, etc.)
templates/       main layout and partials (navbar, footer)
theme/           TailwindCSS configuration
django_project/  settings, urls, wsgi
```

Each app has a `services.py` containing business logic. Views only call functions from services and contain no direct logic.

All views are written as Class-Based Views (CBVs).

## Migrations

After changing a model, create and apply migrations.

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

## System Check

```bash
uv run python manage.py check
```
