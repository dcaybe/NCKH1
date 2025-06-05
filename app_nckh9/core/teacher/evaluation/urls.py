from django.urls import path
from . import views

app_name = 'teacher_evaluation'

urlpatterns = [
    # Evaluation views
    path('', views.evaluation_list, name='list'),
    path('<int:evaluation_id>/', views.evaluation_detail, name='detail'),
    path('create/<int:score_id>/', views.evaluation_create, name='create'),
    path('<int:evaluation_id>/edit/', views.evaluation_edit, name='edit'),
]