from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path(
        'reset-password/<uidb64>/<token>/',
        views.password_reset_confirm,
        name='password_reset_confirm'
    ),
]