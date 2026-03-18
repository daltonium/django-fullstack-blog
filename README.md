# Inkwell - Django Blog Platform

## Project Structure
```
blog_platform/
├── blog_platform/       # Project config
├── blog/                # Blog app (posts, categories, tags, comments)
├── users/               # Auth app
├── templates/           # All HTML templates
│   ├── base.html
│   ├── blog/
│   └── users/
├── static/css/main.css  # All styles
└── manage.py
```

## Setup
```bash
python -m venv venv && source venv/bin/activate
pip install django psycopg2-binary pillow
createdb blog_db
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Learning Map
| Concept | Where Used |
|---------|-----------|
| SlugField + auto-generation | Post/Category/Tag .save() |
| ForeignKey | Post->Category, Comment->Post, Comment->User |
| ManyToManyField | Post <-> Tags |
| Pagination | paginate() helper in views.py |
| Template Inheritance | base.html extended by all templates |
| select_related / prefetch_related | All list views |
| F() expressions | Post.increment_view() |
| Q() objects | search_posts() single query |

## Key Backend Patterns
- select_related on every FK queryset (zero N+1)
- prefetch_related for M2M and reverse FK
- F() expression for atomic view counter
- Q() with .distinct() for full-text search
- UUID suffix for guaranteed slug uniqueness
- DB indexes on slug, (status, published_at), author
