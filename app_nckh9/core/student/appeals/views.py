from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator

from core.common.utils.constants import (
    ALLOWED_FILE_TYPES,
    MAX_FILE_SIZE,
    APPEAL_STATUS_PENDING
)
from .models import Appeal, AppealHistory
from ..profile.models import StudentProfile

@login_required
def appeal_list(request):
    """Xem danh sách khiếu nại"""
    try:
        student = StudentProfile.objects.get(email=request.user.email)
        appeals = Appeal.objects.filter(student=student)
        
        # Lọc theo trạng thái nếu có
        status = request.GET.get('status')
        if status:
            appeals = appeals.filter(status=status)
            
        # Phân trang
        paginator = Paginator(appeals, 10)
        page = request.GET.get('page')
        appeals = paginator.get_page(page)
        
        context = {
            'student': student,
            'appeals': appeals,
            'status_choices': Appeal.STATUS_CHOICES
        }
        return render(request, 'student/appeals/list.html', context)
        
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('student:dashboard')

@login_required
def appeal_create(request):
    """Tạo khiếu nại mới"""
    try:
        student = StudentProfile.objects.get(email=request.user.email)
        
        if request.method == 'POST':
            # Kiểm tra xem sinh viên có đang trong thời gian được phép khiếu nại
            current_semester = student.class_name.hoc_ky_hien_tai
            if not current_semester or not current_semester.is_appeal_period:
                messages.error(request, 'Hiện không trong thời gian khiếu nại')
                return redirect('student:appeal_list')
            
            # Tạo khiếu nại mới
            appeal = Appeal(
                student=student,
                semester=current_semester,
                appeal_type=request.POST.get('appeal_type'),
                title=request.POST.get('title'),
                content=request.POST.get('content'),
                status=APPEAL_STATUS_PENDING
            )
            
            # Xử lý file minh chứng
            evidence_files = {}
            for i in range(1, 4):  # Cho phép tối đa 3 file
                file_key = f'evidence_{i}'
                if file_key in request.FILES:
                    file = request.FILES[file_key]
                    
                    # Kiểm tra định dạng file
                    if file.content_type not in ALLOWED_FILE_TYPES:
                        messages.error(
                            request,
                            f'File {file_key} không đúng định dạng. Chỉ chấp nhận ảnh hoặc PDF.'
                        )
                        return render(request, 'student/appeals/create.html')

                    # Kiểm tra kích thước file
                    if file.size > MAX_FILE_SIZE:
                        messages.error(
                            request,
                            f'File {file_key} quá lớn. Kích thước tối đa là 5MB.'
                        )
                        return render(request, 'student/appeals/create.html')

                    evidence_files[file_key] = file
            
            appeal.evidence_files = evidence_files
            appeal.save()
            
            # Tạo lịch sử
            AppealHistory.objects.create(
                appeal=appeal,
                old_status='',
                new_status=APPEAL_STATUS_PENDING,
                changed_by=request.user,
                note='Tạo khiếu nại mới'
            )
            
            messages.success(request, 'Đã gửi khiếu nại thành công')
            return redirect('student:appeal_list')
            
        context = {
            'student': student,
            'appeal_types': Appeal.APPEAL_TYPES
        }
        return render(request, 'student/appeals/create.html', context)
        
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('student:dashboard')

@login_required
def appeal_detail(request, appeal_id):
    """Xem chi tiết khiếu nại"""
    appeal = get_object_or_404(Appeal, id=appeal_id)
    
    # Kiểm tra quyền truy cập
    if appeal.student.email != request.user.email:
        messages.error(request, 'Bạn không có quyền xem thông tin này')
        return redirect('student:appeal_list')
    
    context = {
        'appeal': appeal,
        'history': appeal.history.all().select_related('changed_by')
    }
    return render(request, 'student/appeals/detail.html', context)

@login_required
def appeal_update(request, appeal_id):
    """Cập nhật khiếu nại"""
    appeal = get_object_or_404(Appeal, id=appeal_id)
    
    # Kiểm tra quyền cập nhật
    if appeal.student.email != request.user.email:
        messages.error(request, 'Bạn không có quyền cập nhật thông tin này')
        return redirect('student:appeal_list')
        
    # Chỉ cho phép cập nhật khi đang ở trạng thái pending
    if appeal.status != APPEAL_STATUS_PENDING:
        messages.error(request, 'Không thể cập nhật khiếu nại đã được xử lý')
        return redirect('student:appeal_detail', appeal_id=appeal.id)
    
    if request.method == 'POST':
        # Lưu trạng thái cũ
        old_content = appeal.content
        
        # Cập nhật thông tin
        appeal.content = request.POST.get('content')
        
        # Xử lý file minh chứng mới nếu có
        if 'new_evidence' in request.FILES:
            file = request.FILES['new_evidence']
            
            if file.content_type not in ALLOWED_FILE_TYPES:
                messages.error(request, 'File không đúng định dạng')
                return render(request, 'student/appeals/update.html', {'appeal': appeal})
                
            if file.size > MAX_FILE_SIZE:
                messages.error(request, 'File quá lớn (tối đa 5MB)')
                return render(request, 'student/appeals/update.html', {'appeal': appeal})
            
            # Thêm file mới vào evidence_files
            evidence_files = appeal.evidence_files
            file_key = f'evidence_{len(evidence_files) + 1}'
            evidence_files[file_key] = file
            appeal.evidence_files = evidence_files
        
        appeal.save()
        
        # Tạo lịch sử
        if old_content != appeal.content:
            AppealHistory.objects.create(
                appeal=appeal,
                old_status=appeal.status,
                new_status=appeal.status,
                changed_by=request.user,
                note='Cập nhật nội dung khiếu nại'
            )
        
        messages.success(request, 'Đã cập nhật khiếu nại')
        return redirect('student:appeal_detail', appeal_id=appeal.id)
    
    return render(request, 'student/appeals/update.html', {'appeal': appeal})

@login_required
def appeal_cancel(request, appeal_id):
    """Hủy khiếu nại"""
    appeal = get_object_or_404(Appeal, id=appeal_id)
    
    # Kiểm tra quyền hủy
    if appeal.student.email != request.user.email:
        messages.error(request, 'Bạn không có quyền hủy khiếu nại này')
        return redirect('student:appeal_list')
        
    # Chỉ cho phép hủy khi đang ở trạng thái pending
    if appeal.status != APPEAL_STATUS_PENDING:
        messages.error(request, 'Không thể hủy khiếu nại đã được xử lý')
        return redirect('student:appeal_detail', appeal_id=appeal.id)
    
    if request.method == 'POST':
        # Cập nhật trạng thái và lưu lịch sử
        old_status = appeal.status
        appeal.status = 'cancelled'
        appeal.save()
        
        AppealHistory.objects.create(
            appeal=appeal,
            old_status=old_status,
            new_status='cancelled',
            changed_by=request.user,
            note='Hủy khiếu nại'
        )
        
        messages.success(request, 'Đã hủy khiếu nại')
        return redirect('student:appeal_list')
    
    return render(request, 'student/appeals/cancel.html', {'appeal': appeal})