from django.db import models
from core.common.base.models import TimeStampedModel

class TeacherReport(TimeStampedModel):
    """Model quản lý báo cáo của giáo viên"""
    REPORT_TYPES = [
        ('class_summary', 'Tổng kết lớp'),
        ('score_analysis', 'Phân tích điểm rèn luyện'),
        ('activity_summary', 'Tổng kết hoạt động'),
        ('student_progress', 'Tiến độ sinh viên'),
        ('other', 'Khác'),
    ]
    
    PERIOD_TYPES = [
        ('semester', 'Học kỳ'),
        ('month', 'Tháng'),
        ('week', 'Tuần'),
        ('custom', 'Tùy chỉnh'),
    ]

    teacher = models.ForeignKey(
        'teacher.TeacherProfile',
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name="Giáo viên"
    )
    
    class_info = models.ForeignKey(
        'teacher.ClassInfo',
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name="Lớp học"
    )
    
    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPES,
        verbose_name="Loại báo cáo"
    )
    
    period_type = models.CharField(
        max_length=20,
        choices=PERIOD_TYPES,
        verbose_name="Loại thời gian"
    )
    
    title = models.CharField(
        max_length=255,
        verbose_name="Tiêu đề"
    )
    
    content = models.TextField(
        verbose_name="Nội dung"
    )
    
    from_date = models.DateField(
        verbose_name="Từ ngày"
    )
    
    to_date = models.DateField(
        verbose_name="Đến ngày"
    )
    
    attachments = models.JSONField(
        default=dict,
        verbose_name="File đính kèm"
    )
    
    analytics_data = models.JSONField(
        default=dict,
        verbose_name="Dữ liệu phân tích"
    )
    
    is_draft = models.BooleanField(
        default=True,
        verbose_name="Bản nháp"
    )

    class Meta:
        verbose_name = "Báo cáo"
        verbose_name_plural = "Danh sách báo cáo"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.class_info} - {self.title}"

class ScoreAnalytics(TimeStampedModel):
    """Model lưu trữ phân tích điểm rèn luyện"""
    class_info = models.ForeignKey(
        'teacher.ClassInfo',
        on_delete=models.CASCADE,
        related_name='score_analytics',
        verbose_name="Lớp học"
    )
    
    semester = models.ForeignKey(
        'common.Semester',
        on_delete=models.CASCADE,
        related_name='score_analytics',
        verbose_name="Học kỳ"
    )
    
    # Thống kê cơ bản
    total_students = models.IntegerField(
        verbose_name="Tổng số sinh viên"
    )
    
    evaluated_students = models.IntegerField(
        verbose_name="Số sinh viên đã đánh giá"
    )
    
    average_score = models.FloatField(
        verbose_name="Điểm trung bình"
    )
    
    # Phân phối điểm
    score_distribution = models.JSONField(
        default=dict,
        verbose_name="Phân phối điểm"
    )
    
    # Phân tích theo tiêu chí
    criteria_analysis = models.JSONField(
        default=dict,
        verbose_name="Phân tích tiêu chí"
    )
    
    # Xu hướng điểm
    score_trends = models.JSONField(
        default=dict,
        verbose_name="Xu hướng điểm"
    )
    
    # So sánh với kỳ trước
    previous_semester_comparison = models.JSONField(
        default=dict,
        verbose_name="So sánh với kỳ trước"
    )

    class Meta:
        verbose_name = "Phân tích điểm"
        verbose_name_plural = "Phân tích điểm"
        ordering = ['-semester']
        unique_together = ['class_info', 'semester']

    def __str__(self):
        return f"{self.class_info} - {self.semester}"

    def calculate_statistics(self):
        """Tính toán các chỉ số thống kê"""
        from core.student.score.models import ScoreRating
        from django.db.models import Avg, Count
        
        # Lấy tất cả điểm của lớp trong học kỳ
        scores = ScoreRating.objects.filter(
            student__class_name=self.class_info,
            semester=self.semester
        )
        
        # Cập nhật thống kê cơ bản
        self.total_students = self.class_info.current_student_count
        self.evaluated_students = scores.count()
        self.average_score = scores.aggregate(
            Avg('total_score')
        )['total_score__avg'] or 0
        
        # Tính phân phối điểm
        self.score_distribution = {
            'excellent': scores.filter(total_score__gte=90).count(),
            'good': scores.filter(total_score__range=(80, 89)).count(),
            'fair': scores.filter(total_score__range=(65, 79)).count(),
            'average': scores.filter(total_score__range=(50, 64)).count(),
            'weak': scores.filter(total_score__range=(35, 49)).count(),
            'poor': scores.filter(total_score__lt=35).count()
        }
        
        self.save()