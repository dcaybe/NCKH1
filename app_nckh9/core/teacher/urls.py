from django.urls import path, include

app_name = 'teacher'

urlpatterns = [
    # Class management
    path('classes/', include('core.teacher.classes.urls', namespace='classes')),
    
    # Evaluation management
    path('evaluation/', include('core.teacher.evaluation.urls', namespace='evaluation')),
    
    # Reports and analytics
    path('reports/', include('core.teacher.reports.urls', namespace='reports')),
]