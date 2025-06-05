from django.db import models
from core.common.base.models import TimeStampedModel
from django.core.exceptions import ValidationError

class TeacherEvaluation(TimeStampedModel):
    """Model quản lý đánh giá điểm rèn luyện từ giáo viên"""
    teacher = models.ForeignKey(
        'teacher.TeacherProfile',
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name="Giáo viên"
    )
    
    student_score = models.ForeignKey(
        'student.ScoreRating',
        on_delete=models.CASCADE,
        related_name='teacher_evaluations',
        verbose_name="Điểm rèn luyện sinh viên"
    )
    
    # Đánh giá điểm học tập
    learning_score_adjustment = models.IntegerField(
        default=0,
        verbose_name="Điều chỉnh điểm học tập"
    )
    learning_score_note = models.TextField(
        blank=True,
        verbose_name="Ghi chú điểm học tập"
    )
    
    # Đánh giá điểm nội quy
    discipline_score_adjustment = models.IntegerField(
        default=0,
        verbose_name="Điều chỉnh điểm nội quy"
    )
    discipline_score_note = models.TextField(
        blank=True,
        verbose_name="Ghi chú điểm nội quy"
    )
    
    # Đánh giá điểm hoạt động
    activity_score_adjustment = models.IntegerField(
        default=0,
        verbose_name="Điều chỉnh điểm hoạt động"
    )
    activity_score_note = models.TextField(
        blank=True,
        verbose_name="Ghi chú điểm hoạt động"
    )
    
    # Đánh giá tổng thể
    overall_comment = models.TextField(
        blank=True,
        verbose_name="Nhận xét tổng thể"
    )
    
    is_approved = models.BooleanField(
        default=False,
        verbose_name="Đã phê duyệt"
    )
    
    evidence_files = models.JSONField(
        default=dict,
        verbose_name="File minh chứng"
    )

    class Meta:
        verbose_name = "Đánh giá điểm rèn luyện"
        verbose_name_plural = "Danh sách đánh giá điểm rèn luyện"
        ordering = ['-created_at']
        unique_together = ['teacher', 'student_score']

    def __str__(self):
        return f"Đánh giá: {self.student_score}"

    def clean(self):
        # Kiểm tra giới hạn điều chỉnh điểm
        total_adjustment = (
            self.learning_score_adjustment +
            self.discipline_score_adjustment +
            self.activity_score_adjustment
        )
        if abs(total_adjustment) > 20:
            raise ValidationError(
                "Tổng điều chỉnh điểm không được vượt quá ±20"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Cập nhật điểm rèn luyện của sinh viên
        if self.is_approved:
            score = self.student_score
            score.learning_score += self.learning_score_adjustment
            score.activity_score += self.activity_score_adjustment
            score.save()

class EvaluationPeriod(TimeStampedModel):
    """Model quản lý đợt đánh giá điểm rèn luyện"""
    semester = models.ForeignKey(
        'common.Semester',
        on_delete=models.CASCADE,
        related_name='evaluation_periods',
        verbose_name="Học kỳ"
    )
    
    name = models.CharField(
        max_length=255,
        verbose_name="Tên đợt đánh giá"
    )
    
    start_date = models.DateField(
        verbose_name="Ngày bắt đầu"
    )
    
    end_date = models.DateField(
        verbose_name="Ngày kết thúc"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Mô tả"
    )

    class Meta:
        verbose_name = "Đợt đánh giá"
        verbose_name_plural = "Danh sách đợt đánh giá"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} - {self.semester}"

    def clean(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(
                    "Ngày kết thúc không thể trước ngày bắt đầu"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.is_active:
            # Hủy kích hoạt các đợt đánh giá khác trong cùng học kỳ
            EvaluationPeriod.objects.filter(
                semester=self.semester,
                is_active=True
            ).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)