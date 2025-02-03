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

        post_migrate.connect(self.create_roles, sender=self)

    def create_roles(self, sender, **kwargs):
        from django.contrib.auth.models import Group, Permission  # Import inside this method
        
        print("Creating roles...")  # Debugging message
        groups_permissions = {
            "Super Admin": Permission.objects.all(),  # Full access
            "Admin": [
                "add_project", "change_project", "delete_project",
                "add_task", "change_task", "delete_task",
            ],
            "Staff": [
                "add_task", "change_task", "view_project",
            ],
            "Viewer": ["view_project", "view_task"],
        }

        for group_name, permissions_list in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)

            if created or group.permissions.count() == 0:
                group.permissions.clear()

                if permissions_list == Permission.objects.all():
                    group.permissions.add(*permissions_list)
                else:
                    for codename in permissions_list:
                        try:
                            permission = Permission.objects.get(codename=codename)
                            group.permissions.add(permission)
                        except Permission.DoesNotExist:
                            print(f"Permission '{codename}' does not exist.")
        
        print("Roles and permissions creation finished.")
