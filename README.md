# EV Service (Django)

This is a simple, beginner-friendly Django project scaffold for an EV service web application.

Overview:
- Built with Django and SQLite (default, no extra database setup required).
- Simple apps: vehicles, services, bookings.
- Templates are plain HTML with comments to explain what's happening.

Quick start (PowerShell):

1) Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install requirements
```powershell
pip install -r requirements.txt
```

3) Apply migrations and run server
```powershell
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

Files of interest:
- `ev_service/` - Django project settings and URLs
- `vehicles/` - vehicle models and simple views
- `services/` - service types (e.g. charging)
- `templates/` - HTML templates

Next steps:
- Add authentication for users
- Add forms for creating bookings from the UI
- Add tests and deployment steps

If you provided a PDF synopsis in this folder, it will be used to flesh out the domain models and requirements. If you want, tell me any specific details to include from the PDF and I will update models and pages accordingly.
