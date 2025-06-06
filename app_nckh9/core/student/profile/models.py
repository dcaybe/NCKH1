from django.db import models
from core.common.base.models import UserProfile, AcademicInfo, TimeStampedModel

class StudentProfile(UserProfile, AcademicInfo):
    """Model quản lý thông tin sinh viên"""
    student_id = models.CharField(max_length=20, unique=True, verbose_name="Mã sinh viên")
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Nam'), ('female', 'Nữ')],
        verbose_name="Giới tính"
    )
    date_of_birth = models.DateField(verbose_name="Ngày sinh")
    class_name = models.ForeignKey(
        'teacher.ClassInfo',
        on_delete=models.SET_NULL,
        null=True,
        related_name='students',
        verbose_name="Lớp"
    )
    major = models.CharField(max_length=255, verbose_name="Chuyên ngành")
    
    # Thông tin cố vấn học tập
    advisor = models.ForeignKey(
        'teacher.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='advised_students',
        verbose_name="Cố vấn học tập"
    )
    
    class Meta:
        verbose_name = "Sinh viên"
        verbose_name_plural = "Danh sách sinh viên"
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"

    @property
    def current_semester_score(self):
        """Lấy điểm rèn luyện học kỳ hiện tại"""
        from core.student.score.models import ScoreRating
        current_score = ScoreRating.objects.filter(
            student=self,
            semester__is_current=True
        ).first()
        return current_score

    @property
    def score_average(self):
        """Tính điểm rèn luyện trung bình"""
        from core.student.score.models import ScoreRating
        from django.db.models import Avg
        
        avg = ScoreRating.objects.filter(
            student=self
        ).aggregate(Avg('total_score'))['total_score__avg']
        
        return round(avg, 2) if avg else 0

    def get_pending_appeals(self):
        """Lấy danh sách khiếu nại đang chờ xử lý"""
        from core.student.appeals.models import Appeal
        return Appeal.objects.filter(
            student=self,
            status='pending'
        ).order_by('-created_at')

class StudentDocument(TimeStampedModel):
    """Model quản lý các tài liệu của sinh viên"""
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="Sinh viên"
    )
    document_type = models.CharField(
        max_length=50,
        choices=[
            ('identity', 'CMND/CCCD'),
            ('academic_record', 'Bảng điểm'),
            ('certificate', 'Chứng chỉ'),
            ('other', 'Khác')
        ],
        verbose_name="Loại tài liệu"
    )
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    file = models.FileField(upload_to='student_documents/', verbose_name="File")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_verified = models.BooleanField(default=False, verbose_name="Đã xác minh")

    class Meta:
        verbose_name = "Tài liệu sinh viên"
        verbose_name_plural = "Danh sách tài liệu"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.title}"