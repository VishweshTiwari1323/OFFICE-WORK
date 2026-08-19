"""
WSGI config for pm_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pm_system.settings')

application = get_wsgi_application()

# Ensure /tmp directory exists for Vercel SQLite database
if os.environ.get('VERCEL'):
    import tempfile
    tmp_dir = tempfile.gettempdir()
    os.makedirs(tmp_dir, exist_ok=True)

# Run migrations and seed data on startup
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False, verbosity=1)
    print("Migrations completed successfully")
    import seed_data
    seed_data.seed()
    print("Seed data loaded successfully")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Startup error: {type(e).__name__}: {e}")
