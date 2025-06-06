from django.urls import path
from . import views

app_name = 'teacher_classes'

urlpatterns = [
    # Class management
    path('', views.class_list, name='list'),
    path('<str:class_id>/', views.class_detail, name='detail'),
    path('<str:class_id>/edit/', views.class_edit, name='edit'),
    
    # Activity management
    path('<str:class_id>/activities/', views.activity_list, name='activity_list'),
    path('<str:class_id>/activities/create/', views.activity_create, name='activity_create'),
    path(
        '<str:class_id>/activities/<int:activity_id>/',
        views.activity_detail,
        name='activity_detail'
    ),
]