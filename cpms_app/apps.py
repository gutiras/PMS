from django.apps import AppConfig
from django.db.models.signals import post_migrate

class GanttAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cpms_app'

    def ready(self):
        # Register role creation after migrations
        from django.contrib.auth.models import Group, Permission  # Import here
        from django.db.models.signals import post_migrate
        
        try:
            import cpms_app.signals
        except ImportError:
            pass

       

   
