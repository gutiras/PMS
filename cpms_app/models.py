from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission  # For assigning milestones to users or teams
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings  # To reference the custom User model
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from django.core.validators import FileExtensionValidator
import json


from datetime import timedelta


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True)
    location = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        User is created inactive by default.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.is_active = False  # Mark user inactive initially
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        Superuser will always be active by default.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  # Superuser should be active by default

        return self.create_user(username, email, password, **extra_fields)
# Custom User Model

class User(AbstractUser):
    
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('viewer', 'Viewer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    # Custom User Manager
    objects = UserManager()
    class Meta:
        permissions = [
            ("user_can_upload_file", "Can upload file"),
            ("user_can_create_folder", "Can create folder"),
            ("user_can_delete_file", "Can delete file"),
            ("user_can_rename_file", "Can rename file"),
            # Add other custom permissions as needed
        ]
    def save(self, *args, **kwargs):
        if not self.pk:  # Only run this check on user creation
            self.is_active = True  # Keep the user inactive initially
        super().save(*args, **kwargs)
        self.check_inactivity_and_deactivate()  # This will run the check for inactivity after save

    def check_inactivity_and_deactivate(self):
        """ Deactivate user if no login in 30 days """
        if self.last_login and self.last_login < timezone.now() - timedelta(days=30):
            self.is_active = False
            self.save()

    def __str__(self):
        return self.username

# Optional: You can add signals for automatic profile creation or other custom behavior

class Team(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    leader = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='led_teams'
    )
    members = models.ManyToManyField(User, related_name='teams')
    
    def save(self, *args, **kwargs):
        if self.pk:  # Existing object
            self.old_name = Team.objects.get(pk=self.pk).name
        self.clean()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name


class Project(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    can_be_extended = models.BooleanField(default=False)
    assigned_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    progress = models.FloatField(default=0.0)  # Progress percentage (0 to 100)
    status = models.CharField(
        max_length=50,
        choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')],
        default='pending'
    )
    deletion_requested_by = models.ForeignKey(
        User, 
        related_name='deletion_requested_projects', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    deletion_confirmed = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
 
    def calculate_progress(self):
        """Calculate project progress as the average progress of all its milestones."""
        milestones = self.milestones.all()
        total_milestones = milestones.count()

        if total_milestones == 0:
            return 0  # Avoid division by zero if no milestones exist

        total_progress = sum(milestone.progress for milestone in milestones)  # Sum milestone progress
        return round(total_progress / total_milestones, 2)    # Average progress

    def project_length(self):
        """Calculate total length of the project in days."""
        return (self.end_date - self.start_date).days + 1

    def days_left(self):
        """Calculate remaining days until the project end date."""
        today = date.today()
        remaining_days = (self.end_date - today).days
        return  remaining_days # Prevent negative values if project has ended

    def __str__(self):
        return self.name

    def update_status_based_on_milestones(self):
        """Update project status based on the milestone completion."""
        completed_milestones = self.milestones.filter(status='completed')
        total_milestones = self.milestones.count()
        in_progress_steps = self.milestones.filter(status='in_progress')

        # Set status based on milestone completion
        if completed_milestones.count() == total_milestones and total_milestones != 0:
            self.status = 'completed'
        elif in_progress_steps.count() > 0:
            self.status = 'in_progress'
        else:
            self.status = 'pending'
    def save(self, *args, **kwargs):
        # Check if it's a new object
        is_new = not self.pk

        super().save(*args, **kwargs)  # Save the object (new or existing)

        if not is_new:
            self.update_status_based_on_milestones()  # Update status only for existing objects
            super().save(*args, **kwargs)  # Save again with the updated status
    def to_json(self):
        """Serialize project attributes to JSON format."""
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date),
            "can_be_extended": self.can_be_extended,
            "assigned_team_name": self.assigned_team.name if self.assigned_team else None,
            "assigned_team_id":self.assigned_team.id if self.assigned_team else None,
            "progress": self.progress,
            "status": self.status,
            "deletion_requested_by": self.deletion_requested_by.id if self.deletion_requested_by else None,
            "deletion_confirmed": self.deletion_confirmed,
            "description": self.description,
        }, default=str)  # Use default=str to handle date serialization

    def __str__(self):
        return self.name

class Milestone(models.Model):
        STATUS_CHOICES = [
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
        ]
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        name = models.CharField(max_length=255)
        start_date = models.DateField()
        end_date = models.DateField()
        can_be_extended = models.BooleanField(default=False)
        assigned_to = models.ManyToManyField(User, related_name="milestones", blank=True)  # Multiple users can be assigned
        project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name="milestones")
        status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
        assigned_group = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name="milestones")
        description = models.TextField(null=True, blank=True)
        actual_end_date = models.DateField(null=True, blank=True)  # Add this field
        effort_estimation = models.IntegerField(null=True, blank=True)  # Estimated hours to complete
        actual_effort = models.IntegerField(null=True, blank=True)  # Actual hours spent   
        def __str__(self):
            return self.name 
        @property
        def progress(self):
            """Calculate milestone progress as the average progress of all its tasks."""
            tasks = self.tasks.all()
            total_tasks = tasks.count()

            if total_tasks == 0:
                return 0  # Avoid division by zero if no tasks exist

            total_progress = sum(task.progress for task in tasks)  # Sum all task progress values
            return round(total_progress / total_tasks, 2)  # Calculate average progress
        @property
        def effort_difference(self):
            """ Calculate difference between estimated and actual effort """
            if self.effort_estimation is not None and self.actual_effort is not None:
                return self.effort_estimation - self.actual_effort
            return None
        def assign_milestone_to_group(self):
            """ Assign the milestone to all members of the group """
            if self.assigned_group:
                self.assigned_to.set(self.assigned_group.members.all())  # Assign milestone to all members of the team
                self.save()
        @property
        def delayed_days(self):
            if self.status == "completed" and self.actual_end_date:
                return (self.actual_end_date - self.end_date).days
            elif self.end_date > date.today():
                return (self.end_date - date.today()).days
            return 0
        def update_status_based_on_tasks(self):
            completed_tasks = self.tasks.filter(status='completed')
            total_tasks = self.tasks.count()
            in_progress_steps = self.tasks.filter(status='in_progress')

            # Set status based on milestone completion
            if completed_tasks.count() == total_tasks and total_tasks != 0:
                self.status = 'completed'
            elif in_progress_steps.count() > 0:
                self.status = 'in_progress'
            else:
                self.status = 'pending'
        def save(self, *args, **kwargs):
            is_new = not self.pk
            super().save(*args, **kwargs)
            if not is_new:
                self.update_status_based_on_tasks()  # Update status only for existing objects
                super().save(*args, **kwargs)  # Save again with the updated status

        def __str__(self):
            return self.name

        def to_json(self):
            """Serialize milestone attributes to JSON format."""
            return json.dumps({
                "id": self.id,
                "name": self.name,
                "start_date": str(self.start_date),
                "end_date": str(self.end_date),
                "can_be_extended": self.can_be_extended,
                "assigned_to": [user.id for user in self.assigned_to.all()],
                "project": self.project.id,
                "status": self.status,
                "assigned_group": self.assigned_group.id if self.assigned_group else None,
                "description": self.description,
                "actual_end_date": str(self.actual_end_date) if self.actual_end_date else None,
                "effort_estimation": self.effort_estimation,
                "actual_effort": self.actual_effort,
                "effort_difference": self.effort_difference,
                "delayed_days": self.delayed_days,
            }, default=str)  # Use default=str to handle date serialization


class Task(models.Model):
    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ManyToManyField(User, related_name="tasks", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started")
    milestone = models.ForeignKey("Milestone", on_delete=models.CASCADE, related_name="tasks")
    start_date = models.DateField()
    end_date = models.DateField()
    def __str__(self):
        return self.name

    def to_json(self):
        """Serialize task attributes to JSON format."""
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "milestone_id": self.milestone.id,
            "assigned_to": [user.username for user in self.assigned_to.all()],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        })

    @property
    def is_delayed(self):
        """Check if the task is delayed based on the milestone's end date."""
        if self.status != "completed" and self.milestone.end_date < date.today():
            return True
        return False

    @property
    def remaining_days(self):
        """Calculate the remaining days to complete the task."""
        if self.status != "completed":
            return (self.milestone.end_date - date.today()).days
        return 0
    
    @property
    def progress(self):
        """Calculate task progress based on completed steps."""
        total_steps = self.steps.count()
        completed_steps = self.steps.filter(status="completed").count()
        
        if total_steps == 0:
            return 0  # Avoid division by zero if there are no steps

        return (completed_steps / total_steps) * 100  # Return progress percentage
    def update_status_based_on_steps(self):
        completed_steps = self.steps.filter(status='completed')
        in_progress_steps = self.steps.filter(status='in_progress')
        total_steps = self.steps.count()
        
        # Set status based on milestone completion
        if completed_steps.count() == total_steps and total_steps != 0:
            self.status = 'completed'
        elif in_progress_steps.count() > 0:
            self.status = 'in_progress'
        else:
            self.status = 'not_started'
    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if not is_new:
            self.update_status_based_on_steps()  # Update status only for existing objects
            super().save(*args, **kwargs)  # Save again with the updated status

    def __str__(self):
        return self.name
    
class TaskStep(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="steps")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(help_text="The step order for execution.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)



class TaskIssue(models.Model):
    step = models.ForeignKey(TaskStep, on_delete=models.CASCADE, related_name="issues")
    description = models.TextField(help_text="Description of the issue.")
    reported_at = models.DateTimeField(auto_now_add=True)
    reported_by =models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reported_by'
    )
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True)
    remark= models.TextField(blank=True, null=True)

    def __str__(self):
        status = "Resolved" if self.resolved else "Unresolved"
        return f"Issue in Step: {self.step.name} ({status})"



class TaskUpdate(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="updates")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="task_updates")
    date = models.DateField(default=timezone.now)  # Default to today's date
    progress_detail = models.TextField()  # What has been done
    issues = models.TextField(blank=True, null=True)  # Any blockers or issues
    created_at = models.DateTimeField(auto_now_add=True)  # When this update was created

    class Meta:
        ordering = ["-created_at"]  # Display newest updates first
        unique_together = ["task", "date", "updated_by"]  # One update per day per user per task

    def __str__(self):
        return f"Update for {self.task.name} by {self.updated_by.username} on {self.date}"


class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, null=True, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    project = models.ForeignKey(
        'Project',
        related_name='chat_rooms',
        on_delete=models.CASCADE,
        default=1  # Replace 1 with the ID of an actual project or remove it after migration
    )
    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(blank=True)  # Content is optional for file-only messages
    timestamp = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies'
    )
    mentions = models.ManyToManyField(
        User,
        blank=True,
        related_name='mentioned_in_messages'
    )
    file = models.FileField(
        upload_to='chat_files/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'jpg', 'png', 'mp4', 'zip'])]
    )

    def __str__(self):
        return f'{self.user.username}: {self.content[:50] if self.content else "File uploaded"}'


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
   
    def __str__(self):
        return f"Notification to {self.recipient} - {self.message[:50]}"
    


class ActivityLog(models.Model):
    ACTIVITY_CHOICES = [
        ('cancel_deletion_request', 'Cancel Deletion Request'),
        ('create_project', 'Create Project'),
        ('delete_project', 'Delete Project'),
        ('edit_project', 'Edit Project'),
        ('assign_team_to_project', 'Assign Team to Project'),

        ('create_user', 'Create User'),
        ('delete_user', 'Delete User'),
        ('edit_user', 'Edit User'),

        ('failed_login', 'Failed Login'),
        ('login', 'User Logged In'),

        ('message_deleted', 'Message Deleted'),
        ('message_edited', 'Message Edited'),
        ('message_sent', 'Message Sent'),

        ('task_created', 'Task Created'),
        ('task_deleted', 'Task Deleted'),
        ('task_edited', 'Task Edited'),
        ('task_status_updated', 'Task Status Updated'),
        ('assign_user_to_task', 'Assign User to Task'),

        ('team_created', 'Team Created'),
        ('team_deleted', 'Team Deleted'),
        ('team_leader_changed', 'Team Leader Changed'),
        ('team_member_added', 'Team Member Added'),
        ('team_member_removed', 'Team Member Removed'),
        ('team_updated', 'Team Updated'),

        ('update_profile', 'Update Profile'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    activity_description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    object_name = models.CharField(max_length=255, blank=True, null=True)  # The name of the object involved in the action
    object_id = models.IntegerField(blank=True, null=True)  # The ID of the object (to fetch specific object)
    deleted_object_data = models.JSONField(blank=True, null=True)  # Store all attributes of the deleted object in JSON
    updated_object_data = models.JSONField(blank=True, null=True)  # Store updated attributes of the object in JSON
    created_object_data = models.JSONField(blank=True, null=True) 
    def log_deleted_object(self, instance):
        """
        Logs attributes of a deleted object.
        :param instance: The object being deleted
        """
        self.deleted_object_data = json.loads(instance.to_json())  # Assuming the instance has a `to_json` method or serializer
        self.object_name = str(instance)
        self.object_id = instance.id
        self.activity_type = 'delete_' + instance._meta.model_name.lower()

    def log_updated_object(self, instance, updated_fields):
        """
        Logs updated attributes of an object.
        :param instance: The object being updated
        :param updated_fields: Dictionary of updated fields with old and new values
        """
        self.updated_object_data = updated_fields
        self.object_name = str(instance)
        self.object_id = instance.id
        self.activity_type = 'edit_' + instance._meta.model_name.lower()

    def __str__(self):
        return f"{self.user.username} {self.activity_type} at {self.timestamp}"