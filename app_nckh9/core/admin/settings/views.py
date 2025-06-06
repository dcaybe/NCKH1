from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from .models import SystemSetting, SettingHistory

def is_admin(user):
    """Kiểm tra user có phải là admin không"""
    return user.is_authenticated and user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def setting_list(request):
    """Xem danh sách cài đặt"""
    settings = SystemSetting.objects.all()
    
    # Lọc theo loại cài đặt
    setting_type = request.GET.get('type')
    if setting_type:
        settings = settings.filter(setting_type=setting_type)
        
    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        settings = settings.filter(is_active=(status == 'active'))
    
    # Phân trang
    paginator = Paginator(settings, 20)
    page = request.GET.get('page')
    settings = paginator.get_page(page)
    
    context = {
        'settings': settings,
        'setting_types': SystemSetting.SETTING_TYPES
    }
    return render(request, 'admin/settings/list.html', context)

@login_required
@user_passes_test(is_admin)
def setting_create(request):
    """Tạo cài đặt mới"""
    if request.method == 'POST':
        key = request.POST.get('key')
        
        # Kiểm tra key đã tồn tại chưa
        if SystemSetting.objects.filter(key=key).exists():
            messages.error(request, 'Key cài đặt đã tồn tại')
            return render(request, 'admin/settings/create.html')
        
        setting = SystemSetting(
            key=key,
            value=request.POST.get('value'),
            setting_type=request.POST.get('setting_type'),
            description=request.POST.get('description', ''),
            is_active=request.POST.get('is_active') == 'on'
        )
        
        try:
            setting.full_clean()
            setting.save()
            
            # Tạo lịch sử
            SettingHistory.objects.create(
                setting=setting,
                old_value={},
                new_value=setting.value,
                changed_by=request.user,
                reason='Tạo cài đặt mới'
            )
            
            messages.success(request, 'Đã tạo cài đặt mới')
            return redirect('admin:setting_detail', setting_id=setting.id)
            
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'admin/settings/create.html', {
        'setting_types': SystemSetting.SETTING_TYPES
    })

@login_required
@user_passes_test(is_admin)
def setting_detail(request, setting_id):
    """Xem chi tiết cài đặt"""
    setting = get_object_or_404(SystemSetting, id=setting_id)
    
    # Lấy lịch sử thay đổi
    history = SettingHistory.objects.filter(
        setting=setting
    ).select_related('changed_by').order_by('-created_at')
    
    context = {
        'setting': setting,
        'history': history
    }
    return render(request, 'admin/settings/detail.html', context)

@login_required
@user_passes_test(is_admin)
def setting_edit(request, setting_id):
    """Chỉnh sửa cài đặt"""
    setting = get_object_or_404(SystemSetting, id=setting_id)
    
    if request.method == 'POST':
        # Lưu giá trị cũ để tạo lịch sử
        old_value = setting.value
        
        # Cập nhật thông tin
        setting.value = request.POST.get('value')
        setting.description = request.POST.get('description', '')
        setting.is_active = request.POST.get('is_active') == 'on'
        
        try:
            setting.full_clean()
            setting.save()
            
            # Tạo lịch sử nếu giá trị thay đổi
            if old_value != setting.value:
                SettingHistory.objects.create(
                    setting=setting,
                    old_value=old_value,
                    new_value=setting.value,
                    changed_by=request.user,
                    reason=request.POST.get('reason', '')
                )
            
            messages.success(request, 'Đã cập nhật cài đặt')
            return redirect('admin:setting_detail', setting_id=setting.id)
            
        except Exception as e:
            messages.error(request, str(e))
    
    return render(request, 'admin/settings/edit.html', {'setting': setting})

@login_required
@user_passes_test(is_admin)
def setting_history(request, setting_id):
    """Xem lịch sử thay đổi cài đặt"""
    setting = get_object_or_404(SystemSetting, id=setting_id)
    history = SettingHistory.objects.filter(setting=setting)
    
    # Lọc theo khoảng thời gian
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    if from_date and to_date:
        history = history.filter(
            created_at__range=[from_date, to_date]
        )
    
    # Lọc theo người thay đổi
    changed_by = request.GET.get('changed_by')
    if changed_by:
        history = history.filter(changed_by__username=changed_by)
    
    # Phân trang
    paginator = Paginator(history, 20)
    page = request.GET.get('page')
    history = paginator.get_page(page)
    
    context = {
        'setting': setting,
        'history': history
    }
    return render(request, 'admin/settings/history.html', context)