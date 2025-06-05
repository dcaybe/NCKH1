from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg

from core.common.utils.constants import ALLOWED_FILE_TYPES, MAX_FILE_SIZE
from .models import ScoreRating
from ..profile.models import StudentProfile

@login_required
def score_rating(request):
    """Xử lý chấm điểm rèn luyện của sinh viên"""
    try:
        student = StudentProfile.objects.get(email=request.user.email)
        
        if request.method == 'POST':
            # Khởi tạo đối tượng ScoreRating
            score = ScoreRating(
                student=student,
                
                # Điểm học tập
                learning_score=int(request.POST.get('learning_score', 0)),
                research_score=int(request.POST.get('research_score', 0)),
                no_cheating='no_cheating' in request.POST,
                no_late='no_late' in request.POST,
                skip_olympic='skip_olympic' in request.POST,
                skip_class='skip_class' in request.POST,
                
                # Điểm nội quy
                no_discipline_violation='no_discipline_violation' in request.POST,
                union_score=int(request.POST.get('union_score', 0)),
                missing_meetings='missing_meetings' in request.POST,
                no_student_card='no_student_card' in request.POST,
                no_class_meetings='no_class_meetings' in request.POST,
                late_fee='late_fee' in request.POST,
                
                # Điểm hoạt động
                full_attendance='full_attendance' in request.POST,
                activity_score=int(request.POST.get('activity_score', 0)),
                admission_participation='admission_participation' in request.POST,
                missing_activities='missing_activities' in request.POST,
                violate_culture='violate_culture' in request.POST,
                
                # Điểm công dân
                party_compliance='party_compliance' in request.POST,
                community_service='community_service' in request.POST,
                destroy_solidarity='destroy_solidarity' in request.POST,
                late_insurance='late_insurance' in request.POST,
                
                # Điểm cán bộ lớp
                class_role_score=int(request.POST.get('class_role_score', 0)),
                achievements='achievements' in request.POST,
                irresponsible='irresponsible' in request.POST,
            )

            # Xử lý file minh chứng
            evidence_files = {}
            notes = {}
            for i in range(1, 8):
                file_key = f'evidence_{i}'
                if file_key in request.FILES:
                    file = request.FILES[file_key]
                    
                    # Kiểm tra định dạng file
                    if file.content_type not in ALLOWED_FILE_TYPES:
                        messages.error(
                            request,
                            f'File {file_key} không đúng định dạng. Chỉ chấp nhận ảnh hoặc PDF.'
                        )
                        return render(request, 'student/score/rating.html', {'student': student})

                    # Kiểm tra kích thước file
                    if file.size > MAX_FILE_SIZE:
                        messages.error(
                            request,
                            f'File {file_key} quá lớn. Kích thước tối đa là 5MB.'
                        )
                        return render(request, 'student/score/rating.html', {'student': student})

                    evidence_files[file_key] = file
                
                # Lưu ghi chú
                note = request.POST.get(f'note_{i}')
                if note:
                    notes[f'note_{i}'] = note

            score.evidence_files = evidence_files
            score.notes = notes
            score.save()

            messages.success(
                request,
                f'Đã lưu điểm rèn luyện. Tổng điểm: {score.total_score}, '
                f'Xếp loại: {score.classification}'
            )
            return redirect('student:dashboard')

        context = {
            'student': student,
            'today_date': timezone.now().strftime("%d/%m/%Y")
        }
        return render(request, 'student/score/rating.html', context)
        
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('student:dashboard')

@login_required
def view_score(request):
    """Xem điểm rèn luyện của sinh viên"""
    try:
        student = StudentProfile.objects.get(email=request.user.email)
        scores = ScoreRating.objects.filter(student=student).order_by('-semester')
        
        # Tính điểm trung bình
        avg_score = scores.aggregate(Avg('total_score'))['total_score__avg']
        
        context = {
            'student': student,
            'scores': scores,
            'avg_score': round(avg_score, 2) if avg_score else 0
        }
        return render(request, 'student/score/view.html', context)
        
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('student:dashboard')

@login_required
def score_history(request):
    """Xem lịch sử điểm rèn luyện của sinh viên"""
    try:
        student = StudentProfile.objects.get(email=request.user.email)
        scores = ScoreRating.objects.filter(
            student=student
        ).select_related('semester').order_by('-semester')
        
        context = {
            'student': student,
            'scores': scores
        }
        return render(request, 'student/score/history.html', context)
        
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('student:dashboard')

@login_required
def score_detail(request, score_id):
    """Xem chi tiết một điểm rèn luyện cụ thể"""
    score = get_object_or_404(ScoreRating, id=score_id)
    
    # Kiểm tra quyền truy cập
    if score.student.email != request.user.email:
        messages.error(request, 'Bạn không có quyền xem thông tin này')
        return redirect('student:dashboard')
    
    context = {
        'score': score
    }
    return render(request, 'student/score/detail.html', context)