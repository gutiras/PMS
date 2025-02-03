# decorators.py (or within your views.py)
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Project
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """
    Decorator to restrict view access based on roles. 
    You can pass a list of roles to allow.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Check if user has any of the allowed roles or is staff
            if not any(role in allowed_roles for role in [request.user.role, 'staff']):
                messages.error(request, 'You do not have the necessary permissions')
                
                # Get the "next" parameter from the request (i.e., the URL the user tried to access)
                next_page = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))

                # If there's no "next" parameter, fallback to the referer or default to '/'
                return redirect(next_page)
            
            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator
def project_leader_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)

        # Check if the user is the leader of the project’s assigned team
        if project.assigned_team.leader == request.user:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have the necessary permissions to perform this action.')

            # Get the "next" parameter from the request (i.e., the URL the user tried to access)
            next_page = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))

            # If no "next" parameter is available, fallback to the referer or default to '/'
            return redirect(next_page)
    
    return _wrapped_view

def team_member_required(view_func):
    def wrapper(request, project_id, task_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id)
        team = project.assigned_team

        if not team or not team.members.filter(id=request.user.id).exists():
            messages.error(request,"You do not have access to this task.")
        
        return view_func(request, project_id, task_id, *args, **kwargs)
    return wrapper