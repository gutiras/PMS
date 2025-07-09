from django.core.management import call_command
from django.db.models.signals import post_save
from cpms_app.models import User
from cpms_app.signals import create_user_profile

# Disconnect the signal temporarily
post_save.disconnect(create_user_profile, sender=User)

# Load the fixture
call_command('loaddata', 'data.json')

# Reconnect the signal
post_save.connect(create_user_profile, sender=User)
