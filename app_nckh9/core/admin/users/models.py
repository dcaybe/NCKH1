from django.db import models
from django.contrib.auth.models import AbstractUser
from core.common.base.models import TimeStampedModel

class CustomUser(AbstractUser):
    """Model mở rộng Django User model"""
    USER_TYPES = [
        ('admin', 'Admin'),
        ('teacher', 'Giáo viên'),
        ('student', 'Sinh viên'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        default='student',
        verbose_name="Loại tài khoản"
    )
    
    email = models.EmailField(
        unique=True,
        verbose_name="Email"
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="Số điện thoại"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP đăng nhập cuối"
    )
    
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Số lần đăng nhập thất bại"
    )
    
    password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Thời điểm đổi mật khẩu"
    )

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Danh sách người dùng"

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class UserActivity(TimeStampedModel):
    """Model lưu lịch sử hoạt động của người dùng"""
    ACTIVITY_TYPES = [
        ('login', 'Đăng nhập'),
        ('logout', 'Đăng xuất'),
        ('password_change', 'Đổi mật khẩu'),
        ('profile_update', 'Cập nhật thông tin'),
        ('other', 'Khác'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name="Người dùng"
    )
    
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPES,
        verbose_name="Loại hoạt động"
    )
    
    description = models.TextField(
        verbose_name="Mô tả"
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name="Địa chỉ IP"
    )
    
    user_agent = models.TextField(
        verbose_name="User Agent"
    )
    
    status = models.CharField(
        max_length=50,
        default='success',
        verbose_name="Trạng thái"
    )

    class Meta:
        verbose_name = "Hoạt động người dùng"
        verbose_name_plural = "Lịch sử hoạt động"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.get_activity_type_display()}"

class UserPermission(TimeStampedModel):
    """Model quản lý quyền của người dùng"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='permissions',
        verbose_name="Người dùng"
    )
    
    codename = models.CharField(
        max_length=100,
        verbose_name="Mã quyền"
    )
    
    module = models.CharField(
        max_length=50,
        verbose_name="Module"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Mô tả"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang kích hoạt"
    )
    
    granted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='granted_permissions',
        verbose_name="Người cấp quyền"
    )
    
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời điểm cấp quyền"
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Thời điểm hết hạn"
    )

    class Meta:
        verbose_name = "Quyền người dùng"
        verbose_name_plural = "Danh sách quyền"
        unique_together = ['user', 'codename']
        ordering = ['module', 'codename']

    def __str__(self):
        return f"{self.user} - {self.codename}"

    def is_valid(self):
        """Kiểm tra quyền còn hiệu lực không"""
        from django.utils import timezone
        return (
            self.is_active and
            (not self.expires_at or self.expires_at > timezone.now())
        )