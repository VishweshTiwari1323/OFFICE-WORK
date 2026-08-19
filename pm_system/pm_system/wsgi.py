"""
WSGI config for pm_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""
import os
import sys
import traceback

# Add project directory to path for Vercel
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['PYTHONPATH'] = project_dir

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pm_system.settings')

# Ensure /tmp directory exists for Vercel SQLite database
if os.environ.get('VERCEL'):  # Note: This will cause error but let's fix below
    import tempfile
    tmp_dir = tempfile.gettempdir()
    os.makedirs(tmp_dir, exist_ok=True)

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()

    # Run migrations and import seed data
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False, verbosity=0)
        import seed_data
        print("SUCCESS: Migrations and seed data loaded", flush=True)
    except Exception as e:
        print(f"INFO: Migration/seed issue (may be expected): {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()

except Exception as e:
    print(f"CRITICAL ERROR: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
    # Re-raise to ensure Vercel logs capture the error
    raise