import os
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from app_nckh9.models import *
from django.db.models import Count, Q, F, Avg, Case, When, IntegerField, Max
from django.db.models.functions import Coalesce
from app_nckh9.forms import *

User = get_user_model()
import json
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    ScoreSerializer, AppealSerializer, NotificationSerializer
)
from .auth_serializers import (
    CustomTokenObtainPairSerializer, UserSerializer
)
from .export_serializers import (
    ExportDataSerializer, SyncDataSerializer,
    ExportProgressSerializer, SyncProgressSerializer
)
from celery import shared_task

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_api(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Đăng xuất thành công'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'error': 'Token không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

# Authentication Views
def login_view(request):
    # Nếu user đã đăng nhập, redirect dựa vào user type
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('app_nckh9:admin_dashboard')
        try:
            if hasattr(request.user, 'email'):
                teacher = InfoTeacher.objects.get(emailCoVan=request.user.email)
                return redirect('app_nckh9:teacher_dashboard')
        except InfoTeacher.DoesNotExist:
            return redirect('app_nckh9:student_dashboard')
            
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Sau khi login thành công, redirect dựa vào user type
            if user.is_superuser or user.is_staff:
                return redirect('app_nckh9:admin_dashboard')
            try:
                if hasattr(user, 'email'):
                    teacher = InfoTeacher.objects.get(emailCoVan=user.email)
                    return redirect('app_nckh9:teacher_dashboard')
            except InfoTeacher.DoesNotExist:
                return redirect('app_nckh9:student_dashboard')
        else:
            messages.error(request, 'Username hoặc mật khẩu không đúng')
    
    return render(request, 'homepage/index.html')

def logout_view(request):
    logout(request)
    return redirect('app_nckh9:login')


def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('app_nckh9:password_reset_confirm', kwargs={
                    'uidb64': uid,
                    'token': token
                })
            )
            
            # Send email
            send_mail(
                subject='Đặt lại mật khẩu - HUMG',
                message=f'Để đặt lại mật khẩu, vui lòng truy cập liên kết sau:\n\n{reset_url}\n\n'
                       f'Nếu bạn không yêu cầu đặt lại mật khẩu, hãy bỏ qua email này.',
                from_email='noreply@humg.edu.vn',
                recipient_list=[email],
                fail_silently=False,
            )
            
            messages.success(
                request,
                'Hướng dẫn đặt lại mật khẩu đã được gửi đến email của bạn. '
                'Vui lòng kiểm tra hộp thư.'
            )
            
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist
            messages.success(
                request,
                'Nếu địa chỉ email này tồn tại trong hệ thống, '
                'bạn sẽ nhận được hướng dẫn đặt lại mật khẩu.'
            )
        except Exception as e:
            messages.error(
                request,
                'Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau.'
            )
        
        return redirect('app_nckh9:login')
        
    return render(request, 'homepage/reset_password.html')






@login_required
def student_score_rating(request):
    user = request.user
    try:
        student = InfoStudent.objects.get(emailSV=user.email)
        
        if request.method == 'POST':
            # Lưu thông tin đánh giá
            score = SinhVienTDG (
                maSV=student.maSV,
                tenSV=student.tenSV,
                lopSV=student.lop_hoc.ma_lop,
                dob=student.dob,
                khoaSV=student.khoaSV,
                khoaHoc=student.khoaHoc,
                
                # Điểm học tập
                kqHocTap=int(request.POST.get('kqHocTap', 0)),
                diemNCKH=int(request.POST.get('diemNCKH', 0)),
                # koDungPhao=True,  
                # koDungPhao = request.POST.get('koDungPhao') == "True",
                koDungPhao='koDungPhao' in request.POST and '3' in request.POST.getlist('koDungPhao'),

                # koDiHocMuon=True, 
                # koDiHocMuon = request.POST.get('koDungPhao') == "True",
                koDiHocMuon='koDiHocMuon' in request.POST and '2' in request.POST.getlist('koDiHocMuon'),
                

                boThiOlympic='penalty' in request.POST and '-15' in request.POST.getlist('penalty'),
                tronHoc='penalty' in request.POST and '-2' in request.POST.getlist('penalty'),
                
                # Điểm nội quy
                koVPKL='koVPKL' in request.POST and '10' in request.POST.getlist('koVPKL'),
                diemCDSV=int(request.POST.get('diemCDSV', 0)),
                koThamgiaDaydu='koThamgiaDaydu' in request.POST and '-10' in request.POST.getlist('koThamgiaDaydu'),
                koDeoTheSV='koDeoTheSV' in request.POST and '-5' in request.POST.getlist('koDeoTheSV'),
                koSHL='koSHL' in request.POST and '-5' in request.POST.getlist('koSHL'),
                dongHPmuon='dongHPmuon' in request.POST and '-10' in request.POST.getlist('dongHPmuon'),
                
                # Điểm hoạt động
                thamgiaDayDu='thamgiaDayDu' in request.POST and '13' in request.POST.getlist('thamgiaDayDu'),
                thanhtichHoatDong=sum(int(x) for x in request.POST.getlist('thanhtichHoatDong', [])),
                thamgiaTVTS='thamgiaTVTS' in request.POST and '2' in request.POST.getlist('thamgiaTVTS'),
                koThamgiaDaydu2='koThamgiaDaydu2' in request.POST and '-5' in request.POST.getlist('koThamgiaDaydu2'),
                viphamVanHoaSV='viphamVanHoaSV' in request.POST and '-5' in request.POST.getlist('viphamVanHoaSV'),
                
                # Điểm công dân
                chaphanhDang='chaphanhDang' in request.POST and '10' in request.POST.getlist('chaphanhDang'),
                giupdoCongDong='giupdoCongDong' in request.POST and '5' in request.POST.getlist('giupdoCongDong'),
                gayMatDoanKet='gayMatDoanKet' in request.POST and '-5' in request.POST.getlist('gayMatDoanKet'),
                dongBHYTmuon='dongBHYTmuon' in request.POST and '-20' in request.POST.getlist('dongBHYTmuon'),
                
                # Điểm cán bộ lớp
                thanhvienBCS=sum(int(x) for x in request.POST.getlist('thanhvienBCS', [])),
                caccapKhenThuong='caccapKhenThuong' in request.POST and '3' in request.POST.getlist('caccapKhenThuong'),
                BCSvotrachnghiem='BCSvotrachnghiem' in request.POST and '-5' in request.POST.getlist('BCSvotrachnghiem'),
                
                # Minh chứng và ghi chú
                ghichu1=request.POST.get('ghichu1', ''),
                ghichu2=request.POST.get('ghichu2', ''),
                ghichu3=request.POST.get('ghichu3', ''),
                ghichu4=request.POST.get('ghichu4', ''),
                ghichu5=request.POST.get('ghichu5', ''),
                ghichu6=request.POST.get('ghichu6', ''),
                ghichu7=request.POST.get('ghichu7', ''),
                ghichu8=request.POST.get('ghichu8', ''),
            )

            # Xử lý file minh chứng
            # Xử lý file minh chứng
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
            max_size = 5 * 1024 * 1024  # 5MB

            for i in range(1, 11):
                file_key = f'anhminhchung{i}'
                if file_key in request.FILES:
                    file = request.FILES[file_key]

                    # Kiểm tra định dạng file
                    if file.content_type not in allowed_types:
                        messages.error(request, f'File {file_key} không đúng định dạng. Chỉ chấp nhận ảnh hoặc PDF.')
                        return render(request, 'students/score_rating.html', {'student': student})

                    # Kiểm tra kích thước file
                    if file.size > max_size:
                        messages.error(request, f'File {file_key} quá lớn. Kích thước tối đa là 5MB.')
                        return render(request, 'students/score_rating.html', {'student': student})

                    # Lưu file hợp lệ
                    setattr(score, file_key, file)
                    
            # Tính tổng điểm
            total = (
                int(score.kqHocTap) + int(score.diemNCKH) +
                (3 if score.koDungPhao else 0) +
                (2 if score.koDiHocMuon else 0) +
                (-15 if score.boThiOlympic else 0) +
                (-2 if score.tronHoc else 0) +
                (10 if score.koVPKL else 0) +
                int(score.diemCDSV) +
                (-10 if score.koThamgiaDaydu else 0) +
                (-5 if score.koDeoTheSV else 0) +
                (-5 if score.koSHL else 0) +
                (-10 if score.dongHPmuon else 0) +
                (13 if score.thamgiaDayDu else 0) +
                int(score.thanhtichHoatDong) +
                (2 if score.thamgiaTVTS else 0) +
                (-5 if score.koThamgiaDaydu2 else 0) +
                (-5 if score.viphamVanHoaSV else 0) +
                (10 if score.chaphanhDang else 0) +
                (5 if score.giupdoCongDong else 0) +
                (-5 if score.gayMatDoanKet else 0) +
                (-20 if score.dongBHYTmuon else 0) +
                int(score.thanhvienBCS) +
                (3 if score.caccapKhenThuong else 0) +
                (-5 if score.BCSvotrachnghiem else 0)
            )

            score.drl_tongket = max(0, min(100, total))  # Giới hạn trong khoảng 0-100
            
            # Xếp loại
            if score.drl_tongket >= 90:
                score.xepLoai = "Xuất sắc"
            elif score.drl_tongket >= 80:
                score.xepLoai = "Tốt"
            elif score.drl_tongket >= 65:
                score.xepLoai = "Khá"
            elif score.drl_tongket >= 50:
                score.xepLoai = "Trung bình"
            elif score.drl_tongket >= 35:
                score.xepLoai = "Yếu"
            else:
                score.xepLoai = "Kém"
            # lưu hoạt động
            HistoryActive.objects.create(
                maSV = student.maSV,
                time = timezone.now(),
                name = 'Chấm DRL',
                action = 'Chấm DRL',
                status = 'Chưa xem',
                description = 'Chấm điểm rèn luyện học kì 1',
                device = 'Chrome / Windows',
                ip = '192.168.1.100',
            )
            score.save()
            messages.success(request, f'Đã lưu điểm rèn luyện. Tổng điểm: {score.drl_tongket}, Xếp loại: {score.xepLoai}')
            return redirect('app_nckh9:student_dashboard')
            

        context = {
            'student': student,
            'today_date': timezone.now().strftime("%d/%m/%Y")
        }
        return render(request, 'students/score_rating.html', context)
    except InfoStudent.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('app_nckh9:student_dashboard')
@login_required
def view_score_rating(request):
    try:




        
        student = InfoStudent.objects.get(maSV = '2221050508')
        # Lấy tất cả điểm rèn luyện của sinh viên, sắp xếp theo thời gian tạo mới nhất
        scores = SinhVienTDG.objects.all()  # Giả sử id tăng dần theo thời gian tạo
        
        context = {
            'student': student,
            'scores': scores
        }
        return render(request, 'students/view_score_rating.html', context)
    except InfoStudent.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('app_nckh9:student_dashboard')

@login_required
def add_sinhvien_tdg(request):
    if request.method == 'POST':
        try:
            # Chuyển đổi dữ liệu form thành từng field riêng biệt
            ma_sv = request.POST.get('maSV')
            ten_sv = request.POST.get('tenSV')
            lop_sv = request.POST.get('lopSV')
            dob = request.POST.get('dob')
            khoa_sv = request.POST.get('khoaSV')
            khoa_hoc = int(request.POST.get('khoaHoc'))

            # Tạo instance mới của SinhVienTDG
            score = SinhVienTDG.objects.create(
                maSV=ma_sv,
                tenSV=ten_sv,
                lopSV=lop_sv,
                dob=dob,
                khoaSV=khoa_sv,
                khoaHoc=khoa_hoc,
                
                # Điểm học tập
                kqHocTap=int(request.POST.get('kqHocTap', 0)),
                diemNCKH=int(request.POST.get('diemNCKH', 0)),
                koDungPhao=request.POST.get('koDungPhao') == 'on',
                koDiHocMuon=request.POST.get('koDiHocMuon') == 'on',
                boThiOlympic=False,
                tronHoc=False,
                
                # Điểm nội quy
                koVPKL=request.POST.get('koVPKL') == 'on',
                diemCDSV=int(request.POST.get('diemCDSV', 0)),
                koThamgiaDaydu=False,
                koDeoTheSV=False,
                koSHL=False,
                dongHPmuon=False,
                
                # Điểm hoạt động
                thamgiaDayDu=request.POST.get('thamgiaDayDu') == 'on',
                thanhtichHoatDong=int(request.POST.get('thanhtichHoatDong', 0)),
                thamgiaTVTS=False,
                koThamgiaDaydu2=False,
                viphamVanHoaSV=False,
                
                # Điểm công dân
                chaphanhDang=True,
                giupdoCongDong=False,
                gayMatDoanKet=False,
                dongBHYTmuon=False,
                
                # Điểm cán bộ lớp
                thanhvienBCS=0,
                caccapKhenThuong=False,
                BCSvotrachnghiem=False,
                
                # Ghi chú
                ghichu1=request.POST.get('ghichu1', ''),
                ghichu2=request.POST.get('ghichu2', ''),
                ghichu3=request.POST.get('ghichu3', ''),
                ghichu4=request.POST.get('ghichu4', ''),
                ghichu5=request.POST.get('ghichu5', ''),
                ghichu6=request.POST.get('ghichu6', ''),
                ghichu7=request.POST.get('ghichu7', ''),
                ghichu8=request.POST.get('ghichu8', '')
            )

            # Xử lý file minh chứng
            if 'anhminhchung1' in request.FILES:
                score.anhminhchung1 = request.FILES['anhminhchung1']
            if 'anhminhchung2' in request.FILES:
                score.anhminhchung2 = request.FILES['anhminhchung2']
            if 'anhminhchung3' in request.FILES:
                score.anhminhchung3 = request.FILES['anhminhchung3']
            if 'anhminhchung4' in request.FILES:
                score.anhminhchung4 = request.FILES['anhminhchung4']
            if 'anhminhchung5' in request.FILES:
                score.anhminhchung5 = request.FILES['anhminhchung5']
            if 'anhminhchung6' in request.FILES:
                score.anhminhchung6 = request.FILES['anhminhchung6']
            if 'anhminhchung7' in request.FILES:
                score.anhminhchung7 = request.FILES['anhminhchung7']

            # Tính tổng điểm
            total = (
                int(score.kqHocTap) + int(score.diemNCKH) +
                (3 if score.koDungPhao else 0) +
                (2 if score.koDiHocMuon else 0) +
                (-15 if score.boThiOlympic else 0) +
                (-2 if score.tronHoc else 0) +
                (10 if score.koVPKL else 0) +
                int(score.diemCDSV) +
                (-10 if score.koThamgiaDaydu else 0) +
                (-5 if score.koDeoTheSV else 0) +
                (-5 if score.koSHL else 0) +
                (-10 if score.dongHPmuon else 0) +
                (13 if score.thamgiaDayDu else 0) +
                int(score.thanhtichHoatDong) +
                (2 if score.thamgiaTVTS else 0) +
                (-5 if score.koThamgiaDaydu2 else 0) +
                (-5 if score.viphamVanHoaSV else 0) +
                (10 if score.chaphanhDang else 0) +
                (5 if score.giupdoCongDong else 0) +
                (-5 if score.gayMatDoanKet else 0) +
                (-20 if score.dongBHYTmuon else 0) +
                int(score.thanhvienBCS) +
                (3 if score.caccapKhenThuong else 0) +
                (-5 if score.BCSvotrachnghiem else 0)
            )

            score.drl_tongket = max(0, min(100, total))
            
            # Xếp loại
            if score.drl_tongket >= 90:
                score.xepLoai = "Xuất sắc"
            elif score.drl_tongket >= 80:
                score.xepLoai = "Tốt"
            elif score.drl_tongket >= 65:
                score.xepLoai = "Khá"
            elif score.drl_tongket >= 50:
                score.xepLoai = "Trung bình"
            elif score.drl_tongket >= 35:
                score.xepLoai = "Yếu"
            else:
                score.xepLoai = "Kém"

            score.save()
            messages.success(request, f'Đã thêm điểm rèn luyện cho sinh viên {score.tenSV}. Tổng điểm: {score.drl_tongket}, Xếp loại: {score.xepLoai}')
            return redirect('app_nckh9:admin_dashboard')

        except Exception as e:
            messages.error(request, f'Lỗi khi thêm điểm: {str(e)}')
            return redirect('app_nckh9:add_sinhvien_tdg')

    return render(request, 'students/add_sinhvien_tdg.html')



# Admin Views
@login_required
def admin_dashboard(request):
    stats = HomepageManager.objects.first()
    activities = HistoryActive.objects.all().order_by('-time')[:10]  # Lấy 10 hoạt động gần nhất
    
    context = {
        'stats': stats,
        'activities': activities,
        'user': request.user,
        'today_date': timezone.now().strftime("%d/%m/%Y")
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def admin_user_management(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        user = AdminManage.objects.get(id=user_id)
        
        if action == 'activate':
            user.status = 'active'
        elif action == 'deactivate':
            user.status = 'inactive'
            
        user.save()
        return JsonResponse({'status': 'success'})
    
    users = AdminManage.objects.all()
    context = {'users': users}
    return render(request, 'admin/user-management.html', context)

def create_default_rules():
    """Tạo các quy tắc chấm điểm mặc định dựa trên dữ liệu từ trang scoring-rules.html"""
    default_rules = [
        # I. Ý thức và kết quả học tập (0-30 điểm)
        {'section': 'ythuc_hoctap', 'sub_section': 'Kết quả học tập', 'rule_name': 'Điểm TBCHT ≥ 3,6', 'point_type': 'cong', 'points': '+20', 'max_points': 20, 'order': 1},
        {'section': 'ythuc_hoctap', 'sub_section': 'Kết quả học tập', 'rule_name': 'Điểm TBCHT từ 3,2 đến 3,59', 'point_type': 'cong', 'points': '+18', 'max_points': 18, 'order': 2},
        {'section': 'ythuc_hoctap', 'sub_section': 'Kết quả học tập', 'rule_name': 'Điểm TBCHT từ 2,5 đến 3,19', 'point_type': 'cong', 'points': '+16', 'max_points': 16, 'order': 3},
        {'section': 'ythuc_hoctap', 'sub_section': 'Kết quả học tập', 'rule_name': 'Điểm TBCHT từ 2,0 đến 2,49', 'point_type': 'cong', 'points': '+12', 'max_points': 12, 'order': 4},
        {'section': 'ythuc_hoctap', 'sub_section': 'Kết quả học tập', 'rule_name': 'Điểm TBCHT từ 1,5 đến 1,99', 'point_type': 'cong', 'points': '+10', 'max_points': 10, 'order': 5},
        {'section': 'ythuc_hoctap', 'sub_section': 'Kết quả học tập', 'rule_name': 'Điểm TBCHT từ 1,0 đến 1,49', 'point_type': 'cong', 'points': '+8', 'max_points': 8, 'order': 6},
        
        {'section': 'ythuc_hoctap', 'sub_section': 'Nghiên cứu khoa học, thi Olympic', 'rule_name': 'Đạt giải NCKH cấp Bộ và giải tương đương tối đa', 'point_type': 'cong', 'points': '+8', 'max_points': 8, 'order': 7, 'note': 'Cộng điểm thưởng theo QĐ số 2311/QĐ-MĐC ngày 25/12/2023 về KHCN, sinh viên được cộng dồn điểm thưởng'},
        {'section': 'ythuc_hoctap', 'sub_section': 'Nghiên cứu khoa học, thi Olympic', 'rule_name': 'Đạt giải NCKH cấp Trường, Tiểu ban chuyên môn tối đa', 'point_type': 'cong', 'points': '+6', 'max_points': 6, 'order': 8},
        {'section': 'ythuc_hoctap', 'sub_section': 'Nghiên cứu khoa học, thi Olympic', 'rule_name': 'Đạt giải NCKH khác tối đa', 'point_type': 'cong', 'points': '+6', 'max_points': 6, 'order': 9},
        {'section': 'ythuc_hoctap', 'sub_section': 'Nghiên cứu khoa học, thi Olympic', 'rule_name': 'Đạt giải Olympic cấp Quốc gia tối đa', 'point_type': 'cong', 'points': '+10', 'max_points': 10, 'order': 10},
        {'section': 'ythuc_hoctap', 'sub_section': 'Nghiên cứu khoa học, thi Olympic', 'rule_name': 'Tham gia Olympic cấp Quốc gia tối đa', 'point_type': 'cong', 'points': '+6', 'max_points': 6, 'order': 11},
        {'section': 'ythuc_hoctap', 'sub_section': 'Nghiên cứu khoa học, thi Olympic', 'rule_name': 'Đạt giải Olympic cấp Trường tối đa', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 12},
        {'section': 'ythuc_hoctap', 'sub_section': 'Nghiên cứu khoa học, thi Olympic', 'rule_name': 'Tham gia Olympic cấp Trường/NCKH cấp Trường', 'point_type': 'cong', 'points': '+2/+3', 'max_points': 3, 'order': 13},
        
        {'section': 'ythuc_hoctap', 'sub_section': 'Việc thực hiện nội quy học tập, quy chế thi, kiểm tra', 'rule_name': 'Không vi phạm quy chế thi, kiểm tra', 'point_type': 'cong', 'points': '+3', 'max_points': 3, 'order': 14},
        {'section': 'ythuc_hoctap', 'sub_section': 'Việc thực hiện nội quy học tập, quy chế thi, kiểm tra', 'rule_name': 'Đi học đầy đủ, đúng giờ', 'point_type': 'cong', 'points': '+2', 'max_points': 2, 'order': 15},
        
        {'section': 'ythuc_hoctap', 'sub_section': 'Phần trừ điểm', 'rule_name': 'Đã đăng ký, nhưng bỏ không tham tham gia nghiên cứu khoa học, thi Olympic, Robocon và các cuộc thi khác tương đương', 'point_type': 'tru', 'points': '-15', 'max_points': 0, 'order': 16},
        {'section': 'ythuc_hoctap', 'sub_section': 'Phần trừ điểm', 'rule_name': 'Không đi học, đi không đúng giờ', 'point_type': 'tru', 'points': '-2/buổi', 'max_points': 0, 'order': 17},
        
        # II. Ý thức chấp hành nội quy, quy chế (0-25 điểm)
        {'section': 'ythuc_kyluat', 'sub_section': 'Phần cộng điểm', 'rule_name': 'Chấp hành tốt nội quy, quy chế của Nhà trường, không vi phạm kỷ luật', 'point_type': 'cong', 'points': '+10', 'max_points': 10, 'order': 1},
        {'section': 'ythuc_kyluat', 'sub_section': 'Phần cộng điểm', 'rule_name': 'Đeo thẻ sinh viên trong khuôn viên trường', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 2},
        {'section': 'ythuc_kyluat', 'sub_section': 'Phần cộng điểm', 'rule_name': 'Tham gia đầy đủ các buổi sinh hoạt lớp, họp, hội nghị, tập huấn và các hoạt động khác khi Nhà trường yêu cầu', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 3},
        {'section': 'ythuc_kyluat', 'sub_section': 'Phần cộng điểm', 'rule_name': 'Đóng học phí đúng hạn', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 4},
        
        {'section': 'ythuc_kyluat', 'sub_section': 'Phần trừ điểm', 'rule_name': 'Vi phạm quy chế, quy định của Nhà trường (có biên bản xử lý)', 'point_type': 'tru', 'points': '-10', 'max_points': 0, 'order': 5},
        {'section': 'ythuc_kyluat', 'sub_section': 'Phần trừ điểm', 'rule_name': 'Không tham gia các buổi sinh hoạt lớp, họp, hội nghị, tập huấn và các hoạt động khác khi Nhà trường yêu cầu', 'point_type': 'tru', 'points': '-5/lần', 'max_points': 0, 'order': 6},
        {'section': 'ythuc_kyluat', 'sub_section': 'Phần trừ điểm', 'rule_name': 'Đóng học phí không đúng hạn', 'point_type': 'tru', 'points': '-5', 'max_points': 0, 'order': 7},
        
        # III. Hoạt động đoàn thể, thể thao (0-20 điểm)
        {'section': 'hoatdong_doanthethechao', 'sub_section': 'Phần cộng điểm', 'rule_name': 'Tham gia đầy đủ các hoạt động, sinh hoạt do Đoàn TN, Hội SV tổ chức', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 1},
        {'section': 'hoatdong_doanthethechao', 'sub_section': 'Phần cộng điểm', 'rule_name': 'Là thành viên đội tuyển thể thao, văn nghệ của Trường, Khoa, Lớp', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 2},
        {'section': 'hoatdong_doanthethechao', 'sub_section': 'Phần cộng điểm', 'rule_name': 'Đạt giải thể thao, văn nghệ cấp Trường trở lên', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 3},
        {'section': 'hoatdong_doanthethechao', 'sub_section': 'Phần cộng điểm', 'rule_name': 'Tham gia các hoạt động tình nguyện (mùa hè xanh, tiếp sức mùa thi...)', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 4},
        
        {'section': 'hoatdong_doanthethechao', 'sub_section': 'Phần trừ điểm', 'rule_name': 'Không tham gia các hoạt động, sinh hoạt do Đoàn TN, Hội SV tổ chức', 'point_type': 'tru', 'points': '-5/lần', 'max_points': 0, 'order': 5},
        
        # IV. Quan hệ cộng đồng (0-15 điểm)
        {'section': 'quanhe_congdong', 'sub_section': 'Phần cộng điểm', 'rule_name': 'Có tinh thần giúp đỡ bạn bè trong học tập, trong cuộc sống', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 1},
        {'section': 'quanhe_congdong', 'sub_section': 'Phần cộng điểm', 'rule_name': 'Tham gia các hoạt động từ thiện, nhân đạo, hiến máu nhân đạo', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 2},
        {'section': 'quanhe_congdong', 'sub_section': 'Phần cộng điểm', 'rule_name': 'Tham gia các hoạt động tuyên truyền, phổ biến chính sách, pháp luật', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 3},
        
        {'section': 'quanhe_congdong', 'sub_section': 'Phần trừ điểm', 'rule_name': 'Gây mất đoàn kết trong tập thể lớp', 'point_type': 'tru', 'points': '-5', 'max_points': 0, 'order': 4},
        {'section': 'quanhe_congdong', 'sub_section': 'Phần trừ điểm', 'rule_name': 'Không đóng BHYT đúng hạn', 'point_type': 'tru', 'points': '-20', 'max_points': 0, 'order': 5},
        
        # V. Phụ trách lớp, đoàn thể (0-10 điểm)
        {'section': 'phutrachlop', 'sub_section': 'Chức vụ và hoàn thành nhiệm vụ', 'rule_name': 'Lớp trưởng, Phó Bí thư Liên chi, Bí thư Chi đoàn', 'point_type': 'cong', 'points': '+7', 'max_points': 7, 'order': 1, 'note': 'Mục này dành cho SV là thành viên Ban cán sự lớp quản lý sinh viên; cán bộ Đoàn TN, Hội SV'},
        {'section': 'phutrachlop', 'sub_section': 'Chức vụ và hoàn thành nhiệm vụ', 'rule_name': 'Lớp phó, Phó Bí thư Chi đoàn, Hội trưởng Hội SV', 'point_type': 'cong', 'points': '+5', 'max_points': 5, 'order': 2},
        
        {'section': 'phutrachlop', 'sub_section': 'Khen thưởng', 'rule_name': 'Được các cấp khen thưởng (có minh chứng kèm theo)', 'point_type': 'cong', 'points': '+3', 'max_points': 3, 'order': 3},
        
        {'section': 'phutrachlop', 'sub_section': 'Phần trừ điểm', 'rule_name': 'Là thành viên Ban cán sự lớp quản lý sinh viên; cán bộ Đoàn TN, Hội SV thiếu trách nhiệm (bị GVCN hoặc cấp có thẩm quyền kỉ luật bằng văn bản)', 'point_type': 'tru', 'points': '-5/lần', 'max_points': 0, 'order': 4}
    ]
    
    # Tạo các quy tắc mặc định
    for rule_data in default_rules:
        Rules.objects.create(**rule_data)

@login_required
def admin_scoring_rules(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update':
            rule_id = request.POST.get('rule_id')
            points = request.POST.get('points')
            
            try:
                rule = Rules.objects.get(id=rule_id)
                rule.points = points
                rule.save()
                messages.success(request, f'Đã cập nhật quy tắc "{rule.rule_name}" thành công')
                return JsonResponse({'status': 'success'})
            except Rules.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Không tìm thấy quy tắc'}, status=404)
        
        elif action == 'create':
            section = request.POST.get('section')
            sub_section = request.POST.get('sub_section')
            rule_name = request.POST.get('rule_name')
            point_type = request.POST.get('point_type')
            points = request.POST.get('points')
            max_points = request.POST.get('max_points', 0)
            note = request.POST.get('note', '')
            
            # Tính thứ tự hiển thị mới
            last_order = Rules.objects.filter(section=section).aggregate(Max('order'))['order__max'] or 0
            
            try:
                rule = Rules.objects.create(
                    section=section,
                    sub_section=sub_section,
                    rule_name=rule_name,
                    point_type=point_type,
                    points=points,
                    max_points=max_points,
                    order=last_order + 1,
                    note=note
                )
                messages.success(request, f'Đã thêm quy tắc mới thành công')
                return JsonResponse({'status': 'success', 'rule_id': rule.id})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
        elif action == 'delete':
            rule_id = request.POST.get('rule_id')
            
            try:
                rule = Rules.objects.get(id=rule_id)
                rule_name = rule.rule_name
                rule.delete()
                messages.success(request, f'Đã xóa quy tắc "{rule_name}" thành công')
                return JsonResponse({'status': 'success'})
            except Rules.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Không tìm thấy quy tắc'}, status=404)
        
        elif action == 'restore_defaults':
            # Xóa tất cả quy tắc hiện tại
            Rules.objects.all().delete()
            
            # Thêm quy tắc mặc định từ dữ liệu ban đầu
            create_default_rules()
            
            messages.success(request, 'Đã khôi phục quy tắc mặc định thành công')
            return JsonResponse({'status': 'success'})
    
    # Lấy tất cả quy tắc và phân nhóm theo section
    rules_by_section = {}
    for rule_type, rule_name in Rules.RULE_TYPES:
        rules_by_section[rule_type] = {
            'name': rule_name,
            'rules': Rules.objects.filter(section=rule_type).order_by('order')
        }
    
    context = {
        'rules_by_section': rules_by_section,
        'rule_types': Rules.RULE_TYPES,
        'point_types': Rules.POINT_TYPES
    }
    
    return render(request, 'admin/scoring-rules.html', context)

@login_required
def admin_backup_restore(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'backup':
            # Implement backup logic
            pass
        elif action == 'restore':
            # Implement restore logic
            pass
    return render(request, 'admin/backup-restore.html')

@login_required
def admin_statistics(request):
    context = {
        'analytics': Analysts2.objects.first()
    }
    return render(request, 'admin/statistics.html', context)

@login_required
def admin_sync(request):
    if request.method == 'POST':
        # Implement sync logic here
        return JsonResponse({'status': 'success'})
    return render(request, 'admin/sync.html')

@login_required
def admin_notifications(request):
    notifications = AdminNotification.objects.all().order_by('-created_at')
    context = {'notifications': notifications}
    return render(request, 'admin/notifications.html', context)

@login_required
def admin_batch_approval(request):
    if request.method == 'POST':
        # Implement batch approval logic here
        return JsonResponse({'status': 'success'})
    
    pending_items = BatchApprovalQueue.objects.filter(status='pending')
    context = {'pending_items': pending_items}
    return render(request, 'admin/batch-approval.html', context)

@login_required
def admin_activity_history(request):
    activities = AdminActivity.objects.all().order_by('-timestamp')
    context = {'activities': activities}
    return render(request, 'admin/activity-history.html', context)

@login_required
def admin_cham_drl(request):
    """
    View để quản lý đợt chấm điểm rèn luyện (ChamDRL)
    """
    if request.method == 'POST':
        # Xử lý thêm mới đợt chấm DRL
        ma_cham_drl = request.POST.get('ma_cham_drl')
        ten_dot_cham = request.POST.get('ten_dot_cham')
        hoc_ky_id = request.POST.get('hoc_ky')
        ngay_gio_bat_dau = request.POST.get('ngay_gio_bat_dau')
        ngay_gio_ket_thuc = request.POST.get('ngay_gio_ket_thuc')
        mo_ta = request.POST.get('mo_ta')
        is_active = request.POST.get('isActive') == 'on'
        
        try:
            hoc_ky = HocKy.objects.get(id=hoc_ky_id)
            
            cham_drl = ChamDRL(
                ma_cham_drl=ma_cham_drl,
                ten_dot_cham=ten_dot_cham,
                hoc_ky=hoc_ky,
                ngay_gio_bat_dau=ngay_gio_bat_dau,
                ngay_gio_ket_thuc=ngay_gio_ket_thuc,
                mo_ta=mo_ta,
                isActive=is_active
            )
            cham_drl.full_clean()  # Validate model
            cham_drl.save()
            messages.success(request, 'Thêm đợt chấm điểm rèn luyện thành công!')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    # Lấy danh sách các đợt chấm DRL và học kỳ
    cham_drl_list = ChamDRL.objects.all().order_by('-created_at')
    hoc_ky_list = HocKy.objects.all().order_by('-nam_hoc', '-hoc_ky')
    
    context = {
        'cham_drl_list': cham_drl_list,
        'hoc_ky_list': hoc_ky_list
    }
    return render(request, 'admin/cham-drl.html', context)

@login_required
def admin_cham_drl_edit(request):
    """
    View để xử lý chỉnh sửa đợt chấm điểm rèn luyện
    """
    if request.method == 'POST':
        cham_drl_id = request.POST.get('id')
        ma_cham_drl = request.POST.get('ma_cham_drl')
        ten_dot_cham = request.POST.get('ten_dot_cham')
        hoc_ky_id = request.POST.get('hoc_ky')
        ngay_gio_bat_dau = request.POST.get('ngay_gio_bat_dau')
        ngay_gio_ket_thuc = request.POST.get('ngay_gio_ket_thuc')
        mo_ta = request.POST.get('mo_ta')
        is_active = request.POST.get('isActive') == 'on'
        
        try:
            cham_drl = ChamDRL.objects.get(id=cham_drl_id)
            hoc_ky = HocKy.objects.get(id=hoc_ky_id)
            
            cham_drl.ma_cham_drl = ma_cham_drl
            cham_drl.ten_dot_cham = ten_dot_cham
            cham_drl.hoc_ky = hoc_ky
            cham_drl.ngay_gio_bat_dau = ngay_gio_bat_dau
            cham_drl.ngay_gio_ket_thuc = ngay_gio_ket_thuc
            cham_drl.mo_ta = mo_ta
            cham_drl.isActive = is_active
            
            cham_drl.full_clean()  # Validate model
            cham_drl.save()
            messages.success(request, 'Cập nhật đợt chấm điểm rèn luyện thành công!')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('app_nckh9:admin_cham_drl')

@login_required
def admin_cham_drl_delete(request):
    """
    View để xử lý xóa đợt chấm điểm rèn luyện
    """
    if request.method == 'POST':
        cham_drl_id = request.POST.get('id')
        
        try:
            cham_drl = ChamDRL.objects.get(id=cham_drl_id)
            cham_drl.delete()
            messages.success(request, 'Xóa đợt chấm điểm rèn luyện thành công!')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('app_nckh9:admin_cham_drl')

@login_required
def admin_cham_drl_toggle_active(request, cham_drl_id):
    """
    View để kích hoạt/hủy kích hoạt đợt chấm điểm rèn luyện
    """
    try:
        cham_drl = ChamDRL.objects.get(id=cham_drl_id)
        cham_drl.isActive = not cham_drl.isActive
        cham_drl.save()
        
        if cham_drl.isActive:
            messages.success(request, f'Đã kích hoạt đợt chấm điểm "{cham_drl.ten_dot_cham}"')
        else:
            messages.info(request, f'Đã hủy kích hoạt đợt chấm điểm "{cham_drl.ten_dot_cham}"')
    except Exception as e:
        messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('app_nckh9:admin_cham_drl')

# AI Assistant Views
@login_required
def chat_view(request):
    if not request.user.is_authenticated:
        return redirect('app_nckh9:login')
    return render(request, 'chat/index.html')

@login_required
def chat_send(request):
    if request.method == 'POST':
        try:
            message = request.POST.get('message')
            chatbot = KairaChatBot.objects.first()
            if not chatbot:
                return JsonResponse({
                    'response': 'Xin lỗi, hệ thống AI đang được bảo trì. Vui lòng thử lại sau.'
                })
            response = chatbot.get_response(message)
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({
                'response': 'Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại.'
            })
    return JsonResponse({'error': 'Invalid request'}, status=400)

# API Views
class ScoreListCreateAPIView(generics.ListCreateAPIView):
    queryset = SinhVienTDG.objects.all()
    serializer_class = ScoreSerializer

class ScoreRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SinhVienTDG.objects.all()
    serializer_class = ScoreSerializer

class AppealListCreateAPIView(generics.ListCreateAPIView):
    queryset = StudentsReport.objects.all()
    serializer_class = AppealSerializer

class AppealRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentsReport.objects.all()
    serializer_class = AppealSerializer

class NotificationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Nofitication.objects.all()
    serializer_class = NotificationSerializer

class NotificationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Nofitication.objects.all()
    serializer_class = NotificationSerializer

@api_view(['POST'])
def mark_notification_as_read(request, pk):
    try:
        notification = Nofitication.objects.get(pk=pk)
        notification.is_read = True
        notification.save()
        return Response({'status': 'success'})
    except Nofitication.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=404)
    

def admin_backup_restore(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_backup':
            # Logic tạo bản sao lưu
            return JsonResponse({'status': 'success', 'message': 'Bản sao lưu đã được tạo thành công!'})
        elif action == 'restore_backup':
            backup_id = request.POST.get('backup_id')
            # Logic khôi phục bản sao lưu
            return JsonResponse({'status': 'success', 'message': f'Khôi phục bản sao lưu {backup_id} thành công!'})
        elif action == 'delete_backup':
            backup_id = request.POST.get('backup_id')
            # Logic xóa bản sao lưu
            return JsonResponse({'status': 'success', 'message': f'Bản sao lưu {backup_id} đã bị xóa!'})
        elif action == 'save_settings':
            frequency = request.POST.get('frequency')
            time = request.POST.get('time')
            max_backups = request.POST.get('max_backups')
            # Logic lưu cài đặt sao lưu tự động
            return JsonResponse({'status': 'success', 'message': 'Cài đặt đã được lưu!'})

    # Dữ liệu giả lập để hiển thị trong giao diện
    backups = [
        {'id': '20240220_153000', 'time': '20/02/2024 15:30', 'type': 'Tự động', 'size': '500 MB', 'status': 'Hoàn thành'},
        {'id': '20240219_120000', 'time': '19/02/2024 12:00', 'type': 'Thủ công', 'size': '450 MB', 'status': 'Hoàn thành'},
    ]
    context = {
        'backups': backups,
        'last_backup': '20/02/2024 15:30',
        'used_space': '2.5 GB',
        'total_backups': len(backups),
    }
    return render(request, 'admin/backup-restore.html', context)


@login_required
def admin_batch_approval(request):
   
    return render(request, 'admin/batch-approval.html')

@login_required
def admin_notifications(request):
   
    return render(request, 'admin/notifications.html')

@login_required
def admin_ai_assistant(request):
   
    return render(request, 'admin/ai-assistant.html')

@login_required
def admin_activity_history(request):
   
    return render(request, 'admin/activity-history.html')

#student clone view




def student_show_point(request):
    sinhvien = InfoStudent.objects.filter(maSV="2221050508").first()
    if not sinhvien:
        messages.error(request, "Không tìm thấy thông tin sinh viên.")
        return redirect('app_nckh9:student_dashboard')
    
    historic_points = []
    trend_labels = []
    trend_scores = []
    
    history = HistoryPoint.objects.filter(maSV="2221050508").first()
    if history:
        for i in range(1, 21):
            score = getattr(history, f"hocky{i}", None)
            if score is not None:
                # Tạo nhãn và điểm cho biểu đồ
                semester_label = f"Học kỳ {i}"
                nam = ((i - 1) // 2) + 1  # Năm học (1-5)
                hk = 1 if i % 2 != 0 else 2  # Học kỳ lẻ (HK1), chẵn (HK2)
                trend_labels.append(f"HK{hk}-N{nam}")
                trend_scores.append(score)  

                # Tạo dữ liệu historic_points
                historic_points.append((semester_label, score))
    current_semester = historic_points[-1] if historic_points else None
        # Sau khi đã tạo historic_points
    avg_score = None
    if historic_points:
        total_score = sum(score for _, score in historic_points)
        avg_score = round(total_score / len(historic_points))  # Làm tròn 2 chữ số thập phân

    return render(request, 'students/show_point.html', {
        'sinhvien': sinhvien,
        'historic_points': historic_points,
        'trend_labels': trend_labels,
        'trend_scores': trend_scores,
        'current_semester': current_semester,
        'avg_score': avg_score
    })




def student_ai_assistant(request):
   
    return render(request, 'students/ai-assistant.html')

# def student_score_rating(request):
#     return render(request, 'students/score_rating.html')

def student_appeal(request):
   
    return render(request,'students/appeal.html')
@login_required
def student_historic_fix(request):
        user = request.user
        student = InfoStudent.objects.get(emailSV = user.email)
        historic_fixs = HistoryActive.objects.filter(maSV = student.maSV)
        context = {
            'student': student,
            'historic_fixs': historic_fixs,
        }
        return render(request,'students/historic_fix.html',context)


# def student_notifications(request):
#     sinhvien = InfoStudent.objects.filter(maSV="2221050508").first()
#     notifications = Notification.objects.all().order_by('-dob')
#     return render(request, 'students/notification.html', {'notifications': notifications, 'sinhvien': sinhvien})

def student_notifications(request):
    sinhvien = InfoStudent.objects.filter(maSV="2221050508").first()
    notifications = Nofitication.objects.all().order_by('-dob')
    return render(request, 'students/notification.html', {'notifications': notifications, 'sinhvien': sinhvien})


def student_rank(request):
    sinhvien = InfoStudent.objects.filter(maSV="2221050508").first()
    rankings = HistoryPoint.objects.filter(hocky1__isnull=False).order_by('-hocky1')
    top3 = rankings[:3]
    others = rankings[3:]
    return render(request, 'students/rank.html', {
        'top3': top3,
        'others': others,
        'sinhvien': sinhvien
    })
# def student_appeal_again(request):
   
#     return render(request,'students/appeal_again.html')
@login_required
def student_appeal_again(request):
    user = request.user
    try:
        student = InfoStudent.objects.get(emailSV=user.email)

        if request.method == 'POST':
            complaint_type = request.POST.get('complaintType')
            reason = request.POST.get('complaintReason')
            semester_id = request.POST.get('semester')
            evidence = request.FILES.getlist('attachment')

            # Validation
            if not all([complaint_type, reason, semester_id]):
                messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc')
                return redirect('app_nckh9:student_appeal_again')

            try:
                semester = HocKy.objects.get(pk=semester_id)
            except HocKy.DoesNotExist:
                messages.error(request, 'Học kỳ không hợp lệ')
                return redirect('app_nckh9:student_appeal_again')

            # File validation
            if evidence:
                for file in evidence:
                    if file.size > 5 * 1024 * 1024:  # 5MB limit
                        messages.error(request, f'File {file.name} vượt quá kích thước cho phép (5MB)')
                        return redirect('app_nckh9:student_appeal_again')
                    
                    ext = file.name.split('.')[-1].lower()
                    if ext not in ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']:
                        messages.error(request, f'File {file.name} không đúng định dạng cho phép')
                        return redirect('app_nckh9:student_appeal_again')

            # Create report
            report = StudentsReport(
                title=f'Khiếu nại điểm - {complaint_type}',
                content=reason,
                student=student,
                semester=semester
            )
            
            if evidence:
                report.evidence = evidence[0]  # Save first file as main evidence
            
            report.save()
            messages.success(request, 'Đơn khiếu nại của bạn đã được gửi thành công!')
            return redirect('app_nckh9:student_dashboard')

        # Lấy danh sách học kỳ
        semesters = HocKy.objects.all().order_by('-nam_hoc', '-hoc_ky')
        context = {
            'student': student,
            'semesters': semesters,
            'max_upload_size': 5  # 5MB
        }
        return render(request, 'students/appeal_again.html', context)

    except InfoStudent.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin sinh viên')
        return redirect('app_nckh9:student_dashboard')
# teacher clone view
@login_required
def teacher_dashboard(request):
    try:
        teacher = InfoTeacher.objects.get(emailCoVan=request.user.email)
        
        # Lấy danh sách sinh viên thuộc lớp của giáo viên
        students = InfoStudent.objects.filter(lop_hoc__giao_vien_chu_nhiem=teacher)
        total_students = students.count()
        
        # Lấy thông tin về đợt chấm DRL hiện tại
        active_cham_drl = ChamDRL.objects.filter(isActive=True).first()
        lopGV = LopHoc.objects.filter(giao_vien_chu_nhiem=teacher)
        pending_scores = SinhVienTDG.objects.filter(
            trangthai=True,
            lopSV__in=lopGV.values_list('ma_lop', flat=True)
        ).values('maSV').distinct().count()
        
        # Lấy thông báo mới nhất
        notifications = PrivateNofitication.objects.all().order_by('-dob')[:1]
        
        # Tính toán thống kê về điểm rèn luyện
        stats = {
            'total_students': total_students,
            'pending_scores': pending_scores,  # Sẽ được cập nhật nếu có dữ liệu
            'avg_score': 0,       # Sẽ được cập nhật nếu có dữ liệu
            'excellent': 0,        # Sinh viên xuất sắc
            'good': 0,             # Sinh viên giỏi
            'average': 0,          # Sinh viên khá
            'below_average': 0     # Sinh viên cần cải thiện
        }
        
        # Nếu có đợt chấm DRL hiện tại, tính toán các thống kê liên quan
        if active_cham_drl:
            # Thời gian còn lại của đợt chấm DRL (tính theo ngày)
            from django.utils import timezone
            now = timezone.now()
            if now < active_cham_drl.ngay_gio_ket_thuc:
                days_remaining = (active_cham_drl.ngay_gio_ket_thuc.date() - now.date()).days
                stats['days_remaining'] = days_remaining
            
            # Thêm thông tin về đợt chấm DRL
            stats['active_cham_drl'] = active_cham_drl
        
        context = {
            'teacher': teacher,
            'students': students,
            'stats': stats,
            'notifications': notifications,
            'active_cham_drl': active_cham_drl
        }
        
        return render(request, 'teacher/dashboard.html', context)
    except InfoTeacher.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('app_nckh9:login')
        
# Export và Sync Data API Endpoints
@api_view(['POST'])
@login_required
def initiate_export(request):
    """Khởi tạo quá trình export data"""
    serializer = ExportDataSerializer(data=request.data)
    if serializer.is_valid():
        task = AsyncExportTask.objects.create(
            format=serializer.validated_data['format'],
            data_type=serializer.validated_data['data_type'],
            start_date=serializer.validated_data.get('start_date'),
            end_date=serializer.validated_data.get('end_date'),
            include_fields=serializer.validated_data.get('include_fields', [])
        )
        # Bắt đầu task export bất đồng bộ
        export_data.delay(task.id)
        return Response({
            'task_id': task.id,
            'message': 'Export đã được khởi tạo'
        }, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@login_required
def export_progress(request, task_id):
    """Kiểm tra tiến trình của export task"""
    try:
        task = AsyncExportTask.objects.get(id=task_id)
        serializer = ExportProgressSerializer(task)
        return Response(serializer.data)
    except AsyncExportTask.DoesNotExist:
        return Response({'error': 'Task không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@login_required
def download_export(request, task_id):
    """Download file đã export"""
    try:
        task = AsyncExportTask.objects.get(id=task_id)
        if task.status != 'completed':
            return Response({'error': 'Export chưa hoàn thành'}, status=status.HTTP_400_BAD_REQUEST)
            
        file_path = task.file_path
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename=export_{task_id}.{task.format}'
            return response
        return Response({'error': 'File không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
    except AsyncExportTask.DoesNotExist:
        return Response({'error': 'Task không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@login_required
def initiate_sync(request):
    """Khởi tạo quá trình sync data"""
    serializer = SyncDataSerializer(data=request.data)
    if serializer.is_valid():
        task = AsyncSyncTask.objects.create(
            sync_type=serializer.validated_data['sync_type'],
            source_system=serializer.validated_data['source_system'],
            data_type=serializer.validated_data['data_type'],
            last_sync_time=serializer.validated_data.get('last_sync_time')
        )
        # Bắt đầu task sync bất đồng bộ
        sync_data.delay(task.id)
        return Response({
            'task_id': task.id,
            'message': 'Sync đã được khởi tạo'
        }, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@login_required
def sync_progress(request, task_id):
    """Kiểm tra tiến trình của sync task"""
    try:
        task = AsyncSyncTask.objects.get(id=task_id)
        serializer = SyncProgressSerializer(task)
        return Response(serializer.data)
    except AsyncSyncTask.DoesNotExist:
        return Response({'error': 'Task không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@login_required
def sync_errors(request, task_id):
    """Lấy danh sách lỗi của sync task"""

def password_reset_confirm(request, uidb64, token):
    try:
        # Get user from uid
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        # Verify token
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                # Get new password
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                
                if password != confirm_password:
                    messages.error(request, 'Mật khẩu không khớp')
                    return render(request, 'homepage/reset_password_confirm.html')
                    
                # Update password
                user.password = make_password(password)
                user.save()
                
                messages.success(request, 'Mật khẩu đã được đặt lại thành công')
                return redirect('app_nckh9:login')
                
            return render(request, 'homepage/reset_password_confirm.html')
            
        messages.error(
            request,
            'Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn'
        )
        return redirect('app_nckh9:reset_password')
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(
            request,
            'Liên kết đặt lại mật khẩu không hợp lệ'
        )
        return redirect('app_nckh9:reset_password')
    try:
        task = AsyncSyncTask.objects.get(id=task_id)
        return Response({
            'errors': task.errors,
            'total_records': task.total_records,
            'failed_records': task.failed_records
        })
    except AsyncSyncTask.DoesNotExist:
        return Response({'error': 'Task không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
    except InfoTeacher.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('app_nckh9:login')
@login_required
def teacher_class_management(request):
    try:
        teacher = InfoTeacher.objects.get(emailCoVan=request.user.email)
    except InfoTeacher.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('app_nckh9:login')
    return render(request,'teacher/class-management.html', {'teacher': teacher})


@login_required
def teacher_activity_history(request):
    try:
        teacher = InfoTeacher.objects.get(emailCoVan=request.user.email)
    except InfoTeacher.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('app_nckh9:login')
    return render(request,'teacher/activity-history.html', {'teacher': teacher})
@login_required
def teacher_notifications(request):
    try:
        teacher = InfoTeacher.objects.get(emailCoVan=request.user.email)
        # Get all private notifications ordered by date (newest first)
        notifications = PrivateNofitication.objects.all().order_by('-dob')
    except InfoTeacher.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('app_nckh9:login')
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        notifications = []
    
    return render(request, 'teacher/notifications.html', {
        'teacher': teacher,
        'notifications': notifications
    })
@login_required
def teacher_ai_assistant(request):
    try:
        teacher = InfoTeacher.objects.get(emailCoVan=request.user.email)
    except InfoTeacher.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('app_nckh9:login')
    return render(request,'teacher/ai-assistant.html', {'teacher': teacher})
@login_required
def teacher_rescore_student(request, maSV):
    # try:
        teacher = InfoTeacher.objects.get(emailCoVan=request.user.email)
        
        try:
            student = SinhVienTDG.objects.get(maSV=maSV, trangthai=False)
        except SinhVienTDG.DoesNotExist:
            messages.error(request, 'Không tìm thấy sinh viên này hoặc sinh viên đã được chấm điểm')
            return redirect('app_nckh9:teacher_score_management')

        if request.method == 'POST':
            # try:
                # Kiểm tra xem đã có bản ghi GVCNDanhGia cho sinh viên này chưa
                # try:
                #     gvcn_danhgia = GVCNDanhGia.objects.get(maSV=maSV)
                # except GVCNDanhGia.DoesNotExist:
                #     # Tạo mới nếu chưa tồn tại
                gvcn_danhgia = GVCNDanhGia()
                
                # Copy student info
                gvcn_danhgia.maSV = student.maSV
                gvcn_danhgia.tenSV = student.tenSV
                gvcn_danhgia.lopSV = student.lopSV
                gvcn_danhgia.dob = student.dob
                gvcn_danhgia.khoaSV = student.khoaSV
                gvcn_danhgia.khoaHoc = student.khoaHoc
                
                # Update scores from form data with safer conversion
                try:
                    gvcn_danhgia.kqHocTap = int(request.POST.get('kqHocTap', 0))
                except (ValueError, TypeError):
                    gvcn_danhgia.kqHocTap = 0
                    
                try:
                    gvcn_danhgia.diemNCKH = int(request.POST.get('diemNCKH', 0))
                except (ValueError, TypeError):
                    gvcn_danhgia.diemNCKH = 0
                    
                try:
                    gvcn_danhgia.diemCDSV = int(request.POST.get('diemCDSV', 0))
                except (ValueError, TypeError):
                    gvcn_danhgia.diemCDSV = 0
                    
                try:
                    gvcn_danhgia.thanhtichHoatDong = int(request.POST.get('thanhtichHoatDong', 0))
                except (ValueError, TypeError):
                    gvcn_danhgia.thanhtichHoatDong = 0
                    
                try:
                    gvcn_danhgia.thanhvienBCS = int(request.POST.get('thanhvienBCS', 0))
                except (ValueError, TypeError):
                    gvcn_danhgia.thanhvienBCS = 0
                
                # Update boolean fields
                boolean_fields = [
                    'koDungPhao', 'koDiHocMuon', 'boThiOlympic', 'tronHoc', 'koVPKL',
                    'koThamgiaDaydu', 'koDeoTheSV', 'koSHL', 'dongHPmuon', 'thamgiaDayDu',
                    'thamgiaTVTS', 'koThamgiaDaydu2', 'viphamVanHoaSV', 'chaphanhDang',
                    'giupdoCongDong', 'gayMatDoanKet', 'dongBHYTmuon', 'caccapKhenThuong',
                    'BCSvotrachnghiem'
                ]
                
                # Đặt tất cả các trường boolean thành False trước
                for field in boolean_fields:
                    setattr(gvcn_danhgia, field, False)
                
                # Sau đó cập nhật các trường được chọn thành True
                for field in boolean_fields:
                    if field in request.POST:
                        setattr(gvcn_danhgia, field, True)
                
                # Tính điểm từ các trường boolean
                boolean_points = (
                    (3 if gvcn_danhgia.koDungPhao else 0) +
                    (2 if gvcn_danhgia.koDiHocMuon else 0) +
                    (-15 if gvcn_danhgia.boThiOlympic else 0) +
                    (-2 if gvcn_danhgia.tronHoc else 0) +
                    (10 if gvcn_danhgia.koVPKL else 0) +
                    
                    (-10 if gvcn_danhgia.koThamgiaDaydu else 0) +
                    (-5 if gvcn_danhgia.koDeoTheSV else 0) +
                    (-5 if gvcn_danhgia.koSHL else 0) +
                    (-10 if gvcn_danhgia.dongHPmuon else 0) +
                    (13 if gvcn_danhgia.thamgiaDayDu else 0) +
                    
                    (2 if gvcn_danhgia.thamgiaTVTS else 0) +
                    (-5 if gvcn_danhgia.koThamgiaDaydu2 else 0) +
                    (-5 if gvcn_danhgia.viphamVanHoaSV else 0) +
                    (10 if gvcn_danhgia.chaphanhDang else 0) +
                    (5 if gvcn_danhgia.giupdoCongDong else 0) +
                    (-5 if gvcn_danhgia.gayMatDoanKet else 0) +
                    (-20 if gvcn_danhgia.dongBHYTmuon else 0) +
                    
                    (3 if gvcn_danhgia.caccapKhenThuong else 0) +
                    (-5 if gvcn_danhgia.BCSvotrachnghiem else 0)
                )
                
                # Calculate total points
                gvcn_danhgia.drl_tongket = (
                    gvcn_danhgia.kqHocTap + 
                    gvcn_danhgia.diemNCKH + 
                    gvcn_danhgia.diemCDSV + 
                    gvcn_danhgia.thanhtichHoatDong + 
                    gvcn_danhgia.thanhvienBCS + 
                    boolean_points
                )
                
                # Determine xepLoai based on total points
                if gvcn_danhgia.drl_tongket >= 90:
                    gvcn_danhgia.xepLoai = 'Xuất sắc'
                elif gvcn_danhgia.drl_tongket >= 80:
                    gvcn_danhgia.xepLoai = 'Tốt'
                elif gvcn_danhgia.drl_tongket >= 65:
                    gvcn_danhgia.xepLoai = 'Khá'
                elif gvcn_danhgia.drl_tongket >= 50:
                    gvcn_danhgia.xepLoai = 'Trung bình'
                elif gvcn_danhgia.drl_tongket >= 35:
                    gvcn_danhgia.xepLoai = 'Yếu'
                else:
                    gvcn_danhgia.xepLoai = 'Kém'
                
                # Save the GVCNDanhGia record
                gvcn_danhgia.save()
                
                # Update student's trangthai to True to indicate scoring is complete
                student.trangthai = True
                student.save()
                
                # Create notification for student
                student_notification = Nofitication()
                student_notification.title = f'Điểm rèn luyện đã được chấm'
                student_notification.dob = timezone.now()
                student_notification.content = f'Giáo viên {teacher.tenGV} đã chấm điểm rèn luyện của bạn. Điểm tổng kết: {gvcn_danhgia.drl_tongket} - Xếp loại: {gvcn_danhgia.xepLoai}'
                student_notification.save()
                
                # Create private notification for teacher
                teacher_notification = PrivateNofitication()
                teacher_notification.title = f'Đã chấm điểm rèn luyện thành công'
                teacher_notification.dob = timezone.now()
                teacher_notification.content = f'Bạn đã chấm điểm rèn luyện thành công cho sinh viên {student.tenSV} - {student.maSV}. Điểm tổng kết: {gvcn_danhgia.drl_tongket} - Xếp loại: {gvcn_danhgia.xepLoai}'
                teacher_notification.save()
                
                messages.success(request, 'Đã lưu đánh giá điểm rèn luyện thành công!')
                return redirect('app_nckh9:teacher_score_management')
                
            # except Exception as inner_e:
            #     messages.error(request, f'Lỗi khi xử lý dữ liệu: {str(inner_e)}')
            #     return redirect('app_nckh9:teacher_score_management')
        
        # For GET request, show the form with current student data
        return render(request, 'teacher/rescore_student.html', {
            'teacher': teacher,
            'student': student,
        })
        
    # except InfoTeacher.DoesNotExist:
    #     messages.error(request, 'Không tìm thấy thông tin giáo viên')
    #     return redirect('app_nckh9:teacher_score_management')
    # except Exception as e:
    #     messages.error(request, f'Có lỗi xảy ra: {str(e)}')
    #     return redirect('app_nckh9:teacher_score_management')

@login_required
def teacher_score_management(request):
    try:
        teacher = InfoTeacher.objects.get(emailCoVan=request.user.email)
        lopGV = LopHoc.objects.filter(giao_vien_chu_nhiem=teacher)
        students = SinhVienTDG.objects.filter(trangthai=False,lopSV__in=lopGV.values_list('ma_lop', flat=True))
        
        # Apply filters
        # if ma_lop:
        #     students = students.filter(lopSV=ma_lop)
        
        # if search:
        #     students = students.filter(
        #         Q(maSV__icontains=search) |
        #         Q(tenSV__icontains=search) |
        #         Q(lopSV__icontains=search)
        #     )
        
        # Get unique classes for filter dropdown
        # classes = SinhVienTDG.objects.values_list('lopSV', flat=True).distinct()
        
        return render(request, 'teacher/score-management.html', {
            'teacher': teacher,
            'students': students,
            'lopGV': lopGV,
            # 'classes': classes,
            # 'selected_class': ma_lop,
            # 'search_query': search,
        })
    except InfoTeacher.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('app_nckh9:login')
    return render(request,'teacher/score-management.html', {'teacher': teacher})
@login_required
def teacher_score_management_detail(request):
    try:
        teacher = InfoTeacher.objects.get(emailCoVan=request.user.email)
        
        # Get filter parameters
        # ma_lop = request.GET.get('ma_lop')
        ma_lop = 'CNTT01'
        # search = request.GET.get('search', '')
        
        # Get all students
        students = SinhVienTDG.objects.filter(maSV='2221050508')
        
        # Apply filters
        # if ma_lop:
        #     students = students.filter(lopSV=ma_lop)
        
        # if search:
        #     students = students.filter(
        #         Q(maSV__icontains=search) |
        #         Q(tenSV__icontains=search) |
        #         Q(lopSV__icontains=search)
        #     )
        
        # Get unique classes for filter dropdown
        # classes = SinhVienTDG.objects.values_list('lopSV', flat=True).distinct()
        
        return render(request, 'teacher/score_management_detail.html', {
            'teacher': teacher,
            'students': students,
            # 'classes': classes,
            'selected_class': ma_lop,
            # 'search_query': search,
        })
        
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        return redirect('app_nckh9:teacher_score_management_detail')


from django.contrib.auth.decorators import login_required


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import SinhVienTDG, InfoTeacher, Ranking, Nofitication

@login_required
def student_dashboard(request):
    user = request.user

    # Lấy thông tin sinh viên đang đăng nhập
    current_student = InfoStudent.objects.filter(emailSV = user.email).first()
    # hoc_ki = HocKy.objects.filter(sinhvien=sinhvien)
    
    # Lấy danh sách xếp hạng và thông báo
    rankings = Ranking.objects.filter(maSV=request.user.id)
    notifications = Nofitication.objects.all()
    historic_points = []
    trend_labels = []
    trend_scores = []
    
    history = HistoryPoint.objects.filter(maSV="2221050508").first()
    if history:
        for i in range(1, 21):
            score = getattr(history, f"hocky{i}", None)
            if score is not None:
                # Tạo nhãn và điểm cho biểu đồ
                semester_label = f"Học kỳ {i}"
                nam = ((i - 1) // 2) + 1  # Năm học (1-5)
                hk = 1 if i % 2 != 0 else 2  # Học kỳ lẻ (HK1), chẵn (HK2)
                trend_labels.append(f"HK{hk}-N{nam}")
                trend_scores.append(score)  

                # Tạo dữ liệu historic_points
                historic_points.append((semester_label, score))
    current_semester = historic_points[-1] if historic_points else None
        # Sau khi đã tạo historic_points
    avg_score = None
    if historic_points:
        total_score = sum(score for _, score in historic_points)
        avg_score = round(total_score / len(historic_points))  # Làm tròn 2 chữ số thập phân

    if avg_score >= 90:
        xeploai = "Xuất sắc"
    elif avg_score >= 80:
        xeploai = "Tốt"
    elif avg_score >= 65:
        xeploai = "Khá"
    elif avg_score >= 50:
        xeploai = "Trung bình"
    elif avg_score >= 35:
        xeploai = "Yếu"
    else:
        xeploai = "Kém"
    # Truyền dữ liệu vào context
    context = {
        # 'hoc_ki': hoc_ki,
        'current_student': current_student,
        'rankings': rankings,
        'notifications': notifications,
        'xeploai':xeploai,
    }
    
    return render(request, 'students/dashboard.html', context)


@login_required
@login_required

@login_required
@login_required
@login_required
def add_hoc_ky(request):
    if request.method == 'POST':
        form = HocKyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thêm học kỳ thành công.')
            return redirect('app_nckh9:student_dashboard')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = HocKyForm()
    return render(request, 'students/add_hoc_ky.html', {'form': form})
def add_info_student(request):
    if request.method == 'POST':
        form = InfoStudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thêm thông tin sinh viên thành công.')
            return redirect('app_nckh9:student_dashboard')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = InfoStudentForm()
    return render(request, 'students/add_info_student.html', {'form': form})
def view_sinhvien(request):
    sinhvien = InfoStudent.objects.filter(maSV="2221050508").first()
    if not sinhvien:
        messages.error(request, "Không tìm thấy thông tin sinh viên.")
        return redirect('app_nckh9:student_dashboard')
    return render(request, 'students/view_sinhvien.html', {'sinhvien': sinhvien})
def add_sinhvien_tdg(request):
    if request.method == 'POST':
        form = SinhVienTDGForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thêm thông tin sinh viên thành công.')
            return redirect('app_nckh9:student_dashboard')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = SinhVienTDGForm()
    return render(request, 'students/add_sinhvien_tdg.html', {'form': form})

from django.shortcuts import render, redirect
from .forms import HistoryPointForm


def history_point_list(request):
    history_points = HistoryPoint.objects.all()
    return render(request, 'students/history_point.html', {'history_points': history_points})

from django.shortcuts import render, redirect
from .forms import HistoryPointForm

def add_history_point(request):
    if request.method == 'POST':
        form = HistoryPointForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app_nckh9:student_dashboard')  # Sử dụng namespace chính xác
    else:
        form = HistoryPointForm()
    return render(request, 'students/add_history_point.html', {'form': form})



def historic_point_view(request, maSV):
    student = InfoStudent.objects.filter(maSV=maSV).first()
    if not student:
        messages.error(request, "Không tìm thấy thông tin sinh viên.")
        return redirect('app_nckh9:student_dashboard')

    historic_points = []
    history = HistoryPoint.objects.filter(maSV=maSV).first()
    if history:
        for i in range(1, 21):
            score = getattr(history, f"hocky{i}", None)
            if score is not None:
                historic_points.append((f"Học kỳ {i}", score))

    return render(request, 'students/historic_point.html', {'historic_points': historic_points})

    if not student:
        messages.error(request, "Không tìm thấy thông tin sinh viên.")
        return redirect('app_nckh9:student_dashboard')

    historic_points = []
    history = HistoryPoint.objects.filter(maSV=maSV).first()
    if history:
        for i in range(1, 21):
            score = getattr(history, f"hocky{i}", None)
            if score is not None:
                historic_points.append((f"Học kỳ {i}", score))

    return render(request, 'students/historic_point.html', {'historic_points': historic_points})

from django.shortcuts import render, redirect
from .forms import NotificationForm

def add_notification(request):
    return render(request, 'students/add_notification.html')


    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('app_nckh9:student_notifications')  # Thay đổi URL nếu cần
    else:
        form = NotificationForm()
    return render(request, 'students/add_notification.html', {'form': form})

def lop_hoc_list(request):
    """Hiển thị danh sách các lớp học"""
    lop_hoc_list = LopHoc.objects.all().order_by('-khoa_hoc', 'khoa', 'ma_lop')
    return render(request, 'app_nckh9/lop_hoc_list.html', {'lop_hoc_list': lop_hoc_list})

def add_student_to_class(request, ma_lop):
    lop_hoc = get_object_or_404(LopHoc, ma_lop=ma_lop)
    
    if request.method == 'POST':
        form = AddStudentToClassForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            if lop_hoc.so_luong_sv_hien_tai() < lop_hoc.si_so_toi_da:
                student.lop_hoc = lop_hoc
                student.save()
                messages.success(request, f'Đã thêm sinh viên {student.tenSV} vào lớp {lop_hoc.ten_lop}')
                return redirect('app_nckh9:lop_hoc_list')
            else:
                messages.error(request, 'Lớp học đã đầy, không thể thêm sinh viên')
    else:
        form = AddStudentToClassForm()
    
    context = {
        'form': form,
        'lop_hoc': lop_hoc,
    }
    return render(request, 'app_nckh9/add_student_to_class.html', context)


@login_required
def teacher_analytics(request):
    try:
        # Lấy thông tin giáo viên
        teacher = InfoTeacher.objects.get(emailCoVan=request.user.email)
        
        # Lấy danh sách lớp của giáo viên
        lopGV = LopHoc.objects.filter(giao_vien_chu_nhiem=teacher)
        lop_ids = list(lopGV.values_list('ma_lop', flat=True))
        
        # Lấy danh sách sinh viên của giáo viên
        students = InfoStudent.objects.filter(lop_hoc__giao_vien_chu_nhiem=teacher)
        total_students = students.count()
        
        # Lấy đợt chấm điểm rèn luyện hiện tại
        active_cham_drl = ChamDRL.objects.filter(isActive=True).first()
        
        # Khởi tạo dữ liệu thống kê
        stats = {
            'total_students': total_students,
            'excellent': 0,
            'good': 0,
            'average': 0,
            'below_average': 0,
            'excellent_percent': 0,
            'good_percent': 0,
            'average_percent': 0,
            'below_average_percent': 0
        }
        
        # Khởi tạo cấu trúc dữ liệu biểu đồ
        chart_data = {
            'grade_distribution': [0, 0, 0, 0],  # Xuất sắc, Giỏi, Khá, Cần cải thiện
            'score_trend': [],
            'class_comparison': [],
            'criteria_analysis': [0, 0, 0, 0, 0],
            'detailed_score_stack': []
        }
        
        # Lấy dữ liệu thực tế nếu có đợt chấm điểm hiện tại
        if active_cham_drl:
            try:
                # 1. Phân bố điểm rèn luyện
                diem_rl = GVCNDanhGia.objects.filter(

                    cham_drl=active_cham_drl
                )
                
                if diem_rl.exists():
                    # Phân loại sinh viên theo điểm
                    excellent_count = diem_rl.filter(tong_diem__gte=90).count()
                    good_count = diem_rl.filter(tong_diem__gte=80, tong_diem__lt=90).count()
                    average_count = diem_rl.filter(tong_diem__gte=65, tong_diem__lt=80).count()
                    below_average_count = diem_rl.filter(tong_diem__lt=65).count()
                    
                    # Cập nhật thống kê
                    stats['excellent'] = excellent_count
                    stats['good'] = good_count
                    stats['average'] = average_count
                    stats['below_average'] = below_average_count
                    
                    # Tính phần trăm nếu có sinh viên
                    if total_students > 0:
                        stats['excellent_percent'] = round(excellent_count / total_students * 100, 1)
                        stats['good_percent'] = round(good_count / total_students * 100, 1)
                        stats['average_percent'] = round(average_count / total_students * 100, 1)
                        stats['below_average_percent'] = round(below_average_count / total_students * 100, 1)
                    
                    # Cập nhật dữ liệu biểu đồ phân bố điểm
                    chart_data['grade_distribution'] = [
                        excellent_count, good_count, average_count, below_average_count
                    ]
                
                # 2. Xu hướng điểm theo thời gian
                periods = ChamDRL.objects.all().order_by('created_at')[:5]  # Lấy 5 đợt chấm điểm gần nhất
                
                for period in periods:
                    period_scores = GVCNDanhGia.objects.filter(
                        cham_drl=period
                    )
                    
                    if period_scores.exists():
                        avg_score = period_scores.aggregate(Avg('tong_diem'))['tong_diem__avg']
                        chart_data['score_trend'].append({
                            'period': f"Học kỳ {period.id}",
                            'avg_score': round(avg_score, 1) if avg_score else 0
                        })
                
                # 3. So sánh giữa các lớp
                for lop in lopGV:
                    lop_scores = GVCNDanhGia.objects.filter(
                        cham_drl=active_cham_drl
                    )
                    
                    if lop_scores.exists():
                        avg_score = lop_scores.aggregate(Avg('tong_diem'))['tong_diem__avg']
                        student_count = lop_scores.count()
                        
                        chart_data['class_comparison'].append({
                            'class_name': lop.ten_lop,
                            'avg_score': round(avg_score, 1) if avg_score else 0,
                            'student_count': student_count
                        })
                
                # 4. Phân tích tiêu chí
                if diem_rl.exists():
                    criteria_avg = [
                        diem_rl.aggregate(Avg('y_thuc_hoc_tap'))['y_thuc_hoc_tap__avg'] or 0,
                        diem_rl.aggregate(Avg('y_thuc_ky_luat'))['y_thuc_ky_luat__avg'] or 0,
                        diem_rl.aggregate(Avg('hoat_dong_doan_the'))['hoat_dong_doan_the__avg'] or 0,
                        diem_rl.aggregate(Avg('quan_he_cong_dong'))['quan_he_cong_dong__avg'] or 0,
                        diem_rl.aggregate(Avg('pham_chat_dao_duc'))['pham_chat_dao_duc__avg'] or 0
                    ]
                    
                    chart_data['criteria_analysis'] = [round(score, 1) for score in criteria_avg]
                
                # 5. Phân bố chi tiết theo thời gian
                for period in periods:
                    period_scores = DiemRenLuyen.objects.filter(
                        sinh_vien__lop_hoc__giao_vien_chu_nhiem=teacher,
                        cham_drl=period
                    )
                    
                    if period_scores.exists():
                        excellent = period_scores.filter(tong_diem__gte=90).count()
                        good = period_scores.filter(tong_diem__gte=80, tong_diem__lt=90).count()
                        average = period_scores.filter(tong_diem__gte=65, tong_diem__lt=80).count()
                        below_average = period_scores.filter(tong_diem__lt=65).count()
                        
                        chart_data['detailed_score_stack'].append({
                            'period': f"Học kỳ {period.id}",
                            'excellent': excellent,
                            'good': good,
                            'average': average,
                            'below_average': below_average
                        })
            except Exception as e:
                # Nếu có lỗi, sử dụng dữ liệu mẫu
                print(f"Lỗi khi lấy dữ liệu thực tế: {e}")
                chart_data = {
                    'grade_distribution': [10, 20, 15, 5],
                    'score_trend': [
                        {'period': 'Học kỳ 1', 'avg_score': 85.5},
                        {'period': 'Học kỳ 2', 'avg_score': 87.2},
                        {'period': 'Học kỳ 3', 'avg_score': 86.8},
                        {'period': 'Học kỳ 4', 'avg_score': 88.1},
                        {'period': 'Học kỳ 5', 'avg_score': 89.3}
                    ],
                    'class_comparison': [
                        {'class_name': 'CNTT1', 'avg_score': 88.5, 'student_count': 30},
                        {'class_name': 'CNTT2', 'avg_score': 85.2, 'student_count': 28},
                        {'class_name': 'CNTT3', 'avg_score': 82.7, 'student_count': 25},
                        {'class_name': 'KHMT1', 'avg_score': 87.9, 'student_count': 32},
                        {'class_name': 'KHMT2', 'avg_score': 84.3, 'student_count': 27}
                    ],
                    'criteria_analysis': [85, 78, 92, 80, 88],
                    'detailed_score_stack': [
                        {
                            'period': 'Học kỳ 1',
                            'excellent': 8,
                            'good': 15,
                            'average': 12,
                            'below_average': 5
                        },
                        {
                            'period': 'Học kỳ 2',
                            'excellent': 10,
                            'good': 18,
                            'average': 10,
                            'below_average': 2
                        },
                        {
                            'period': 'Học kỳ 3',
                            'excellent': 12,
                            'good': 20,
                            'average': 8,
                            'below_average': 0
                        }
                    ]
                }
        else:
            # Nếu không có đợt chấm điểm hiện tại, sử dụng dữ liệu mẫu
            chart_data = {
                'grade_distribution': [10, 20, 15, 5],
                'score_trend': [
                    {'period': 'Học kỳ 1', 'avg_score': 85.5},
                    {'period': 'Học kỳ 2', 'avg_score': 87.2},
                    {'period': 'Học kỳ 3', 'avg_score': 86.8},
                    {'period': 'Học kỳ 4', 'avg_score': 88.1},
                    {'period': 'Học kỳ 5', 'avg_score': 89.3}
                ],
                'class_comparison': [
                    {'class_name': 'CNTT1', 'avg_score': 88.5, 'student_count': 30},
                    {'class_name': 'CNTT2', 'avg_score': 85.2, 'student_count': 28},
                    {'class_name': 'CNTT3', 'avg_score': 82.7, 'student_count': 25},
                    {'class_name': 'KHMT1', 'avg_score': 87.9, 'student_count': 32},
                    {'class_name': 'KHMT2', 'avg_score': 84.3, 'student_count': 27}
                ],
                'criteria_analysis': [85, 78, 92, 80, 88],
                'detailed_score_stack': [
                    {
                        'period': 'Học kỳ 1',
                        'excellent': 8,
                        'good': 15,
                        'average': 12,
                        'below_average': 5
                    },
                    {
                        'period': 'Học kỳ 2',
                        'excellent': 10,
                        'good': 18,
                        'average': 10,
                        'below_average': 2
                    },
                    {
                        'period': 'Học kỳ 3',
                        'excellent': 12,
                        'good': 20,
                        'average': 8,
                        'below_average': 0
                    }
                ]
            }
        
        # Chuyển đổi dữ liệu biểu đồ sang JSON
        try:
            chart_data_json = json.dumps(chart_data, default=str)
        except Exception as e:
            print(f"Lỗi khi chuyển đổi dữ liệu sang JSON: {e}")
            chart_data_json = json.dumps({
                'grade_distribution': [0, 0, 0, 0],
                'score_trend': [],
                'class_comparison': [],
                'criteria_analysis': [0, 0, 0, 0, 0],
                'detailed_score_stack': []
            })
        
        # Tạo context và trả về template
        context = {
            'teacher': teacher,
            'stats': stats,
            'active_cham_drl': active_cham_drl,
            'chart_data': chart_data_json
        }
        
        return render(request, 'teacher/analytics.html', context)
    except InfoTeacher.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin giảng viên')
        return redirect('app_nckh9:login')
    except Exception as e:
        messages.error(request, f'Lỗi: {str(e)}')
        return redirect('app_nckh9:teacher_dashboard')
