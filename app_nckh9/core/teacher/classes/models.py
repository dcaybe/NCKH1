from django.db import models
from core.common.base.models import TimeStampedModel
from django.core.exceptions import ValidationError

class ClassInfo(TimeStampedModel):
    """Model quản lý thông tin lớp học"""
    class_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Mã lớp"
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name="Tên lớp"
    )
    
    department = models.CharField(
        max_length=100,
        verbose_name="Khoa"
    )
    
    year = models.IntegerField(
        verbose_name="Khóa học"
    )
    
    advisor = models.ForeignKey(
        'teacher.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='advised_classes',
        verbose_name="Cố vấn học tập"
    )
    
    max_students = models.PositiveSmallIntegerField(
        default=125,
        verbose_name="Sĩ số tối đa"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Mô tả"
    )
    
    current_semester = models.ForeignKey(
        'common.Semester',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_classes',
        verbose_name="Học kỳ hiện tại"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )

    class Meta:
        verbose_name = "Lớp học"
        verbose_name_plural = "Danh sách lớp học"
        ordering = ['department', 'year', 'class_id']

    def __str__(self):
        return f"{self.class_id} - {self.name}"

    def clean(self):
        # Kiểm tra sĩ số tối đa
        if self.max_students < self.current_student_count:
            raise ValidationError(
                "Sĩ số tối đa không thể nhỏ hơn số sinh viên hiện tại"
            )

    @property
    def current_student_count(self):
        """Lấy số lượng sinh viên hiện tại"""
        return self.students.filter(is_active=True).count()

    def has_space(self):
        """Kiểm tra xem lớp còn chỗ không"""
        return self.current_student_count < self.max_students

    def add_student(self, student):
        """Thêm sinh viên vào lớp"""
        if not self.has_space():
            raise ValidationError("Lớp đã đủ sĩ số")
        if not self.is_active:
            raise ValidationError("Lớp không còn hoạt động")
        
        student.class_name = self
        student.save()

    def remove_student(self, student):
        """Xóa sinh viên khỏi lớp"""
        if student.class_name != self:
            raise ValidationError("Sinh viên không thuộc lớp này")
        
        student.class_name = None
        student.save()

class ClassActivity(TimeStampedModel):
    """Model quản lý hoạt động của lớp"""
    class_info = models.ForeignKey(
        ClassInfo,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name="Lớp học"
    )
    
    title = models.CharField(
        max_length=255,
        verbose_name="Tiêu đề"
    )
    
    description = models.TextField(
        verbose_name="Mô tả"
    )
    
    start_date = models.DateField(
        verbose_name="Ngày bắt đầu"
    )
    
    end_date = models.DateField(
        verbose_name="Ngày kết thúc"
    )
    
    is_required = models.BooleanField(
        default=False,
        verbose_name="Bắt buộc tham gia"
    )
    
    participants = models.ManyToManyField(
        'student.StudentProfile',
        related_name='class_activities',
        verbose_name="Người tham gia"
    )
    
    attachments = models.JSONField(
        default=dict,
        verbose_name="File đính kèm"
    )

    class Meta:
        verbose_name = "Hoạt động lớp"
        verbose_name_plural = "Danh sách hoạt động"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.class_info} - {self.title}"

    def clean(self):
        # Kiểm tra ngày
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(
                    "Ngày kết thúc không thể trước ngày bắt đầu"
                )