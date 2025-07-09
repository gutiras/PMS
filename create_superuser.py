import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cpms_project.settings")  # Change this to your settings module
django.setup()

User = get_user_model()

username = os.getenv("DJANGO_SU_NAME")
email = os.getenv("DJANGO_SU_EMAIL")
password = os.getenv("DJANGO_SU_PASS")

if username and email and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"✅ Superuser '{username}' created.")
    else:
        print(f"⚠️ Superuser '{username}' already exists.")
else:
    print("❌ Missing environment variables for superuser creation.")
