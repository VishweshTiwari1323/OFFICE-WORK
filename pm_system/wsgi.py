"""
WSGI config for pm_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pm_system.settings')

application = get_wsgi_application()

# Run migrations and seed data on startup
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    
    import seed_data
    seed_data.seed()
except Exception as e:
    print(f"Startup error: {e}")
