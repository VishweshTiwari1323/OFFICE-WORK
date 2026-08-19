"""
WSGI config for pm_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""
import os
import sys

# Add project directory to path for Vercel
os.environ['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pm_system.settings')

# Ensure /tmp directory exists for Vercel SQLite database
if os.environ.get('VERCEL'):
    import tempfile
    tmp_dir = tempfile.gettempdir()
    os.makedirs(tmp_dir, exist_ok=True)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Run migrations and seed data on startup
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False, verbosity=0)
    import seed_data
    seed_data.seed()
except Exception as e:
    import traceback
    traceback.print_exc()