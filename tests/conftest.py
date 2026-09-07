import pytest
from src.index import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_skills():
    return [
        {"ma_ky_nang": 1, "ten_ky_nang": "Python"},
        {"ma_ky_nang": 2, "ten_ky_nang": "SQL"},
        {"ma_ky_nang": 3, "ten_ky_nang": "Docker"},
        {"ma_ky_nang": 4, "ten_ky_nang": "React"},
        {"ma_ky_nang": 5, "ten_ky_nang": "Flask"}
    ]

@pytest.fixture
def sample_cv_text():
    return """
    Nguyen Van A
    Email: nguyenvana@example.com
    Dien thoai: 0912345678
    
    Tom tat:
    Lap trinh vien Backend voi 3 nam kinh nghiem lam viec voi Python, Flask va MySQL.
    
    Hoc van:
    Cu nhan Cong nghe thong tin - Dai hoc Bach Khoa (2018 - 2022).
    
    Kinh nghiem lam viec:
    2022 - Nay: Cong ty Tech Solutions
    - Phat trien cac he thong REST API su dung Python va Flask.
    - Toi uu hoa truy van database MySQL va trien khai service voi Docker.
    """

@pytest.fixture
def sample_job():
    return {
        "tin_id": 1,
        "tieu_de": "Senior Python Backend Engineer",
        "mo_ta": "Phat trien RESTful APIs su dung Python va Flask, lam viec voi co so du lieu SQL va Docker.",
        "so_nam_kinh_nghiem": 2,
        "skill_ids": [1, 2, 3],
        "dia_chi": "Ha Noi",
        "luong": 25000000
    }
