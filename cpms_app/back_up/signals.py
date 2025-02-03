from django.db.models.signals import post_save, post_delete, m2m_changed ,pre_save ,pre_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Profile, Team, Notification, Task, User, Project, ChatRoom, ActivityLog
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.utils import timezone
from django.shortcuts import  get_object_or_404


@receiver(m2m_changed, sender=Team.members.through)
def notify_user_removed_from_team(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_remove':  # Only act after removal has been completed
        for user_id in pk_set:
            try:
                user = User.objects.get(id=user_id)  # Get the removed user
                print(f"User removed: {user.username}")  # Log the removed user

                # Create and save the notification for the removed user
                notification = Notification.objects.create(
                    recipient=user,
                    message=f"You have been removed from the team: {instance.name}.",
                    timestamp=timezone.now()
                )
                print(f"Notification created for {user.username} - {notification.message}")

            except User.DoesNotExist:
                print(f"User with ID {user_id} does not exist")
            except Exception as e:
                print(f"Error creating notification: {e}")

# Automatically create a Profile when a User is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Automatically save the Profile when the User is updated
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=Team)
def send_team_creation_notification(sender, instance, created, **kwargs):
    """
    This signal will send notifications when a new team is created.
    """
    if created:
        # Get the leader of the team
        leader = instance.leader
        
        # Create a notification for the leader
        Notification.objects.create(
            recipient=leader,
            message=f"You have been assigned as the leader of the team: {instance.name}.",
            timestamp=timezone.now(),
        )

        # Create notifications for all team members, including the leader
        for member in instance.members.all():
            Notification.objects.create(
                recipient=member,
                message=f"You have been added to the team: {instance.name}.",
                timestamp=instance.timestamp,
            )

@receiver(pre_delete, sender=Team)
def send_team_deletion_notification(sender, instance, **kwargs):
    """
    This signal will send notifications when a team is deleted.
    """
    # Get the name of the deleted team for the notification
    team_name = instance.name
    
    # Create notifications for all team members that the team has been deleted
    for member in instance.members.all():
        Notification.objects.create(
            recipient=member,
            message=f"The team {team_name} has been deleted.",
            timestamp=timezone.now(),
        )
@receiver(m2m_changed, sender=Task.assigned_to.through)
def notify_task_assignment(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        # Ensure User objects are fully initialized
        from django.db import transaction
        with transaction.atomic():
            for user_id in pk_set:
                user = User.objects.get(pk=user_id)
                Notification.objects.create(
                    recipient=user,
                    message=f"You have been assigned a new task: {instance.name}."
                )

@receiver(pre_delete, sender=Task)
def notify_users_task_deleted(sender, instance, **kwargs):
    # Get the users assigned to the task before deletion
    assigned_users = instance.assigned_to.all()

    if not assigned_users:
        print(f"No users were assigned to task '{instance.name}'.")
        return
    
    # Create a notification for each assigned user
    for user in assigned_users:
        Notification.objects.create(
            recipient=user,
            message=f"The task '{instance.name}' you were assigned to has been deleted."
        )
        print(f"Notification sent to {user.username}: 'The task {instance.name} was deleted.'")

@receiver(pre_save, sender=Project)
def revoke_tasks_on_team_change(sender, instance, **kwargs):
    if instance.pk:  # Ensures we're updating an existing project
        previous_project = Project.objects.get(pk=instance.pk)

        # Check if there was a previously assigned team
        if previous_project.assigned_team and previous_project.assigned_team != instance.assigned_team:
            # Get tasks assigned to members of the previous team
            tasks_to_revoke = Task.objects.filter(
                project=instance,
                assigned_to__in=previous_project.assigned_team.members.all()
            )

            # Revoke tasks from the previous team's members
            for task in tasks_to_revoke:
                task.assigned_to.clear()  # Removes all assigned users from the task
                task.is_active = False    # Optionally, deactivate the task
                task.save()


@receiver(post_save, sender=Project)
def create_chat_room(sender, instance, created, **kwargs):
    if created:  # Trigger only when a new project is created
        # Replace spaces in the project name with underscores
        sanitized_name = instance.name.replace(" ", "_")
        ChatRoom.objects.create(
            name=sanitized_name,
            project=instance
        )
@receiver(post_save, sender=Task)
def update_project_status(sender, instance, **kwargs):
    """Update the status of a project when a task changes."""
    project = instance.project
    project.save()  # This will call the custom save method in the Project model

