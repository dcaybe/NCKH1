from django.db import models
from core.common.base.models import TimeStampedModel
from core.common.utils.constants import (
    SCORE_RULES,
    SCORE_RANGE_EXCELLENT,
    SCORE_RANGE_GOOD,
    SCORE_RANGE_FAIR,
    SCORE_RANGE_AVERAGE,
    SCORE_RANGE_WEAK,
    SCORE_EXCELLENT,
    SCORE_GOOD,
    SCORE_FAIR,
    SCORE_AVERAGE,
    SCORE_WEAK,
    SCORE_POOR,
)

class ScoreRating(TimeStampedModel):
    """Model quản lý điểm rèn luyện của sinh viên"""
    student = models.ForeignKey(
        'student.StudentProfile',
        on_delete=models.CASCADE,
        related_name='score_ratings'
    )
    semester = models.ForeignKey(
        'common.Semester',
        on_delete=models.CASCADE,
        related_name='score_ratings'
    )
    
    # Điểm học tập
    learning_score = models.IntegerField(default=0)
    research_score = models.IntegerField(default=0)
    no_cheating = models.BooleanField(default=False)
    no_late = models.BooleanField(default=False)
    skip_olympic = models.BooleanField(default=False)
    skip_class = models.BooleanField(default=False)
    
    # Điểm nội quy
    no_discipline_violation = models.BooleanField(default=False)
    union_score = models.IntegerField(default=0)
    missing_meetings = models.BooleanField(default=False)
    no_student_card = models.BooleanField(default=False)
    no_class_meetings = models.BooleanField(default=False)
    late_fee = models.BooleanField(default=False)
    
    # Điểm hoạt động
    full_attendance = models.BooleanField(default=False)
    activity_score = models.IntegerField(default=0)
    admission_participation = models.BooleanField(default=False)
    missing_activities = models.BooleanField(default=False)
    violate_culture = models.BooleanField(default=False)
    
    # Điểm công dân
    party_compliance = models.BooleanField(default=False)
    community_service = models.BooleanField(default=False)
    destroy_solidarity = models.BooleanField(default=False)
    late_insurance = models.BooleanField(default=False)
    
    # Điểm cán bộ lớp
    class_role_score = models.IntegerField(default=0)
    achievements = models.BooleanField(default=False)
    irresponsible = models.BooleanField(default=False)
    
    # Minh chứng
    evidence_files = models.JSONField(default=dict)
    notes = models.JSONField(default=dict)
    
    # Kết quả
    total_score = models.IntegerField(default=0)
    classification = models.CharField(max_length=50, default=SCORE_POOR)
    is_approved = models.BooleanField(default=False)

    def calculate_total_score(self):
        """Tính tổng điểm dựa trên các tiêu chí"""
        score = (
            self.learning_score +
            self.research_score +
            (SCORE_RULES['koDungPhao'] if self.no_cheating else 0) +
            (SCORE_RULES['koDiHocMuon'] if self.no_late else 0) +
            (SCORE_RULES['boThiOlympic'] if self.skip_olympic else 0) +
            (SCORE_RULES['tronHoc'] if self.skip_class else 0) +
            (SCORE_RULES['koVPKL'] if self.no_discipline_violation else 0) +
            self.union_score +
            (SCORE_RULES['koThamgiaDaydu'] if self.missing_meetings else 0) +
            (SCORE_RULES['koDeoTheSV'] if self.no_student_card else 0) +
            (SCORE_RULES['koSHL'] if self.no_class_meetings else 0) +
            (SCORE_RULES['dongHPmuon'] if self.late_fee else 0) +
            (SCORE_RULES['thamgiaDayDu'] if self.full_attendance else 0) +
            self.activity_score +
            (SCORE_RULES['thamgiaTVTS'] if self.admission_participation else 0) +
            (SCORE_RULES['koThamgiaDaydu2'] if self.missing_activities else 0) +
            (SCORE_RULES['viphamVanHoaSV'] if self.violate_culture else 0) +
            (SCORE_RULES['chaphanhDang'] if self.party_compliance else 0) +
            (SCORE_RULES['giupdoCongDong'] if self.community_service else 0) +
            (SCORE_RULES['gayMatDoanKet'] if self.destroy_solidarity else 0) +
            (SCORE_RULES['dongBHYTmuon'] if self.late_insurance else 0) +
            self.class_role_score +
            (SCORE_RULES['caccapKhenThuong'] if self.achievements else 0) +
            (SCORE_RULES['BCSvotrachnghiem'] if self.irresponsible else 0)
        )
        
        return max(0, min(100, score))  # Giới hạn trong khoảng 0-100

    def set_classification(self):
        """Xếp loại dựa trên tổng điểm"""
        if self.total_score >= SCORE_RANGE_EXCELLENT:
            self.classification = SCORE_EXCELLENT
        elif self.total_score >= SCORE_RANGE_GOOD:
            self.classification = SCORE_GOOD
        elif self.total_score >= SCORE_RANGE_FAIR:
            self.classification = SCORE_FAIR
        elif self.total_score >= SCORE_RANGE_AVERAGE:
            self.classification = SCORE_AVERAGE
        elif self.total_score >= SCORE_RANGE_WEAK:
            self.classification = SCORE_WEAK
        else:
            self.classification = SCORE_POOR

    def save(self, *args, **kwargs):
        self.total_score = self.calculate_total_score()
        self.set_classification()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.semester} - {self.classification}"

    class Meta:
        ordering = ['-semester', '-total_score']
        unique_together = ['student', 'semester']