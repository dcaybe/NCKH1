from django.db import models
from django.core.exceptions import ValidationError
from core.common.base.models import TimeStampedModel

class SystemSetting(TimeStampedModel):
    """Model quản lý cài đặt hệ thống"""
    SETTING_TYPES = [
        ('general', 'Cài đặt chung'),
        ('email', 'Cài đặt email'),
        ('security', 'Cài đặt bảo mật'),
        ('scoring', 'Cài đặt chấm điểm'),
        ('notification', 'Cài đặt thông báo'),
    ]
    
    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Khóa cài đặt"
    )
    
    value = models.JSONField(
        verbose_name="Giá trị"
    )
    
    setting_type = models.CharField(
        max_length=20,
        choices=SETTING_TYPES,
        verbose_name="Loại cài đặt"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Mô tả"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang kích hoạt"
    )

    class Meta:
        verbose_name = "Cài đặt hệ thống"
        verbose_name_plural = "Cài đặt hệ thống"
        ordering = ['setting_type', 'key']

    def __str__(self):
        return f"{self.get_setting_type_display()} - {self.key}"

    def clean(self):
        # Kiểm tra giá trị hợp lệ dựa vào loại cài đặt
        try:
            if self.setting_type == 'general':
                self._validate_general_setting()
            elif self.setting_type == 'email':
                self._validate_email_setting()
            elif self.setting_type == 'security':
                self._validate_security_setting()
            elif self.setting_type == 'scoring':
                self._validate_scoring_setting()
            elif self.setting_type == 'notification':
                self._validate_notification_setting()
        except ValueError as e:
            raise ValidationError(str(e))

    def _validate_general_setting(self):
        required_fields = ['site_name', 'timezone', 'language']
        for field in required_fields:
            if field not in self.value:
                raise ValueError(f"Thiếu trường {field} trong cài đặt chung")

    def _validate_email_setting(self):
        required_fields = ['smtp_host', 'smtp_port', 'smtp_user', 'smtp_password']
        for field in required_fields:
            if field not in self.value:
                raise ValueError(f"Thiếu trường {field} trong cài đặt email")

    def _validate_security_setting(self):
        required_fields = ['min_password_length', 'password_expire_days']
        for field in required_fields:
            if field not in self.value:
                raise ValueError(f"Thiếu trường {field} trong cài đặt bảo mật")

    def _validate_scoring_setting(self):
        required_fields = ['min_score', 'max_score', 'passing_score']
        for field in required_fields:
            if field not in self.value:
                raise ValueError(f"Thiếu trường {field} trong cài đặt chấm điểm")

    def _validate_notification_setting(self):
        required_fields = ['email_notify', 'web_notify']
        for field in required_fields:
            if field not in self.value:
                raise ValueError(f"Thiếu trường {field} trong cài đặt thông báo")

class SettingHistory(TimeStampedModel):
    """Model lưu lịch sử thay đổi cài đặt"""
    setting = models.ForeignKey(
        SystemSetting,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="Cài đặt"
    )
    
    old_value = models.JSONField(
        verbose_name="Giá trị cũ"
    )
    
    new_value = models.JSONField(
        verbose_name="Giá trị mới"
    )
    
    changed_by = models.ForeignKey(
        'admin.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='setting_changes',
        verbose_name="Người thay đổi"
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name="Lý do thay đổi"
    )

    class Meta:
        verbose_name = "Lịch sử cài đặt"
        verbose_name_plural = "Lịch sử cài đặt"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.setting} - {self.created_at}"