"""WSGI config for EV Service project."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ev_service.settings')
application = get_wsgi_application()
