from django.urls import path, include

app_name = 'student'

urlpatterns = [
    # Profile management
    path('profile/', include('core.student.profile.urls', namespace='profile')),
    
    # Score management
    path('score/', include('core.student.score.urls', namespace='score')),
    
    # Appeals management
    path('appeals/', include('core.student.appeals.urls', namespace='appeals')),
]