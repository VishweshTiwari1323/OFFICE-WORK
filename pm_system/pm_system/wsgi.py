import os
import sys
from pathlib import Path

# Add outer and inner pm_system directories to Python system path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pm_system.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application