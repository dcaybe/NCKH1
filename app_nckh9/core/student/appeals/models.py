from django.db import models
from core.common.base.models import TimeStampedModel
from core.common.utils.constants import APPEAL_STATUS_PENDING

class Appeal(TimeStampedModel):
    """Model quản lý khiếu nại của sinh viên"""
    APPEAL_TYPES = [
        ('score', 'Điểm rèn luyện'),
        ('evaluation', 'Đánh giá'),
        ('other', 'Khác'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Đang chờ xử lý'),
        ('reviewing', 'Đang xem xét'),
        ('approved', 'Đã chấp nhận'),
        ('rejected', 'Đã từ chối'),
    ]

    student = models.ForeignKey(
        'student.StudentProfile',
        on_delete=models.CASCADE,
        related_name='appeals',
        verbose_name="Sinh viên"
    )
    
    semester = models.ForeignKey(
        'common.Semester',
        on_delete=models.CASCADE,
        related_name='appeals',
        verbose_name="Học kỳ"
    )
    
    score_rating = models.ForeignKey(
        'student.ScoreRating',
        on_delete=models.CASCADE,
        related_name='appeals',
        verbose_name="Điểm rèn luyện",
        null=True,
        blank=True
    )
    
    appeal_type = models.CharField(
        max_length=50,
        choices=APPEAL_TYPES,
        verbose_name="Loại khiếu nại"
    )
    
    title = models.CharField(
        max_length=255,
        verbose_name="Tiêu đề"
    )
    
    content = models.TextField(
        verbose_name="Nội dung"
    )
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=APPEAL_STATUS_PENDING,
        verbose_name="Trạng thái"
    )
    
    response = models.TextField(
        blank=True,
        null=True,
        verbose_name="Phản hồi"
    )
    
    reviewer = models.ForeignKey(
        'teacher.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_appeals',
        verbose_name="Người xem xét"
    )
    
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Thời gian xem xét"
    )

    evidence_files = models.JSONField(
        default=dict,
        verbose_name="File minh chứng"
    )

    class Meta:
        verbose_name = "Khiếu nại"
        verbose_name_plural = "Danh sách khiếu nại"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Nếu status thay đổi sang approved hoặc rejected
        # thì cập nhật reviewed_at
        if self.status in ['approved', 'rejected'] and not self.reviewed_at:
            from django.utils import timezone
            self.reviewed_at = timezone.now()
        super().save(*args, **kwargs)

class AppealHistory(TimeStampedModel):
    """Model lưu lịch sử thay đổi trạng thái khiếu nại"""
    appeal = models.ForeignKey(
        Appeal,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="Khiếu nại"
    )
    
    old_status = models.CharField(
        max_length=50,
        choices=Appeal.STATUS_CHOICES,
        verbose_name="Trạng thái cũ"
    )
    
    new_status = models.CharField(
        max_length=50,
        choices=Appeal.STATUS_CHOICES,
        verbose_name="Trạng thái mới"
    )
    
    changed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='appeal_status_changes',
        verbose_name="Người thay đổi"
    )
    
    note = models.TextField(
        blank=True,
        verbose_name="Ghi chú"
    )

    class Meta:
        verbose_name = "Lịch sử khiếu nại"
        verbose_name_plural = "Lịch sử khiếu nại"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.appeal} - {self.new_status}"