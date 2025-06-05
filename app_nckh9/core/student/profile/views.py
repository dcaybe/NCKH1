from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from core.common.utils.constants import ALLOWED_FILE_TYPES, MAX_FILE_SIZE
from .models import StudentProfile, StudentDocument

@login_required
def profile_view(request):
    """Xem thông tin cá nhân sinh viên"""
    try:
        student = StudentProfile.objects.select_related(
            'class_name', 'advisor'
        ).get(email=request.user.email)
        
        context = {
            'student': student,
            'pending_appeals': student.get_pending_appeals()[:5],
            'current_score': student.current_semester_score,
            'score_average': student.score_average
        }
        return render(request, 'student/profile/view.html', context)
        
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('student:dashboard')

@login_required
def profile_edit(request):
    """Chỉnh sửa thông tin cá nhân"""
    try:
        student = StudentProfile.objects.get(email=request.user.email)
        
        if request.method == 'POST':
            # Cập nhật thông tin có thể thay đổi
            student.phone = request.POST.get('phone', '')
            student.address = request.POST.get('address', '')
            
            # Xử lý avatar nếu có
            if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']
                if avatar.content_type not in ALLOWED_FILE_TYPES:
                    messages.error(request, 'File ảnh không đúng định dạng')
                    return render(request, 'student/profile/edit.html', {'student': student})
                    
                if avatar.size > MAX_FILE_SIZE:
                    messages.error(request, 'File ảnh quá lớn (tối đa 5MB)')
                    return render(request, 'student/profile/edit.html', {'student': student})
                    
                student.avatar = avatar
            
            student.save()
            messages.success(request, 'Đã cập nhật thông tin cá nhân')
            return redirect('student:profile_view')
            
        return render(request, 'student/profile/edit.html', {'student': student})
        
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('student:dashboard')

@login_required
def document_list(request):
    """Xem danh sách tài liệu"""
    try:
        student = StudentProfile.objects.get(email=request.user.email)
        documents = StudentDocument.objects.filter(student=student)
        
        # Phân trang
        paginator = Paginator(documents, 10)
        page = request.GET.get('page')
        documents = paginator.get_page(page)
        
        context = {
            'student': student,
            'documents': documents
        }
        return render(request, 'student/profile/documents.html', context)
        
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('student:dashboard')

@login_required
def document_upload(request):
    """Upload tài liệu mới"""
    try:
        student = StudentProfile.objects.get(email=request.user.email)
        
        if request.method == 'POST':
            document = StudentDocument(
                student=student,
                document_type=request.POST.get('document_type'),
                title=request.POST.get('title'),
                description=request.POST.get('description', '')
            )
            
            if 'file' in request.FILES:
                file = request.FILES['file']
                if file.content_type not in ALLOWED_FILE_TYPES:
                    messages.error(request, 'File không đúng định dạng')
                    return render(request, 'student/profile/document_upload.html')
                    
                if file.size > MAX_FILE_SIZE:
                    messages.error(request, 'File quá lớn (tối đa 5MB)')
                    return render(request, 'student/profile/document_upload.html')
                    
                document.file = file
                document.save()
                messages.success(request, 'Đã upload tài liệu thành công')
                return redirect('student:document_list')
            else:
                messages.error(request, 'Vui lòng chọn file để upload')
                
        return render(request, 'student/profile/document_upload.html')
        
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('student:dashboard')

@login_required
def document_delete(request, document_id):
    """Xóa tài liệu"""
    document = get_object_or_404(StudentDocument, id=document_id)
    
    # Kiểm tra quyền xóa
    if document.student.email != request.user.email:
        messages.error(request, 'Bạn không có quyền xóa tài liệu này')
        return redirect('student:document_list')
    
    document.delete()
    messages.success(request, 'Đã xóa tài liệu')
    return redirect('student:document_list')