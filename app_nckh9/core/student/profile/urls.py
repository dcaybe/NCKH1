from django.urls import path
from . import views

app_name = 'student_profile'

urlpatterns = [
    # Profile views
    path('', views.profile_view, name='view'),
    path('edit/', views.profile_edit, name='edit'),
    
    # Document management
    path('documents/', views.document_list, name='document_list'),
    path('documents/upload/', views.document_upload, name='document_upload'),
    path('documents/delete/<int:document_id>/', 
         views.document_delete, 
         name='document_delete'),
]