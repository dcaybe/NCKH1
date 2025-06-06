from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count, Q

from core.common.utils.constants import ALLOWED_FILE_TYPES, MAX_FILE_SIZE
from .models import ClassInfo, ClassActivity
from core.teacher.models import TeacherProfile
from core.student.profile.models import StudentProfile

@login_required
def class_list(request):
    """Xem danh sách lớp giảng dạy"""
    try:
        teacher = TeacherProfile.objects.get(email=request.user.email)
        classes = ClassInfo.objects.filter(advisor=teacher)
        
        # Lọc theo trạng thái
        status = request.GET.get('status')
        if status:
            classes = classes.filter(is_active=(status == 'active'))
        
        # Lọc theo khoa
        department = request.GET.get('department')
        if department:
            classes = classes.filter(department=department)
            
        # Phân trang
        paginator = Paginator(classes, 10)
        page = request.GET.get('page')
        classes = paginator.get_page(page)
        
        context = {
            'teacher': teacher,
            'classes': classes,
            'departments': ClassInfo.objects.values_list(
                'department', flat=True
            ).distinct()
        }
        return render(request, 'teacher/classes/list.html', context)
        
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('teacher:dashboard')

@login_required
def class_detail(request, class_id):
    """Xem chi tiết lớp học"""
    class_info = get_object_or_404(ClassInfo, class_id=class_id)
    
    # Kiểm tra quyền truy cập
    if class_info.advisor.email != request.user.email:
        messages.error(request, 'Bạn không có quyền xem thông tin này')
        return redirect('teacher:class_list')
    
    # Lấy danh sách sinh viên
    students = StudentProfile.objects.filter(
        class_name=class_info,
        is_active=True
    ).order_by('student_id')
    
    # Lấy các hoạt động gần đây
    recent_activities = ClassActivity.objects.filter(
        class_info=class_info
    ).order_by('-start_date')[:5]
    
    context = {
        'class_info': class_info,
        'students': students,
        'recent_activities': recent_activities,
        'student_count': students.count(),
        'available_slots': class_info.max_students - students.count()
    }
    return render(request, 'teacher/classes/detail.html', context)

@login_required
def class_edit(request, class_id):
    """Chỉnh sửa thông tin lớp học"""
    class_info = get_object_or_404(ClassInfo, class_id=class_id)
    
    # Kiểm tra quyền chỉnh sửa
    if class_info.advisor.email != request.user.email:
        messages.error(request, 'Bạn không có quyền chỉnh sửa thông tin này')
        return redirect('teacher:class_list')
    
    if request.method == 'POST':
        class_info.name = request.POST.get('name')
        class_info.description = request.POST.get('description')
        class_info.max_students = int(request.POST.get('max_students'))
        
        try:
            class_info.full_clean()
            class_info.save()
            messages.success(request, 'Đã cập nhật thông tin lớp học')
            return redirect('teacher:class_detail', class_id=class_id)
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'teacher/classes/edit.html', {'class_info': class_info})

@login_required
def activity_create(request, class_id):
    """Tạo hoạt động mới cho lớp"""
    class_info = get_object_or_404(ClassInfo, class_id=class_id)
    
    # Kiểm tra quyền tạo
    if class_info.advisor.email != request.user.email:
        messages.error(request, 'Bạn không có quyền tạo hoạt động cho lớp này')
        return redirect('teacher:class_list')
    
    if request.method == 'POST':
        activity = ClassActivity(
            class_info=class_info,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            is_required=request.POST.get('is_required') == 'on'
        )
        
        # Xử lý file đính kèm
        attachments = {}
        if 'attachments' in request.FILES:
            files = request.FILES.getlist('attachments')
            for file in files:
                if file.content_type not in ALLOWED_FILE_TYPES:
                    messages.error(
                        request,
                        'File không đúng định dạng. Chỉ chấp nhận ảnh hoặc PDF.'
                    )
                    return render(request, 'teacher/classes/activity_create.html')
                    
                if file.size > MAX_FILE_SIZE:
                    messages.error(
                        request,
                        'File quá lớn. Kích thước tối đa là 5MB.'
                    )
                    return render(request, 'teacher/classes/activity_create.html')
                
                attachments[file.name] = file
        
        activity.attachments = attachments
        
        try:
            activity.full_clean()
            activity.save()
            messages.success(request, 'Đã tạo hoạt động mới')
            return redirect('teacher:class_detail', class_id=class_id)
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'teacher/classes/activity_create.html', {
        'class_info': class_info
    })

@login_required
def activity_list(request, class_id):
    """Xem danh sách hoạt động của lớp"""
    class_info = get_object_or_404(ClassInfo, class_id=class_id)
    
    # Kiểm tra quyền truy cập
    if class_info.advisor.email != request.user.email:
        messages.error(request, 'Bạn không có quyền xem thông tin này')
        return redirect('teacher:class_list')
    
    activities = ClassActivity.objects.filter(class_info=class_info)
    
    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status == 'upcoming':
        activities = activities.filter(end_date__gte=timezone.now().date())
    elif status == 'past':
        activities = activities.filter(end_date__lt=timezone.now().date())
    
    # Phân trang
    paginator = Paginator(activities, 10)
    page = request.GET.get('page')
    activities = paginator.get_page(page)
    
    context = {
        'class_info': class_info,
        'activities': activities
    }
    return render(request, 'teacher/classes/activity_list.html', context)

@login_required
def activity_detail(request, class_id, activity_id):
    """Xem chi tiết hoạt động"""
    activity = get_object_or_404(
        ClassActivity,
        id=activity_id,
        class_info__class_id=class_id
    )
    
    # Kiểm tra quyền truy cập
    if activity.class_info.advisor.email != request.user.email:
        messages.error(request, 'Bạn không có quyền xem thông tin này')
        return redirect('teacher:class_list')
    
    context = {
        'activity': activity,
        'participant_count': activity.participants.count(),
        'class_info': activity.class_info
    }
    return render(request, 'teacher/classes/activity_detail.html', context)