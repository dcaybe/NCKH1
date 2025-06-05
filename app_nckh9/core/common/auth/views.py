from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.decorators import login_required

User = get_user_model()

def login_view(request):
    """Xử lý đăng nhập và điều hướng dựa vào loại người dùng"""
    if request.user.is_authenticated:
        return _redirect_by_user_type(request.user)
            
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return _redirect_by_user_type(user)
        else:
            messages.error(request, 'Username hoặc mật khẩu không đúng')
    
    return render(request, 'common/login.html')

def logout_view(request):
    """Xử lý đăng xuất"""
    logout(request)
    return redirect('login')

def reset_password(request):
    """Xử lý yêu cầu đặt lại mật khẩu"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={
                    'uidb64': uid,
                    'token': token
                })
            )
            
            send_mail(
                subject='Đặt lại mật khẩu - HUMG',
                message=f'Để đặt lại mật khẩu, vui lòng truy cập liên kết sau:\n\n{reset_url}',
                from_email='noreply@humg.edu.vn',
                recipient_list=[email],
                fail_silently=False,
            )
            
            messages.success(
                request,
                'Hướng dẫn đặt lại mật khẩu đã được gửi đến email của bạn.'
            )
            
        except User.DoesNotExist:
            messages.success(
                request,
                'Nếu địa chỉ email này tồn tại trong hệ thống, '
                'bạn sẽ nhận được hướng dẫn đặt lại mật khẩu.'
            )
        
        return redirect('login')
        
    return render(request, 'common/reset_password.html')

def password_reset_confirm(request, uidb64, token):
    """Xử lý xác nhận đặt lại mật khẩu"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                password = request.POST.get('password')
                user.set_password(password)
                user.save()
                messages.success(request, 'Mật khẩu đã được đặt lại thành công')
                return redirect('login')
                
            return render(request, 'common/password_reset_confirm.html')
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Link đặt lại mật khẩu không hợp lệ')
        
    return redirect('login')

def _redirect_by_user_type(user):
    """Helper function để điều hướng dựa vào loại người dùng"""
    if user.is_superuser or user.is_staff:
        return redirect('admin:dashboard')
    try:
        if hasattr(user, 'email'):
            from core.common.base.models import InfoTeacher
            teacher = InfoTeacher.objects.get(emailCoVan=user.email)
            return redirect('teacher:dashboard')
    except InfoTeacher.DoesNotExist:
        return redirect('student:dashboard')