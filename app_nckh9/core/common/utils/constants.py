# User Types
USER_TYPE_ADMIN = 'admin'
USER_TYPE_TEACHER = 'teacher'
USER_TYPE_STUDENT = 'student'

# User Status
USER_STATUS_ACTIVE = 'active'
USER_STATUS_INACTIVE = 'inactive'
USER_STATUS_PENDING = 'pending'

# Score Classifications
SCORE_EXCELLENT = 'Xuất sắc'
SCORE_GOOD = 'Tốt'
SCORE_FAIR = 'Khá'
SCORE_AVERAGE = 'Trung bình'
SCORE_WEAK = 'Yếu'
SCORE_POOR = 'Kém'

# Score Ranges
SCORE_RANGE_EXCELLENT = 90
SCORE_RANGE_GOOD = 80
SCORE_RANGE_FAIR = 65
SCORE_RANGE_AVERAGE = 50
SCORE_RANGE_WEAK = 35

# Appeal Status
APPEAL_STATUS_PENDING = 'pending'
APPEAL_STATUS_APPROVED = 'approved'
APPEAL_STATUS_REJECTED = 'rejected'

# File Upload Settings
ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Email Settings
EMAIL_SENDER = 'noreply@humg.edu.vn'
EMAIL_SUBJECTS = {
    'password_reset': 'Đặt lại mật khẩu - HUMG',
    'score_update': 'Cập nhật điểm rèn luyện - HUMG',
    'appeal_response': 'Phản hồi khiếu nại - HUMG',
}

# System Settings
ITEMS_PER_PAGE = 10
SESSION_TIMEOUT = 30 * 60  # 30 minutes
PASSWORD_MIN_LENGTH = 8

# Score Calculation Rules
SCORE_RULES = {
    'koDungPhao': 3,
    'koDiHocMuon': 2,
    'boThiOlympic': -15,
    'tronHoc': -2,
    'koVPKL': 10,
    'koThamgiaDaydu': -10,
    'koDeoTheSV': -5,
    'koSHL': -5,
    'dongHPmuon': -10,
    'thamgiaDayDu': 13,
    'thamgiaTVTS': 2,
    'koThamgiaDaydu2': -5,
    'viphamVanHoaSV': -5,
    'chaphanhDang': 10,
    'giupdoCongDong': 5,
    'gayMatDoanKet': -5,
    'dongBHYTmuon': -20,
    'caccapKhenThuong': 3,
    'BCSvotrachnghiem': -5,
}

# Date Format
DATE_FORMAT = '%d/%m/%Y'
DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'