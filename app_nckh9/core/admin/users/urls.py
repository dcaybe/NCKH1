from django.urls import path
from . import views

app_name = 'admin_users'

urlpatterns = [
    # User management
    path('', views.user_list, name='list'),
    path('create/', views.user_create, name='create'),
    path('<int:user_id>/', views.user_detail, name='detail'),
    path('<int:user_id>/edit/', views.user_edit, name='edit'),
    
    # User permissions
    path(
        '<int:user_id>/permissions/',
        views.user_permissions,
        name='permissions'
    ),
    
    # User activity
    path(
        '<int:user_id>/activity/',
        views.user_activity,
        name='activity'
    ),
]