from .models import Notification

def unread_notifications_count(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': Notification.objects.filter(recipient=request.user, is_read=False).count()
        }
    return {
        'unread_notifications_count': 0
    }

def unread_notifications_context(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        return {
            'unread_notifications_count': unread_notifications.count(),
            'notifications': unread_notifications,  # Include the notifications themselves
        }
    return {
        'unread_notifications_count': 0,
        'notifications': []
    }

def notifications_context(request):
    if request.user.is_authenticated:
        all_notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
        unread_count = all_notifications.filter(is_read=False).count()
        return {
            'unread_notifications_count': unread_count,
            'all_notifications': all_notifications  # Includes both read and unread notifications
        }
    return {
        'unread_notifications_count': 0,
        'all_notifications': [],
    }