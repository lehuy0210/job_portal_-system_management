import os
import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
import bcrypt
import jwt

# Thiết lập biến môi trường ảo cho JWT Secret TRƯỚC KHI import service
os.environ["JWT_SECRET"] = "test_super_secret_key"

# Sửa lại 'src.auth' thành tên thư mục module auth thực tế của em nhé
from src.auth.controllers import auth_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    app.testing = True
    with app.test_client() as client:
        yield client


# Đường dẫn để patch mock repository
MOCK_DB_SESSION = "src.auth.controllers.get_db_session"
MOCK_AUTH_REPO = "src.auth.controllers.AuthRepository"


# ==========================================
# 1. CASE NGHIỆP VỤ (BUSINESS LOGIC - HAPPY PATH)
# ==========================================

@patch(MOCK_AUTH_REPO)
@patch(MOCK_DB_SESSION)
def test_register_success(mock_db, mock_repo_class, client):
    """Nghiệp vụ: Đăng ký thành công với dữ liệu hợp lệ"""
    mock_repo_instance = mock_repo_class.return_value
    mock_repo_instance.get_user_by_username.return_value = None  # Chưa ai dùng tên này
    mock_repo_instance.create_user.return_value = {"id": 1, "username": "huy_dev", "ma_vai_tro": 1}

    payload = {"username": "huy_dev", "password": "securepassword123"}
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    assert response.json["data"]["username"] == "huy_dev"
    assert response.json["data"]["ma_vai_tro"] == 1  # Đảm bảo user mới luôn là role 1 (Ứng viên)


@patch(MOCK_AUTH_REPO)
@patch(MOCK_DB_SESSION)
def test_login_success(mock_db, mock_repo_class, client):
    """Nghiệp vụ: Đăng nhập thành công, trả về token hợp lệ"""
    password = "securepassword123"
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Mock DB trả về user với mật khẩu ĐÃ BĂM
    mock_user = MagicMock(id=1, username="huy_dev", password=hashed_pw, ma_vai_tro=1)
    mock_repo_instance = mock_repo_class.return_value
    mock_repo_instance.get_user_by_username.return_value = mock_user

    response = client.post("/api/v1/auth/login", json={"username": "huy_dev", "password": password})

    assert response.status_code == 200
    assert "access_token" in response.json["data"]
    assert response.json["data"]["ma_vai_tro"] == 1


# ==========================================
# 2. CASE ÂM (NEGATIVE CASES)
# ==========================================

def test_auth_validation_errors(client):
    """Case Âm: Pydantic chặn dữ liệu đầu vào không hợp lệ"""
    # Username < 4 ký tự, Password < 6 ký tự
    invalid_payload = {"username": "huy", "password": "123"}

    response = client.post("/api/v1/auth/register", json=invalid_payload)
    assert response.status_code == 400
    assert len(response.json["errors"]) == 2  # Báo 2 lỗi validate


@patch(MOCK_AUTH_REPO)
@patch(MOCK_DB_SESSION)
def test_register_duplicate_username(mock_db, mock_repo_class, client):
    """Case Âm: Bị chặn khi đăng ký trùng username đã có trong hệ thống"""
    mock_repo_instance = mock_repo_class.return_value
    mock_repo_instance.get_user_by_username.return_value = {"id": 99, "username": "huy_dev"}

    payload = {"username": "huy_dev", "password": "newpassword123"}
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json["message"] == "Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác!"


@patch(MOCK_AUTH_REPO)
@patch(MOCK_DB_SESSION)
def test_login_wrong_password(mock_db, mock_repo_class, client):
    """Case Âm: Sai mật khẩu (Tài khoản tồn tại nhưng checkpw fail)"""
    real_password = "correct_password"
    hashed_pw = bcrypt.hashpw(real_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    mock_user = MagicMock(id=1, username="huy_dev", password=hashed_pw)
    mock_repo_class.return_value.get_user_by_username.return_value = mock_user

    payload = {"username": "huy_dev", "password": "wrong_password"}
    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 401
    assert response.json["message"] == "Tên đăng nhập hoặc mật khẩu không chính xác!"


# ==========================================
# 3. CASE BẢO MẬT & PHÂN QUYỀN (SECURITY)
# ==========================================

@patch(MOCK_AUTH_REPO)
@patch(MOCK_DB_SESSION)
def test_security_register_password_is_hashed(mock_db, mock_repo_class, client):
    """Bảo mật: Tuyệt đối KHÔNG LƯU mật khẩu gốc (plaintext) xuống Database"""
    mock_repo_instance = mock_repo_class.return_value
    mock_repo_instance.get_user_by_username.return_value = None

    # THÊM DÒNG NÀY: Giả lập DB trả về dict hợp lệ khi tạo user thành công
    mock_repo_instance.create_user.return_value = {"id": 1, "username": "new_user", "ma_vai_tro": 1}

    plain_password = "super_secret_password"
    client.post("/api/v1/auth/register", json={"username": "new_user", "password": plain_password})

    # Lấy các tham số đã truyền vào hàm create_user của Repository
    called_kwargs = mock_repo_instance.create_user.call_args[1]

    # Mật khẩu gửi xuống DB không được giống mật khẩu gốc
    assert called_kwargs["password_hash"] != plain_password
    # Mật khẩu gửi xuống phải là chuỗi băm của bcrypt
    assert called_kwargs["password_hash"].startswith("$2b$")

@patch(MOCK_AUTH_REPO)
@patch(MOCK_DB_SESSION)
def test_security_jwt_contains_correct_claims(mock_db, mock_repo_class, client):
    """Phân quyền: Đảm bảo JWT Token sinh ra chứa đúng ID và Vai Trò của User để làm thẻ bài qua cổng"""
    password = "securepassword"
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Giả lập user là nhà tuyển dụng (role 2)
    mock_user = MagicMock(id=99, username="nha_tuyen_dung", password=hashed_pw, ma_vai_tro=2)
    mock_repo_class.return_value.get_user_by_username.return_value = mock_user

    response = client.post("/api/v1/auth/login", json={"username": "nha_tuyen_dung", "password": password})

    token = response.json["data"]["access_token"]

    # Giải mã token để xem nội dung "thẻ bài" bên trong
    decoded_payload = jwt.decode(token, "test_super_secret_key", algorithms=["HS256"])

    # Đảm bảo token chứa đủ thông tin để middleware phân quyền đọc được
    assert decoded_payload["user_id"] == 99
    assert decoded_payload["ma_vai_tro"] == 2
