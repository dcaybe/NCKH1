"""
Core module chứa các thành phần chính của hệ thống
"""

from django.urls import path, include

# Main URL patterns
urlpatterns = [
    # Authentication
    path('auth/', include('core.common.auth.urls')),
    
    # Student module
    path('student/', include('core.student.urls')),
    
    # Teacher module 
    path('teacher/', include('core.teacher.urls')),
    
    # Admin module
    path('admin/', include('core.admin.urls')),
]

# Version info
VERSION = (1, 0, 0)
__version__ = '.'.join(map(str, VERSION))

# Default settings
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Default app config
default_app_config = 'core.apps.CoreConfig'