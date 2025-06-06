from django.urls import path
from . import views

app_name = 'student_appeals'

urlpatterns = [
    path('', views.appeal_list, name='list'),
    path('create/', views.appeal_create, name='create'),
    path('<int:appeal_id>/', views.appeal_detail, name='detail'),
    path('<int:appeal_id>/update/', views.appeal_update, name='update'),
    path('<int:appeal_id>/cancel/', views.appeal_cancel, name='cancel'),
]