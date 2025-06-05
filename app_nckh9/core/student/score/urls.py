from django.urls import path
from . import views

app_name = 'student_score'

urlpatterns = [
    path('rating/', views.score_rating, name='rating'),
    path('view/', views.view_score, name='view'),
    path('history/', views.score_history, name='history'),
    path('detail/<int:score_id>/', views.score_detail, name='detail'),
]