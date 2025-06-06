# Kế Hoạch Tái Cấu Trúc Ứng Dụng

## Cấu Trúc Thư Mục Mới

```
core/
├── common/
│   ├── auth/
│   │   ├── views.py         # Xử lý đăng nhập/đăng xuất/reset mật khẩu
│   │   └── urls.py         # URL routing cho authentication
│   ├── base/
│   │   ├── models.py       # Các model dùng chung
│   │   └── serializers.py  # Serializers dùng chung
│   └── utils/
│       ├── constants.py    # Các hằng số
│       └── helpers.py      # Các hàm tiện ích
├── student/
│   ├── score/
│   │   ├── views.py       # Quản lý điểm rèn luyện
│   │   └── urls.py
│   ├── profile/          # Thông tin cá nhân sinh viên
│   └── appeals/         # Xử lý khiếu nại
├── teacher/
│   ├── classes/         # Quản lý lớp học
│   ├── evaluation/      # Đánh giá điểm rèn luyện
│   └── reports/         # Báo cáo và thống kê
└── admin/
    ├── users/           # Quản lý người dùng
    ├── settings/        # Cài đặt hệ thống
    └── analytics/       # Phân tích dữ liệu

templates/
├── common/            # Templates dùng chung
├── student/          # Templates cho sinh viên
├── teacher/         # Templates cho giáo viên
└── admin/           # Templates cho admin

static/
├── css/
├── js/
│   ├── common/      # JavaScript dùng chung
│   ├── student/     # JavaScript cho sinh viên
│   ├── teacher/     # JavaScript cho giáo viên
│   └── admin/       # JavaScript cho admin
└── assets/         # Hình ảnh và tài nguyên khác
```

## Chi Tiết Các Module

### 1. Common Module
- **Auth**: Xử lý authentication và authorization
- **Base**: Chứa các models và serializers dùng chung
- **Utils**: Các công cụ và hàm tiện ích

### 2. Student Module
- **Score**: Quản lý và xem điểm rèn luyện
- **Profile**: Quản lý thông tin cá nhân
- **Appeals**: Xử lý khiếu nại và yêu cầu

### 3. Teacher Module
- **Classes**: Quản lý lớp học và sinh viên
- **Evaluation**: Đánh giá điểm rèn luyện
- **Reports**: Báo cáo và thống kê

### 4. Admin Module
- **Users**: Quản lý tài khoản người dùng
- **Settings**: Cấu hình hệ thống
- **Analytics**: Phân tích dữ liệu

## Kế Hoạch Thực Hiện

### Bước 1: Chuẩn Bị
1. Tạo cấu trúc thư mục mới
2. Sao lưu code hiện tại

### Bước 2: Tái Cấu Trúc Models
1. Tách models.py thành các file riêng trong common/base/
2. Cập nhật các references và imports

### Bước 3: Tái Cấu Trúc Views và URLs
1. Di chuyển các views vào module tương ứng
2. Tổ chức lại cấu trúc URL routing
3. Cập nhật các imports và paths

### Bước 4: Tái Cấu Trúc Templates và Static Files
1. Di chuyển templates vào thư mục tương ứng
2. Tổ chức lại static files theo module
3. Cập nhật các đường dẫn trong code

### Bước 5: Tối Ưu Hóa
1. Kiểm tra và cập nhật các dependencies
2. Tối ưu hóa imports
3. Chuẩn hóa naming convention

## Quy Tắc Đặt Tên
- Sử dụng lowercase cho tên file và thư mục
- Sử dụng dấu gạch dưới cho tên file nhiều từ
- Đặt tên rõ ràng và mô tả đúng chức năng

## Lợi Ích
1. Code dễ bảo trì và mở rộng
2. Giảm sự phụ thuộc giữa các module
3. Dễ dàng phát triển và testing
4. Cấu trúc rõ ràng, dễ hiểu

## Lưu Ý
- Đảm bảo backwards compatibility
- Cập nhật documentation
- Viết tests cho các thay đổi
- Kiểm tra kỹ các dependencies