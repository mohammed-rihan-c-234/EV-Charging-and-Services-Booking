# EV Charging Booking and Services (Django)

Full-stack EV service platform built with Django. Modules include charging bookings, service bookings, spare parts orders, rewards, SOS, and maps.

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

3) Create `.env` (if needed)
Create a `.env` file in the project root for any secrets or API keys your settings read. A common starting point:
```env
DJANGO_SECRET_KEY=replace-me
DEBUG=1
```

4) Apply migrations and run server
```powershell
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

Create an admin user (optional):
```powershell
python manage.py createsuperuser
```

Files of interest:
- `ev_service/` - Django project settings and URLs
- `charging/` - charging stations and bookings
- `bookings/` - service booking flow
- `spareparts/` - parts catalog and orders
- `rewards/` - reward points and coupons
- `templates/` - HTML templates
