from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
   

    path("reports/", views.report_dashboard, name="report_dashboard"),
    path("generate_filtered_excel/", views.generate_filtered_excel, name="generate_filtered_excel"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("user_dashboard/", views.user_dashboard, name="user_dashboard"),
    path('activities/', views.admin_activity_view, name='admin_activities'),




    
    path("", views.landing_page, name="home"),
    path("admin_landing_page/", views.admin_landing_page, name="admin_landing_page"),
    path("other_landing_page/", views.other_landing_page, name="other_landing_page"),
    path('gantt/<int:project_id>/', views.gantt_chart, name='gantt_chart'),


    path("projects/", views.project_list, name="project_list"),
    path('project/<int:project_id>/', views.project_details, name='project_details'),
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/<int:project_id>/edit/", views.project_edit, name="project_edit"),
    path("projects/<int:project_id>/delete/", views.project_delete, name="project_delete"),
    path("projects/<int:project_id>/tasks/", views.task_list, name="task_list"),
    path("projects/<int:project_id>/tasks/create/", views.task_create, name="task_create"),
    path("projects/<int:project_id>/tasks/<int:task_id>/edit/", views.task_edit, name="task_edit"),
    path("projects/<int:project_id>/tasks/<int:task_id>/delete/", views.task_delete, name="task_delete"),
    path('projects/<int:project_id>/cancel-deletion/', views.cancel_project_deletion, name='cancel_project_deletion'),


    path('projects/<int:project_id>/file-manager/', views.file_manager, name='file_manager'),
  
    path('file-manager/<int:project_id>/', views.file_manager, name='file_manager'),


    path("task/<int:project_id>/tasks/<int:task_id>/updates/", views.task_updates, name="task_updates"),
    path('task/<int:task_id>/update_status/', views.task_status_update, name='task_status_update'),



    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/delete/', views.delete_user, name='user_delete'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/toggle_user_status/', views.toggle_user_status, name='toggle_user_status'),
 
    # List all teams
    path('teams/', views.team_list, name='team_list'),
    path('teams/create/', views.team_create, name='team_create'),
    path('teams/<int:team_id>/add-member/', views.add_team_member, name='add_team_member'),
    path('teams/<int:team_id>/edit/', views.edit_team, name='team_edit'),
    path('teams/delete/', views.delete_team, name='team_delete'),
    path('teams/<int:team_id>/remove-member/<int:member_id>/', views.remove_team_member, name='remove_team_member'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('replace-leader/<int:team_id>/', views.replace_team_leader, name='replace_team_leader'),


    path('password_reset/', views.password_reset, name='password_reset'),
    path('password-reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name='password_reset_confirm'),
         
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),


    #chat

  
    path('chat/room/<int:room_id>/', views.chat_room_detail, name='chat_room_detail'),
    path('chatroom', views.chatroom, name='chatroom'),
    path('chat/room/<int:room_id>/send/', views.send_message, name='send_message'),
    #path('chat/message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),

    path('chat/<int:room_id>/edit_message/<int:message_id>/', views.edit_message, name='edit_message'),



    #notifications
    path('notifications/', views.notifications_view, name='notifications_view'),
    #path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),

]
