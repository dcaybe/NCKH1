from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Avg, Count, Q

from core.common.utils.constants import ALLOWED_FILE_TYPES, MAX_FILE_SIZE
from .models import TeacherReport, ScoreAnalytics
from core.teacher.models import TeacherProfile
from core.student.score.models import ScoreRating

@login_required
def report_list(request):
    """Xem danh sách báo cáo"""
    try:
        teacher = TeacherProfile.objects.get(email=request.user.email)
        reports = TeacherReport.objects.filter(teacher=teacher)
        
        # Lọc theo loại báo cáo
        report_type = request.GET.get('type')
        if report_type:
            reports = reports.filter(report_type=report_type)
            
        # Lọc theo lớp
        class_id = request.GET.get('class_id')
        if class_id:
            reports = reports.filter(class_info__class_id=class_id)
            
        # Phân trang
        paginator = Paginator(reports, 10)
        page = request.GET.get('page')
        reports = paginator.get_page(page)
        
        context = {
            'teacher': teacher,
            'reports': reports,
            'report_types': TeacherReport.REPORT_TYPES,
            'classes': teacher.advised_classes.all()
        }
        return render(request, 'teacher/reports/list.html', context)
        
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('teacher:dashboard')

@login_required
def report_create(request):
    """Tạo báo cáo mới"""
    try:
        teacher = TeacherProfile.objects.get(email=request.user.email)
        
        if request.method == 'POST':
            report = TeacherReport(
                teacher=teacher,
                class_info_id=request.POST.get('class_info'),
                report_type=request.POST.get('report_type'),
                period_type=request.POST.get('period_type'),
                title=request.POST.get('title'),
                content=request.POST.get('content'),
                from_date=request.POST.get('from_date'),
                to_date=request.POST.get('to_date'),
                is_draft=request.POST.get('is_draft') == 'on'
            )
            
            # Xử lý file đính kèm
            attachments = {}
            for file_key in request.FILES:
                file = request.FILES[file_key]
                
                if file.content_type not in ALLOWED_FILE_TYPES:
                    messages.error(
                        request,
                        'File không đúng định dạng. Chỉ chấp nhận ảnh hoặc PDF.'
                    )
                    return render(request, 'teacher/reports/create.html')
                    
                if file.size > MAX_FILE_SIZE:
                    messages.error(
                        request,
                        'File quá lớn. Kích thước tối đa là 5MB.'
                    )
                    return render(request, 'teacher/reports/create.html')
                
                attachments[file_key] = file
            
            report.attachments = attachments
            
            # Tạo dữ liệu phân tích nếu là báo cáo điểm
            if report.report_type == 'score_analysis':
                analytics = ScoreAnalytics.objects.filter(
                    class_info=report.class_info
                ).first()
                if analytics:
                    report.analytics_data = {
                        'total_students': analytics.total_students,
                        'evaluated_students': analytics.evaluated_students,
                        'average_score': analytics.average_score,
                        'score_distribution': analytics.score_distribution,
                        'criteria_analysis': analytics.criteria_analysis,
                        'score_trends': analytics.score_trends
                    }
            
            report.save()
            messages.success(request, 'Đã tạo báo cáo mới')
            return redirect('teacher:report_detail', report_id=report.id)
            
        context = {
            'teacher': teacher,
            'classes': teacher.advised_classes.all(),
            'report_types': TeacherReport.REPORT_TYPES,
            'period_types': TeacherReport.PERIOD_TYPES
        }
        return render(request, 'teacher/reports/create.html', context)
        
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('teacher:dashboard')

@login_required
def report_detail(request, report_id):
    """Xem chi tiết báo cáo"""
    report = get_object_or_404(TeacherReport, id=report_id)
    
    # Kiểm tra quyền truy cập
    if report.teacher.email != request.user.email:
        messages.error(request, 'Bạn không có quyền xem báo cáo này')
        return redirect('teacher:report_list')
    
    context = {
        'report': report,
        'analytics': None
    }
    
    if report.report_type == 'score_analysis':
        context['analytics'] = ScoreAnalytics.objects.filter(
            class_info=report.class_info
        ).first()
    
    return render(request, 'teacher/reports/detail.html', context)

@login_required
def report_edit(request, report_id):
    """Chỉnh sửa báo cáo"""
    report = get_object_or_404(TeacherReport, id=report_id)
    
    # Kiểm tra quyền chỉnh sửa
    if report.teacher.email != request.user.email:
        messages.error(request, 'Bạn không có quyền chỉnh sửa báo cáo này')
        return redirect('teacher:report_list')
    
    if request.method == 'POST':
        report.title = request.POST.get('title')
        report.content = request.POST.get('content')
        report.from_date = request.POST.get('from_date')
        report.to_date = request.POST.get('to_date')
        report.is_draft = request.POST.get('is_draft') == 'on'
        
        # Xử lý file đính kèm mới
        if request.FILES:
            attachments = report.attachments
            for file_key in request.FILES:
                file = request.FILES[file_key]
                
                if file.content_type not in ALLOWED_FILE_TYPES:
                    messages.error(
                        request,
                        'File không đúng định dạng. Chỉ chấp nhận ảnh hoặc PDF.'
                    )
                    return render(
                        request,
                        'teacher/reports/edit.html',
                        {'report': report}
                    )
                    
                if file.size > MAX_FILE_SIZE:
                    messages.error(
                        request,
                        'File quá lớn. Kích thước tối đa là 5MB.'
                    )
                    return render(
                        request,
                        'teacher/reports/edit.html',
                        {'report': report}
                    )
                
                attachments[file_key] = file
            
            report.attachments = attachments
        
        report.save()
        messages.success(request, 'Đã cập nhật báo cáo')
        return redirect('teacher:report_detail', report_id=report.id)
    
    return render(request, 'teacher/reports/edit.html', {'report': report})