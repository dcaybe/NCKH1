from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q

from core.common.utils.constants import (
    ALLOWED_FILE_TYPES,
    MAX_FILE_SIZE,
    USER_STATUS_ACTIVE
)
from .models import CustomUser, UserActivity, UserPermission

def is_admin(user):
    """Kiểm tra user có phải là admin không"""
    return user.is_authenticated and user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """Xem danh sách người dùng"""
    users = CustomUser.objects.all()
    
    # Tìm kiếm
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Lọc theo loại tài khoản
    user_type = request.GET.get('type')
    if user_type:
        users = users.filter(user_type=user_type)
        
    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        users = users.filter(is_active=(status == 'active'))
    
    # Phân trang
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'user_types': CustomUser.USER_TYPES,
        'search_term': search
    }
    return render(request, 'admin/users/list.html', context)

@login_required
@user_passes_test(is_admin)
def user_create(request):
    """Tạo người dùng mới"""
    if request.method == 'POST':
        # Kiểm tra username và email đã tồn tại chưa
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username đã tồn tại')
            return render(request, 'admin/users/create.html')
            
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email đã tồn tại')
            return render(request, 'admin/users/create.html')
        
        # Tạo user mới
        user = CustomUser(
            username=username,
            email=email,
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            user_type=request.POST.get('user_type'),
            phone=request.POST.get('phone', ''),
            is_active=request.POST.get('is_active') == 'on'
        )
        
        password = request.POST.get('password')
        user.set_password(password)
        user.save()
        
        # Tạo log
        UserActivity.objects.create(
            user=request.user,
            activity_type='other',
            description=f'Tạo người dùng mới: {user.username}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        messages.success(request, 'Đã tạo người dùng thành công')
        return redirect('admin:user_detail', user_id=user.id)
        
    return render(request, 'admin/users/create.html', {
        'user_types': CustomUser.USER_TYPES
    })

@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    """Xem chi tiết người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Lấy lịch sử hoạt động gần đây
    activities = UserActivity.objects.filter(
        user=user
    ).order_by('-created_at')[:10]
    
    # Lấy danh sách quyền
    permissions = UserPermission.objects.filter(user=user)
    
    context = {
        'user_detail': user,
        'activities': activities,
        'permissions': permissions
    }
    return render(request, 'admin/users/detail.html', context)

@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    """Chỉnh sửa thông tin người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        # Kiểm tra email mới có trùng không
        new_email = request.POST.get('email')
        if new_email != user.email:
            if CustomUser.objects.filter(email=new_email).exists():
                messages.error(request, 'Email đã tồn tại')
                return render(request, 'admin/users/edit.html', {'user': user})
        
        # Cập nhật thông tin
        user.email = new_email
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.phone = request.POST.get('phone', '')
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Đổi mật khẩu nếu có
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
            user.password_changed_at = timezone.now()
        
        user.save()
        
        # Tạo log
        UserActivity.objects.create(
            user=request.user,
            activity_type='profile_update',
            description=f'Cập nhật thông tin người dùng: {user.username}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        messages.success(request, 'Đã cập nhật thông tin người dùng')
        return redirect('admin:user_detail', user_id=user.id)
    
    return render(request, 'admin/users/edit.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def user_permissions(request, user_id):
    """Quản lý quyền của người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        permission_code = request.POST.get('permission')
        action = request.POST.get('action')
        
        if action == 'grant':
            # Cấp quyền mới
            permission = UserPermission(
                user=user,
                codename=permission_code,
                module=request.POST.get('module'),
                description=request.POST.get('description', ''),
                granted_by=request.user
            )
            
            # Thêm thời hạn nếu có
            expires_at = request.POST.get('expires_at')
            if expires_at:
                permission.expires_at = expires_at
                
            permission.save()
            
            messages.success(
                request,
                f'Đã cấp quyền {permission_code} cho {user.username}'
            )
            
        elif action == 'revoke':
            # Thu hồi quyền
            permission = get_object_or_404(
                UserPermission,
                user=user,
                codename=permission_code
            )
            permission.delete()
            
            messages.success(
                request,
                f'Đã thu hồi quyền {permission_code} của {user.username}'
            )
    
    # Lấy danh sách quyền hiện tại
    permissions = UserPermission.objects.filter(user=user)
    
    context = {
        'user': user,
        'permissions': permissions,
        'available_modules': ['student', 'teacher', 'admin']
    }
    return render(request, 'admin/users/permissions.html', context)

@login_required
@user_passes_test(is_admin)
def user_activity(request, user_id):
    """Xem lịch sử hoạt động của người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    activities = UserActivity.objects.filter(user=user)
    
    # Lọc theo loại hoạt động
    activity_type = request.GET.get('type')
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    
    # Lọc theo khoảng thời gian
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    if from_date and to_date:
        activities = activities.filter(
            created_at__range=[from_date, to_date]
        )
    
    # Phân trang
    paginator = Paginator(activities, 20)
    page = request.GET.get('page')
    activities = paginator.get_page(page)
    
    context = {
        'user': user,
        'activities': activities,
        'activity_types': UserActivity.ACTIVITY_TYPES
    }
    return render(request, 'admin/users/activity.html', context)