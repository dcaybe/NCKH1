from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q

from core.common.utils.constants import ALLOWED_FILE_TYPES, MAX_FILE_SIZE
from .models import TeacherEvaluation, EvaluationPeriod
from core.teacher.models import TeacherProfile
from core.student.score.models import ScoreRating

@login_required
def evaluation_list(request):
    """Xem danh sách đánh giá"""
    try:
        teacher = TeacherProfile.objects.get(email=request.user.email)
        evaluations = TeacherEvaluation.objects.filter(teacher=teacher)
        
        # Lọc theo trạng thái
        status = request.GET.get('status')
        if status == 'pending':
            evaluations = evaluations.filter(is_approved=False)
        elif status == 'approved':
            evaluations = evaluations.filter(is_approved=True)
            
        # Lọc theo học kỳ
        semester = request.GET.get('semester')
        if semester:
            evaluations = evaluations.filter(
                student_score__semester__ma_hoc_ky=semester
            )
            
        # Phân trang
        paginator = Paginator(evaluations, 10)
        page = request.GET.get('page')
        evaluations = paginator.get_page(page)
        
        context = {
            'teacher': teacher,
            'evaluations': evaluations,
            'current_period': EvaluationPeriod.objects.filter(
                is_active=True
            ).first()
        }
        return render(request, 'teacher/evaluation/list.html', context)
        
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('teacher:dashboard')

@login_required
def evaluation_detail(request, evaluation_id):
    """Xem chi tiết đánh giá"""
    evaluation = get_object_or_404(TeacherEvaluation, id=evaluation_id)
    
    # Kiểm tra quyền truy cập
    if evaluation.teacher.email != request.user.email:
        messages.error(request, 'Bạn không có quyền xem thông tin này')
        return redirect('teacher:evaluation_list')
    
    context = {
        'evaluation': evaluation,
        'student_score': evaluation.student_score,
        'student': evaluation.student_score.student
    }
    return render(request, 'teacher/evaluation/detail.html', context)

@login_required
def evaluation_create(request, score_id):
    """Tạo đánh giá mới"""
    score = get_object_or_404(ScoreRating, id=score_id)
    
    try:
        teacher = TeacherProfile.objects.get(email=request.user.email)
        
        # Kiểm tra quyền đánh giá
        if score.student.class_name.advisor != teacher:
            messages.error(request, 'Bạn không có quyền đánh giá sinh viên này')
            return redirect('teacher:class_list')
        
        # Kiểm tra thời gian đánh giá
        current_period = EvaluationPeriod.objects.filter(is_active=True).first()
        if not current_period:
            messages.error(request, 'Hiện không trong thời gian đánh giá')
            return redirect('teacher:evaluation_list')
        
        if request.method == 'POST':
            evaluation = TeacherEvaluation(
                teacher=teacher,
                student_score=score,
                learning_score_adjustment=int(
                    request.POST.get('learning_score_adjustment', 0)
                ),
                learning_score_note=request.POST.get('learning_score_note', ''),
                discipline_score_adjustment=int(
                    request.POST.get('discipline_score_adjustment', 0)
                ),
                discipline_score_note=request.POST.get(
                    'discipline_score_note', ''
                ),
                activity_score_adjustment=int(
                    request.POST.get('activity_score_adjustment', 0)
                ),
                activity_score_note=request.POST.get('activity_score_note', ''),
                overall_comment=request.POST.get('overall_comment', ''),
                is_approved=request.POST.get('is_approved') == 'on'
            )
            
            # Xử lý file minh chứng
            evidence_files = {}
            for file_key in request.FILES:
                file = request.FILES[file_key]
                
                if file.content_type not in ALLOWED_FILE_TYPES:
                    messages.error(
                        request,
                        'File không đúng định dạng. Chỉ chấp nhận ảnh hoặc PDF.'
                    )
                    return render(
                        request,
                        'teacher/evaluation/create.html',
                        {'score': score}
                    )
                    
                if file.size > MAX_FILE_SIZE:
                    messages.error(
                        request,
                        'File quá lớn. Kích thước tối đa là 5MB.'
                    )
                    return render(
                        request,
                        'teacher/evaluation/create.html',
                        {'score': score}
                    )
                
                evidence_files[file_key] = file
                
            evaluation.evidence_files = evidence_files
            
            try:
                evaluation.full_clean()
                evaluation.save()
                messages.success(request, 'Đã lưu đánh giá')
                return redirect(
                    'teacher:evaluation_detail',
                    evaluation_id=evaluation.id
                )
            except Exception as e:
                messages.error(request, str(e))
        
        context = {
            'score': score,
            'student': score.student,
            'evaluation_period': current_period
        }
        return render(request, 'teacher/evaluation/create.html', context)
        
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('teacher:dashboard')

@login_required
def evaluation_edit(request, evaluation_id):
    """Chỉnh sửa đánh giá"""
    evaluation = get_object_or_404(TeacherEvaluation, id=evaluation_id)
    
    # Kiểm tra quyền chỉnh sửa
    if evaluation.teacher.email != request.user.email:
        messages.error(request, 'Bạn không có quyền chỉnh sửa đánh giá này')
        return redirect('teacher:evaluation_list')
    
    # Kiểm tra trạng thái
    if evaluation.is_approved:
        messages.error(request, 'Không thể chỉnh sửa đánh giá đã phê duyệt')
        return redirect(
            'teacher:evaluation_detail',
            evaluation_id=evaluation.id
        )
    
    if request.method == 'POST':
        evaluation.learning_score_adjustment = int(
            request.POST.get('learning_score_adjustment', 0)
        )
        evaluation.learning_score_note = request.POST.get(
            'learning_score_note',
            ''
        )
        evaluation.discipline_score_adjustment = int(
            request.POST.get('discipline_score_adjustment', 0)
        )
        evaluation.discipline_score_note = request.POST.get(
            'discipline_score_note',
            ''
        )
        evaluation.activity_score_adjustment = int(
            request.POST.get('activity_score_adjustment', 0)
        )
        evaluation.activity_score_note = request.POST.get(
            'activity_score_note',
            ''
        )
        evaluation.overall_comment = request.POST.get('overall_comment', '')
        evaluation.is_approved = request.POST.get('is_approved') == 'on'
        
        try:
            evaluation.full_clean()
            evaluation.save()
            messages.success(request, 'Đã cập nhật đánh giá')
            return redirect(
                'teacher:evaluation_detail',
                evaluation_id=evaluation.id
            )
        except Exception as e:
            messages.error(request, str(e))
    
    context = {
        'evaluation': evaluation,
        'student': evaluation.student_score.student
    }
    return render(request, 'teacher/evaluation/edit.html', context)