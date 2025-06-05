from django.urls import path
from . import views

app_name = 'teacher_reports'

urlpatterns = [
    # Report management
    path('', views.report_list, name='list'),
    path('create/', views.report_create, name='create'),
    path('<int:report_id>/', views.report_detail, name='detail'),
    path('<int:report_id>/edit/', views.report_edit, name='edit'),
]