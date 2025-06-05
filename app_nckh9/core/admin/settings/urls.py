from django.urls import path
from . import views

app_name = 'admin_settings'

urlpatterns = [
    # Settings management
    path('', views.setting_list, name='list'),
    path('create/', views.setting_create, name='create'),
    path('<int:setting_id>/', views.setting_detail, name='detail'),
    path('<int:setting_id>/edit/', views.setting_edit, name='edit'),
    path(
        '<int:setting_id>/history/',
        views.setting_history,
        name='history'
    ),
]