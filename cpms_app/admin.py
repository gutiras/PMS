from django.contrib import admin
from .models import Team, Milestone ,Project,Message,ChatRoom, ActivityLog, Notification, Task, TaskIssue, TaskStep
from .models import User
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

admin.site.unregister(Group)  # Unregister the default Group model if you want to customize
admin.site.register(Group, GroupAdmin)
admin.site.register(User)
admin.site.register(Message)
admin.site.register(ChatRoom)
admin.site.register(Notification)
admin.site.register(Task)
admin.site.register(TaskIssue)
admin.site.register(TaskStep)

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'get_assigned_users', 'status', 'project')
    list_filter = ('status', 'project')
    search_fields = ('name', 'description')

    def get_assigned_users(self, obj):
        """
        Custom method to display assigned users as a comma-separated list.
        """
        return ", ".join([user.username for user in obj.assigned_to.all()])

    get_assigned_users.short_description = 'Assigned Users'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'progress', 'can_be_extended')
    list_filter = ('can_be_extended',)
    search_fields = ('name',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'leader')
    filter_horizontal = ('members',)  # Add this to allow easy member selection


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'object_name', 'timestamp')
    list_filter = ('activity_type', 'user')
    search_fields = ('activity_description', 'user__username', 'object_name')
    ordering = ('-timestamp',)  # Display most recent activities first
    readonly_fields = ('user', 'activity_type', 'activity_description', 'object_name', 'object_id', 'timestamp')