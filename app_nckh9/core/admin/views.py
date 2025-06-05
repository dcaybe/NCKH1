from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.utils import timezone

from .users.models import CustomUser, UserActivity
from .settings.models import SystemSetting
from core.student.score.models import ScoreRating
from core.student.appeals.models import Appeal

def is_admin(user):
    """Kiểm tra user có phải là admin không"""
    return user.is_authenticated and user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Dashboard cho admin"""
    # Thống kê người dùng
    user_stats = {
        'total_users': CustomUser.objects.count(),
        'active_users': CustomUser.objects.filter(is_active=True).count(),
        'user_types': CustomUser.objects.values('user_type').annotate(
            count=Count('id')
        )
    }
    
    # Thống kê điểm rèn luyện
    current_semester = SystemSetting.objects.get(
        key='current_semester'
    ).value['semester_id']
    
    score_stats = {
        'total_scores': ScoreRating.objects.filter(
            semester_id=current_semester
        ).count(),
        'pending_scores': ScoreRating.objects.filter(
            semester_id=current_semester,
            is_approved=False
        ).count(),
        'score_distribution': ScoreRating.objects.filter(
            semester_id=current_semester
        ).values('classification').annotate(count=Count('id'))
    }
    
    # Thống kê khiếu nại
    appeal_stats = {
        'total_appeals': Appeal.objects.filter(
            semester_id=current_semester
        ).count(),
        'pending_appeals': Appeal.objects.filter(
            semester_id=current_semester,
            status='pending'
        ).count(),
        'appeal_types': Appeal.objects.filter(
            semester_id=current_semester
        ).values('appeal_type').annotate(count=Count('id'))
    }
    
    # Hoạt động gần đây
    recent_activities = UserActivity.objects.select_related(
        'user'
    ).order_by('-created_at')[:10]
    
    # Cài đặt hệ thống quan trọng
    system_settings = SystemSetting.objects.filter(
        setting_type='general',
        is_active=True
    )
    
    context = {
        'user_stats': user_stats,
        'score_stats': score_stats,
        'appeal_stats': appeal_stats,
        'recent_activities': recent_activities,
        'system_settings': system_settings,
        'current_time': timezone.now()
    }
    return render(request, 'admin/dashboard.html', context)