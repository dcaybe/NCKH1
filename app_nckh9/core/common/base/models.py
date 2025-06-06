from django.db import models
from django.utils import timezone

# Base Models
class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created' and 'modified' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserProfile(TimeStampedModel):
    """
    Base user profile model with common fields
    """
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, default='active')
    
    class Meta:
        abstract = True

class AcademicInfo(TimeStampedModel):
    """
    Base academic information model
    """
    khoa = models.CharField(max_length=255)
    nien_khoa = models.CharField(max_length=255)
    he_dao_tao = models.CharField(max_length=255)
    
    class Meta:
        abstract = True