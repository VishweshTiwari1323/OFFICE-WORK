from django.urls import path
from . import views

urlpatterns = [
    # Dashboards
    path('', views.dashboard_router, name='dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('team/', views.team_members_list, name='team_members_list'),

    # Tasks & HTMX Search
    path('tasks/search/', views.task_search, name='task_search'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('projects/create/', views.create_project, name='create_project'),
    path('tasks/<int:pk>/status/<str:new_status>/', views.update_task_status, name='update_task_status'),

    # Reports
    path('reports/submit/', views.submit_report, name='submit_report'),
    path('reports/', views.view_reports, name='view_reports'),

    # Profile Settings
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('change-password/done/', views.ChangePasswordDoneView.as_view(), name='change_password_done'),
    path('change-username/', views.change_username, name='change_username'),
]