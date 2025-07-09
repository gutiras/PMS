import os
import django

# Tell Django where to find settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cpms_project.settings")  # <-- change this!

# Setup Django
django.setup()

from django.core.management import call_command
from django.db.models.signals import post_save
from cpms_app.models import User
from cpms_app.signals import create_user_profile

# Temporarily disconnect the signal to avoid duplicate Profile creation
post_save.disconnect(create_user_profile, sender=User)

# Load your fixture
call_command('loaddata', 'data.json')

# Reconnect the signal afterward
post_save.connect(create_user_profile, sender=User)
