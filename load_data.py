import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cpms_project.settings")
django.setup()

from django.core.management import call_command

call_command('loaddata', 'data.json')
print("✅ Data loaded successfully.")
