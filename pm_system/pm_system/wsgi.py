import os
import sys
from pathlib import Path

# Add outer and inner pm_system directories to Python system path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pm_system.settings')

# Ensure /tmp directory exists for Vercel SQLite database
if os.environ.get('VERCEL'):
    import tempfile
    tmp_dir = tempfile.gettempdir()
    os.makedirs(tmp_dir, exist_ok=True)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application

# Run migrations on startup - critical for Vercel
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False, verbosity=0)
    print("MIGRATIONS COMPLETED", flush=True)
    
    # Import seed data - this creates tables if they don't exist
    import seed_data
    print("SEED DATA LOADED", flush=True)
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"MIGRATION ERROR: {type(e).__name__}: {e}", flush=True)