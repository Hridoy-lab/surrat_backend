# celery.py
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system_integration.settings')

# Create celery app
app = Celery('system_integration')

# Configure using settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Optional: Configure broker connection retry
app.conf.broker_connection_retry_on_startup = True