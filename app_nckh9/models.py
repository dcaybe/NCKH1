from django.db import models
from django.utils import timezone

class InfoStudent(models.Model):
    khoaHoc = models.IntegerField(default=2023)
    maSV = models.IntegerField(unique=True)
    tenSV = models.CharField(max_length=255)
    lopSV = models.CharField(max_length=255)  # Giữ lại để tương thích ngược
    gender = models.CharField(max_length=255)
    dob = models.DateField()
    phone = models.IntegerField()
    emailSV = models.EmailField(unique=True)
    status = models.CharField(max_length=255, default='Đang học')
    address = models.CharField(max_length=255)
    chuyenNganh = models.CharField(max_length=255)
    khoaSV = models.CharField(max_length=255)
    nienkhoa = models.CharField(max_length=255)
    heDaoTao = models.CharField(max_length=255)
    coVanHocTap = models.CharField(max_length=255, blank=True, null=True)
    tkCoVan = models.CharField(max_length=255, blank=True, null=True)
    emialCoVan = models.EmailField(blank=True, null=True)
    phoneCoVan = models.IntegerField(blank=True, null=True)
    boMonCoVan = models.CharField(max_length=255, blank=True, null=True)
    ketqua = models.JSONField(default=dict)
    semester = models.CharField(max_length=255, blank=True, null=True)
    lop_hoc = models.ForeignKey(
        'LopHoc',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='danh_sach_sinh_vien',
        verbose_name="Lớp học"
    )

    def __str__(self):
        return f"{self.maSV} - {self.tenSV}"

class InfoTeacher(models.Model):
    maGV = models.IntegerField()
    tenGV = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    dob = models.DateField()
    phone = models.IntegerField()
    emailCoVan = models.EmailField()
    status = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    boMonCoVan = models.CharField(max_length=255)
    hocViCoVan = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.maGV} - {self.tenGV}"

class SinhVienTDG(models.Model):
    maSV = models.IntegerField()
    tenSV = models.CharField(max_length=255)
    lopSV = models.CharField(max_length=255)
    dob = models.DateField()
    khoaSV = models.CharField(max_length=255)
    khoaHoc = models.IntegerField()
    kqHocTap = models.IntegerField()
    diemNCKH = models.IntegerField()
    koDungPhao = models.BooleanField()
    koDiHocMuon = models.BooleanField()
    boThiOlympic = models.BooleanField()
    tronHoc = models.BooleanField()
    koVPKL = models.BooleanField()
    diemCDSV = models.IntegerField()
    koThamgiaDaydu = models.BooleanField()
    koDeoTheSV = models.BooleanField()
    koSHL = models.BooleanField()
    dongHPmuon = models.BooleanField()
    thamgiaDayDu = models.BooleanField()
    thanhtichHoatDong = models.IntegerField()
    thamgiaTVTS = models.BooleanField()
    koThamgiaDaydu2 = models.BooleanField()
    viphamVanHoaSV = models.BooleanField()
    chaphanhDang = models.BooleanField()
    giupdoCongDong = models.BooleanField()
    gayMatDoanKet = models.BooleanField()
    dongBHYTmuon = models.BooleanField()
    thanhvienBCS = models.IntegerField()
    caccapKhenThuong = models.BooleanField()
    BCSvotrachnghiem = models.BooleanField()
    anhminhchung1 = models.ImageField(upload_to="uploads/")
    anhminhchung2 = models.ImageField(upload_to="uploads/")
    anhminhchung3 = models.ImageField(upload_to="uploads/")
    anhminhchung4 = models.ImageField(upload_to="uploads/")
    anhminhchung5 = models.ImageField(upload_to="uploads/")
    anhminhchung6 = models.ImageField(upload_to="uploads/")
    anhminhchung7 = models.ImageField(upload_to="uploads/")
    ghichu1 = models.CharField(max_length=500)
    ghichu2 = models.CharField(max_length=500)
    ghichu3 = models.CharField(max_length=500)
    ghichu4 = models.CharField(max_length=500)
    ghichu5 = models.CharField(max_length=500)
    ghichu6 = models.CharField(max_length=500)
    ghichu7 = models.CharField(max_length=500)
    ghichu8 = models.CharField(max_length=500)
    drl_tongket = models.IntegerField(default=0)
    xepLoai = models.CharField(max_length=255)
    trangthai = models.BooleanField(default=False)

class GVCNDanhGia(models.Model):
    maSV = models.IntegerField()
    tenSV = models.CharField(max_length=255)
    lopSV = models.CharField(max_length=255) 
    dob = models.DateField()
    khoaSV = models.CharField(max_length=255)
    khoaHoc = models.IntegerField()
    kqHocTap = models.IntegerField()
    diemNCKH = models.IntegerField()
    koDungPhao = models.BooleanField()
    koDiHocMuon = models.BooleanField()
    boThiOlympic = models.BooleanField()
    tronHoc = models.BooleanField()
    koVPKL = models.BooleanField()
    diemCDSV = models.IntegerField()
    koThamgiaDaydu = models.BooleanField()
    koDeoTheSV = models.BooleanField()
    koSHL = models.BooleanField()
    dongHPmuon = models.BooleanField()
    thamgiaDayDu = models.BooleanField()
    thanhtichHoatDong = models.IntegerField()
    thamgiaTVTS = models.BooleanField()
    koThamgiaDaydu2 = models.BooleanField()
    viphamVanHoaSV = models.BooleanField()
    chaphanhDang = models.BooleanField()
    giupdoCongDong = models.BooleanField()
    gayMatDoanKet = models.BooleanField()
    dongBHYTmuon = models.BooleanField()
    thanhvienBCS = models.IntegerField()
    caccapKhenThuong = models.BooleanField()
    BCSvotrachnghiem = models.BooleanField()
    anhminhchung1 = models.ImageField(upload_to="uploads/")
    anhminhchung2 = models.ImageField(upload_to="uploads/")
    anhminhchung3 = models.ImageField(upload_to="uploads/")
    anhminhchung4 = models.ImageField(upload_to="uploads/")
    anhminhchung5 = models.ImageField(upload_to="uploads/")
    anhminhchung6 = models.ImageField(upload_to="uploads/")
    anhminhchung7 = models.ImageField(upload_to="uploads/")
    ghichu1 = models.CharField(max_length=500)
    ghichu2 = models.CharField(max_length=500)
    ghichu3 = models.CharField(max_length=500)
    ghichu4 = models.CharField(max_length=500)
    ghichu5 = models.CharField(max_length=500)
    ghichu6 = models.CharField(max_length=500)
    ghichu7 = models.CharField(max_length=500)
    ghichu8 = models.CharField(max_length=500)
    drl_tongket = models.IntegerField(default=0)
    xepLoai = models.CharField(max_length=255)
    trangthai = models.BooleanField(default=False)

class HoiDongKhoaChamDiem(models.Model):
    maSV = models.IntegerField()
    tenSV = models.CharField(max_length=255)
    lopSV = models.CharField(max_length=255)
    dob = models.DateField()
    khoaSV = models.CharField(max_length=255)
    khoaHoc = models.IntegerField()
    kqHocTap = models.IntegerField()
    diemNCKH = models.IntegerField()
    koDungPhao = models.BooleanField()
    koDiHocMuon = models.BooleanField()
    boThiOlympic = models.BooleanField()
    tronHoc = models.BooleanField()
    koVPKL = models.BooleanField()
    diemCDSV = models.IntegerField()
    koThamgiaDaydu = models.BooleanField()
    koDeoTheSV = models.BooleanField()
    koSHL = models.BooleanField()
    dongHPmuon = models.BooleanField()
    thamgiaDayDu = models.BooleanField()
    thanhtichHoatDong = models.IntegerField()
    thamgiaTVTS = models.BooleanField()
    koThamgiaDaydu2 = models.BooleanField()
    viphamVanHoaSV = models.BooleanField()
    chaphanhDang = models.BooleanField()
    giupdoCongDong = models.BooleanField()
    gayMatDoanKet = models.BooleanField()
    dongBHYTmuon = models.BooleanField()
    thanhvienBCS = models.IntegerField()
    caccapKhenThuong = models.BooleanField()
    BCSvotrachnghiem = models.BooleanField()
    anhminhchung1 = models.ImageField(upload_to="uploads/")
    anhminhchung2 = models.ImageField(upload_to="uploads/")
    anhminhchung3 = models.ImageField(upload_to="uploads/")
    anhminhchung4 = models.ImageField(upload_to="uploads/")
    anhminhchung5 = models.ImageField(upload_to="uploads/")
    anhminhchung6 = models.ImageField(upload_to="uploads/")
    anhminhchung7 = models.ImageField(upload_to="uploads/")
    ghichu1 = models.CharField(max_length=500)
    ghichu2 = models.CharField(max_length=500)
    ghichu3 = models.CharField(max_length=500)
    ghichu4 = models.CharField(max_length=500)
    ghichu5 = models.CharField(max_length=500)
    ghichu6 = models.CharField(max_length=500)
    ghichu7 = models.CharField(max_length=500)
    ghichu8 = models.CharField(max_length=500)
    drl_tongket = models.IntegerField(default=0)
    xepLoai = models.CharField(max_length=255)

class Nofitication(models.Model):
    title = models.CharField(max_length=255)
    dob = models.DateTimeField()
    content = models.TextField()
    picture1 = models.ImageField(upload_to="uploads/")
    picture2 = models.ImageField(upload_to="uploads/")
    picture3 = models.ImageField(upload_to="uploads/")
    picture4 = models.ImageField(upload_to="uploads/")
    picture5 = models.ImageField(upload_to="uploads/")

class PrivateNofitication(models.Model):
    title = models.CharField(max_length=255)
    dob = models.DateTimeField()
    content = models.TextField()
    picture1 = models.ImageField(upload_to="uploads/")
    picture2 = models.ImageField(upload_to="uploads/")
    picture3 = models.ImageField(upload_to="uploads/")
    picture4 = models.ImageField(upload_to="uploads/")
    picture5 = models.ImageField(upload_to="uploads/")

class StudentsReport(models.Model):
    muckhieunai = models.CharField(max_length=255,default='khac')
    title = models.CharField(max_length=255)
    content = models.TextField(default='')
    created_at = models.DateTimeField(default=timezone.now)
    student = models.ForeignKey('InfoStudent', on_delete=models.CASCADE, null=True, blank=True)
    semester = models.ForeignKey('HocKy', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Đang chờ'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Đã từ chối')
    ], default='pending')
    response = models.TextField(blank=True, null=True)
    evidence = models.FileField(upload_to='uploads/reports/', blank=True, null=True)

class ComplaintHistory(models.Model):
    time = models.DateTimeField()
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    description = models.TextField()
    device = models.CharField(max_length=255)

class Ranking(models.Model):
    semester = models.CharField(max_length=255)
    rank_number = models.IntegerField()
    maSV = models.IntegerField()
    tenSV = models.CharField(max_length=255)
    lopSV = models.CharField(max_length=255)
    point = models.ForeignKey('HoiDongKhoaChamDiem', on_delete=models.CASCADE)

class TeacherManager(models.Model):
    allClass = models.IntegerField()
    allStudent = models.IntegerField()
    countdown = models.DateTimeField()

class Analysts(models.Model):
    allStudent = models.IntegerField()
    diemTB = models.FloatField()
    needImprove = models.IntegerField() 
    good = models.IntegerField()
    phanboDRL = models.JSONField()
    xuhuongDiem = models.JSONField()
    phantichTieuchi = models.JSONField()
    compareClass = models.JSONField()

class NofiticationManager(models.Model):
    allNotification = models.IntegerField()
    countdown = models.DateTimeField()
    type = models.CharField(max_length=255)

class HomepageManager(models.Model):
    allStudent = models.IntegerField()
    pending = models.IntegerField()
    diemTb = models.FloatField()
    recommendbyAI = models.JSONField()
    recommendbyAI2 = models.JSONField()

class PendingStudents(models.Model):
    khoa = models.CharField(max_length=255)
    lop = models.CharField(max_length=255)
    semester = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    maSV = models.IntegerField()
    tenSV = models.CharField(max_length=255)
    drl_tongket = models.IntegerField()
    classification = models.CharField(max_length=255)
    time = models.DateTimeField()

class Analysts2(models.Model):
    allStudent = models.IntegerField()
    diemTB = models.FloatField()
    needImprove = models.IntegerField()
    good = models.IntegerField()
    phanboDRL = models.JSONField()
    xuhuongDiem = models.JSONField()
    phantichTieuchi = models.JSONField()
    compareClass = models.JSONField()

class AdminManage(models.Model):
    id = models.AutoField(primary_key=True)
    tenSV = models.CharField(max_length=255)
    emailSV = models.EmailField()
    position = models.CharField(max_length=255)
    khoa = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

class HistoryActive(models.Model):
    maSV = models.CharField(max_length=255,null=True)
    time = models.DateTimeField()
    name = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    description = models.TextField()
    device = models.CharField(max_length=255)
    ip = models.CharField(max_length=255)

class Login(models.Model):
    maSV = models.IntegerField()
    password = models.CharField("password", max_length=255)
    emailSV = models.EmailField()

class KairaChatBot(models.Model):
    question = models.TextField()
    answer = models.TextField()
    time = models.DateTimeField()
    image1 = models.ImageField(upload_to="uploads/")
    image2 = models.ImageField(upload_to="uploads/")

class HistoryPoint(models.Model):
    lopSV = models.CharField(max_length=255)
    tenSV = models.CharField(max_length=255)
    maSV = models.IntegerField()
    hocky1 = models.IntegerField(blank=True, null=True)
    hocky2 = models.IntegerField(blank=True, null=True)
    hocky3 = models.IntegerField(blank=True, null=True)
    hocky4 = models.IntegerField(blank=True, null=True)
    hocky5 = models.IntegerField(blank=True, null=True)
    hocky6 = models.IntegerField(blank=True, null=True)
    hocky7 = models.IntegerField(blank=True, null=True)
    hocky8 = models.IntegerField(blank=True, null=True)
    hocky9 = models.IntegerField(blank=True, null=True)
    hocky10 = models.IntegerField(blank=True, null=True)    
    hocky11 = models.IntegerField(blank=True, null=True)
    hocky12 = models.IntegerField(blank=True, null=True)
    hocky13 = models.IntegerField(blank=True, null=True)
    hocky14 = models.IntegerField(blank=True, null=True)
    hocky15 = models.IntegerField(blank=True, null=True)
    hocky16 = models.IntegerField(blank=True, null=True)
    hocky17 = models.IntegerField(blank=True, null=True)
    hocky18 = models.IntegerField(blank=True, null=True)
    hocky19 = models.IntegerField(blank=True, null=True)
    hocky20 = models.IntegerField(blank=True, null=True)

class AsyncExportTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang chờ'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Thất bại')
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV')
    ]
    
    DATA_TYPE_CHOICES = [
        ('scores', 'Điểm số'),
        ('appeals', 'Khiếu nại'),
        ('users', 'Người dùng'),
        ('activities', 'Hoạt động')
    ]
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)
    file_path = models.CharField(max_length=255, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    include_fields = models.JSONField(null=True, blank=True)

class AsyncSyncTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang chờ'),
        ('processing', 'Đang xử lý'), 
        ('completed', 'Hoàn thành'),
        ('failed', 'Thất bại')
    ]
    
    SYNC_TYPE_CHOICES = [
        ('full', 'Đồng bộ toàn bộ'),
        ('incremental', 'Đồng bộ tăng dần')
    ]
    
    DATA_TYPE_CHOICES = [
        ('scores', 'Điểm số'),
        ('users', 'Người dùng'),
        ('activities', 'Hoạt động')
    ]
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPE_CHOICES)
    source_system = models.CharField(max_length=100)
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)
    total_records = models.IntegerField(null=True, blank=True)
    processed_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    errors = models.JSONField(default=list)
    last_sync_time = models.DateTimeField(null=True, blank=True)

class LopHoc(models.Model):
    ma_lop = models.CharField(max_length=20, unique=True, verbose_name="Mã lớp")
    ten_lop = models.CharField(max_length=100, verbose_name="Tên lớp")
    khoa = models.CharField(max_length=100, verbose_name="Khoa")
    khoa_hoc = models.IntegerField(verbose_name="Khóa học")
    giao_vien_chu_nhiem = models.ForeignKey(
        'InfoTeacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lop_chu_nhiem',
        verbose_name="Giáo viên chủ nhiệm"
    )
    si_so_toi_da = models.PositiveSmallIntegerField(default=125, verbose_name="Sĩ số tối đa")
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    hoc_ky_hien_tai = models.ForeignKey(
        'HocKy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cac_lop_hoc',
        verbose_name="Học kỳ hiện tại"
    )

    class Meta:
        verbose_name = "Lớp học"
        verbose_name_plural = "Danh sách lớp học"
        ordering = ['-khoa_hoc', 'khoa', 'ma_lop']

    def __str__(self):
        return f"{self.ma_lop} - {self.ten_lop} (Khóa {self.khoa_hoc})"
    
    def so_luong_sv_hien_tai(self):
        """Trả về số lượng sinh viên hiện tại trong lớp"""
        return self.danh_sach_sinh_vien.count()
    
    def con_cho_phep_dang_ky(self):
        """Kiểm tra xem lớp còn chỗ trống không"""
        return self.so_luong_sv_hien_tai() < self.si_so_toi_da


class HocKy(models.Model):
    ma_hoc_ky = models.CharField(max_length=20, unique=True, null=True, blank=True, default='HK_DEFAULT')
    ten_hoc_ky = models.CharField(max_length=255)
    nam_hoc = models.IntegerField()
    hoc_ky = models.IntegerField(choices=[(1, "Học kỳ 1"), (2, "Học kỳ 2")])
    ngay_bat_dau = models.DateField(default='2025-01-01')
    ngay_ket_thuc = models.DateField(default='2025-06-30')
    ngay_bat_dau_danh_gia = models.DateField(default='2025-01-01')
    ngay_ket_thuc_danh_gia = models.DateField(default='2025-06-30')
    isActive = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-nam_hoc', '-hoc_ky']
        unique_together = ['nam_hoc', 'hoc_ky']

    def __str__(self):
        return f"{self.ten_hoc_ky} - {self.nam_hoc}"

    def clean(self):
        from django.core.exceptions import ValidationError
        # Kiểm tra ngày bắt đầu phải trước ngày kết thúc
        if self.ngay_bat_dau and self.ngay_ket_thuc and self.ngay_bat_dau >= self.ngay_ket_thuc:
            raise ValidationError("Ngày bắt đầu phải trước ngày kết thúc")
        
        # Kiểm tra thời gian đánh giá phải nằm trong khoảng thời gian học kỳ
        if self.ngay_bat_dau_danh_gia < self.ngay_bat_dau or self.ngay_ket_thuc_danh_gia > self.ngay_ket_thuc:
            raise ValidationError("Thời gian đánh giá phải nằm trong khoảng thời gian học kỳ")

    def save(self, *args, **kwargs):
        # Nếu học kỳ này được set active, hủy active của các học kỳ khác
        if self.isActive:
            HocKy.objects.exclude(id=self.id).update(isActive=False)
        super().save(*args, **kwargs)


class ChamDRL(models.Model):
    ma_cham_drl = models.CharField(max_length=20, unique=True, verbose_name="Mã đợt chấm DRL")
    ten_dot_cham = models.CharField(max_length=255, verbose_name="Tên đợt chấm DRL")
    hoc_ky = models.ForeignKey(
        'HocKy',
        on_delete=models.CASCADE,
        related_name='cac_dot_cham_drl',
        verbose_name="Học kỳ"
    )
    ngay_gio_bat_dau = models.DateTimeField(verbose_name="Ngày giờ bắt đầu chấm DRL")
    ngay_gio_ket_thuc = models.DateTimeField(verbose_name="Ngày giờ kết thúc chấm DRL")
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    isActive = models.BooleanField(default=False, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    class Meta:
        verbose_name = "Đợt chấm điểm rèn luyện"
        verbose_name_plural = "Danh sách đợt chấm điểm rèn luyện"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ten_dot_cham} - {self.hoc_ky}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Kiểm tra ngày bắt đầu phải trước ngày kết thúc
        if self.ngay_gio_bat_dau and self.ngay_gio_ket_thuc and self.ngay_gio_bat_dau >= self.ngay_gio_ket_thuc:
            raise ValidationError("Ngày giờ bắt đầu phải trước ngày giờ kết thúc")
        
        # Kiểm tra thời gian đánh giá phải nằm trong khoảng thời gian học kỳ
        if self.hoc_ky and (self.ngay_gio_bat_dau.date() < self.hoc_ky.ngay_bat_dau or 
                           self.ngay_gio_ket_thuc.date() > self.hoc_ky.ngay_ket_thuc):
            raise ValidationError("Thời gian chấm DRL phải nằm trong khoảng thời gian học kỳ")
    
    def save(self, *args, **kwargs):
        # Nếu đợt chấm DRL này được set active, hủy active của các đợt chấm DRL khác
        if self.isActive:
            ChamDRL.objects.exclude(id=self.id).update(isActive=False)
        super().save(*args, **kwargs)
    
    def is_active_now(self):
        """Kiểm tra xem đợt chấm DRL có đang hoạt động tại thời điểm hiện tại không"""
        now = timezone.now()
        return self.isActive and self.ngay_gio_bat_dau <= now <= self.ngay_gio_ket_thuc
    
    def get_status(self):
        """Trả về trạng thái hiện tại của đợt chấm DRL"""
        now = timezone.now()
        if not self.isActive:
            return "Không hoạt động"
        elif now < self.ngay_gio_bat_dau:
            return "Chưa bắt đầu"
        elif now > self.ngay_gio_ket_thuc:
            return "Đã kết thúc"
        else:
            return "Đang diễn ra"


class Rules(models.Model):
    RULE_TYPES = [
        ('ythuc_hoctap', 'Ý thức và kết quả học tập'),
        ('ythuc_kyluat', 'Ý thức chấp hành nội quy, quy chế'),
        ('hoatdong_doanthethechao', 'Hoạt động đoàn thể, thể thao'),
        ('quanhe_congdong', 'Quan hệ cộng đồng'),
        ('phamchat_daoduc', 'Phẩm chất đạo đức'),
        ('phutrachlop', 'Phụ trách lớp, đoàn thể')
    ]
    
    POINT_TYPES = [
        ('cong', 'Cộng điểm'),
        ('tru', 'Trừ điểm')
    ]
    
    section = models.CharField(max_length=50, choices=RULE_TYPES, verbose_name="Mục đánh giá")
    sub_section = models.CharField(max_length=255, verbose_name="Tiểu mục")
    rule_name = models.CharField(max_length=500, verbose_name="Tên quy tắc")
    point_type = models.CharField(max_length=10, choices=POINT_TYPES, verbose_name="Loại điểm")
    points = models.CharField(max_length=20, verbose_name="Số điểm")
    max_points = models.IntegerField(default=0, verbose_name="Điểm tối đa")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Đang áp dụng")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    
    class Meta:
        verbose_name = "Quy tắc chấm điểm"
        verbose_name_plural = "Quy tắc chấm điểm"
        ordering = ['section', 'order']
    
    def __str__(self):
        return f"{self.rule_name} ({self.points})"
