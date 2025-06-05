from django.urls import path, include
from . import views

app_name = 'admin'

urlpatterns = [
    # Admin dashboard
    path('', views.admin_dashboard, name='dashboard'),
    
    # User management
    path('users/', include('core.admin.users.urls', namespace='users')),
    
    # System settings
    path('settings/', include('core.admin.settings.urls', namespace='settings')),
]