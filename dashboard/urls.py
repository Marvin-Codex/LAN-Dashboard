from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('files/', views.file_manager_view, name='file_manager'),
    path('download/<str:filename>/', views.download_file_view, name='download_file'),
    path('preview/<str:filename>/', views.file_preview_view, name='file_preview'),
    path('activity-logs/', views.activity_logs_view, name='activity_logs'),
    path('phone-mouse/', views.phone_mouse_view, name='phone_mouse'),
]
