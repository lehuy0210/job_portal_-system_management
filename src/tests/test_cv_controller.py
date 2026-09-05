import pytest
from flask import Flask, request
from unittest.mock import patch


# --- GIẢ LẬP MIDDLEWARE PHÂN QUYỀN ---
def mock_token_required_with_user(user_id=1):
    def decorator(f):
        def wrapper(*args, **kwargs):
            request.current_user = {"user_id": user_id}
            return f(*args, **kwargs)

        wrapper.__name__ = f.__name__
        return wrapper

    return decorator


# Khởi tạo mock trước khi import blueprint
patch("src.common.middleware.token_required", mock_token_required_with_user(user_id=1)).start()
from src.cv_management.controllers import cv_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(cv_bp)
    app.testing = True
    with app.test_client() as client:
        yield client


MOCK_DB_SESSION = "src.cv_management.controllers.get_db_session"
MOCK_CV_SERVICE = "src.cv_management.controllers.CVService"


# ==========================================
# 1. CASE ÂM (NEGATIVE CASES) - KIỂM TRA VALIDATION
# ==========================================

def test_create_cv_empty_strings(client):
    """Lỗi: Gửi dữ liệu là chuỗi rỗng (vi phạm min_length=1)"""
    invalid_payload = {
        "tom_tat": "",
        "duong_dan": "  ",
        "source": "",
        "hoc_van": "",
        "kinh_nghiem_lam_viec": ""
    }
    response = client.post("/api/v1/cv/", json=invalid_payload)
    assert response.status_code == 400
    assert "errors" in response.json
    # Pydantic sẽ báo lỗi String should have at least 1 characters


def test_create_cv_missing_required_fields(client):
    """Lỗi: Thiếu hoàn toàn các trường bắt buộc"""
    response = client.post("/api/v1/cv/", json={})
    assert response.status_code == 400
    assert len(response.json["errors"]) == 5  # Báo thiếu 5 trường


def test_update_cv_invalid_data_type(client):
    """Lỗi: Gửi sai kiểu dữ liệu (vd: số thay vì chuỗi)"""
    invalid_payload = {"hoc_van": 12345}
    response = client.put("/api/v1/cv/1", json=invalid_payload)
    assert response.status_code == 400


@patch(MOCK_CV_SERVICE)
@patch(MOCK_DB_SESSION)
def test_update_cv_not_found(mock_db, mock_service, client):
    """Lỗi: Cập nhật CV không tồn tại trong DB"""
    mock_service.return_value.update.side_effect = LookupError("CV không tồn tại")
    response = client.put("/api/v1/cv/999", json={"tom_tat": "Update"})
    assert response.status_code == 404
    assert response.json["message"] == "CV không tồn tại"


# ==========================================
# 2. CASE NGHIỆP VỤ (BUSINESS LOGIC)
# ==========================================

@patch(MOCK_CV_SERVICE)
@patch(MOCK_DB_SESSION)
def test_get_cv_empty_list(mock_db, mock_service, client):
    """Nghiệp vụ: Ứng viên chưa tạo CV nào, trả về mảng rỗng"""
    mock_service.return_value.get_by_ung_vien.return_value = []
    response = client.get("/api/v1/cv/ung-vien")
    assert response.status_code == 200
    assert response.json["data"] == []


@patch(MOCK_CV_SERVICE)
@patch(MOCK_DB_SESSION)
def test_update_cv_no_changes(mock_db, mock_service, client):
    """Nghiệp vụ: Gửi payload rỗng hoặc update nhưng data không đổi"""
    mock_service.return_value.update.return_value = 0  # 0 rows updated
    response = client.put("/api/v1/cv/1", json={})
    assert response.status_code == 200
    assert response.json["message"] == "Không có gì thay đổi"


@patch(MOCK_CV_SERVICE)
@patch(MOCK_DB_SESSION)
def test_update_cv_partial_success(mock_db, mock_service, client):
    """Nghiệp vụ: Chỉ cập nhật 1 trường (Partial Update), các trường khác giữ nguyên"""
    mock_service.return_value.update.return_value = 1
    response = client.put("/api/v1/cv/1", json={"tom_tat": "Tóm tắt mới"})

    assert response.status_code == 200
    assert response.json["message"] == "Cập nhật thành công"
    # Đã sửa: Thêm user_id = 1 vào hàm assert để khớp với controller mới
    mock_service.return_value.update.assert_called_with(
        1, 1,
        {'tom_tat': 'Tóm tắt mới', 'duong_dan': None, 'source': None, 'hoc_van': None, 'kinh_nghiem_lam_viec': None}
    )


# ==========================================
# 3. CASE PHÂN QUYỀN (AUTHORIZATION & SECURITY)
# ==========================================

@patch(MOCK_CV_SERVICE)
@patch(MOCK_DB_SESSION)
def test_create_cv_binds_correct_user(mock_db, mock_service, client):
    """Phân quyền: Đảm bảo CV được tạo bắt buộc gắn với user_id của token đang đăng nhập"""
    mock_service_instance = mock_service.return_value
    mock_service_instance.create.return_value = {"ma_cv": 1}

    valid_payload = {
        "tom_tat": "Dev", "duong_dan": "link",
        "source": "web", "hoc_van": "ĐH", "kinh_nghiem_lam_viec": "1 năm"
    }
    response = client.post("/api/v1/cv/", json=valid_payload)

    assert response.status_code == 201
    # Kiểm tra xem payload truyền vào service.create có bị ép cứng ma_ung_vien từ token không
    called_payload = mock_service_instance.create.call_args[0][0]
    assert called_payload["ma_ung_vien"] == 1


@patch(MOCK_CV_SERVICE)
@patch(MOCK_DB_SESSION)
def test_update_cv_cross_account_idor(mock_db, mock_service, client):
    """
    Phân quyền (BẢO MẬT): User 1 cố tình sửa CV của User 2.
    Test này kỳ vọng API phải chặn lại và trả về 403.
    """
    # Ép Service ném ra lỗi PermissionError khi gọi update
    mock_service_instance = mock_service.return_value
    mock_service_instance.update.side_effect = PermissionError("Bạn không có quyền sửa CV này")

    # Gửi request mạo danh
    response = client.put("/api/v1/cv/2", json={"tom_tat": "Người lạ đang cố sửa"})

    # Kiểm tra API phải trả về đúng mã 403 Forbidden và lời nhắn chặn
    assert response.status_code == 403
    assert response.json["message"] == "Bạn không có quyền sửa CV này"
