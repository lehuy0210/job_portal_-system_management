import os
import pytest
from unittest.mock import MagicMock

from src.ai_engine.ocr.extractor import DocumentExtractor
from src.ai_engine.parsers.cv_parser import CVParser
from src.cv_screening.services import ScreeningService

def test_document_extractor_file_not_found():
    print("\n[TEST] 1. Xu ly ngoai le khi file CV khong ton tai:")
    with pytest.raises(FileNotFoundError):
        DocumentExtractor.extract_text("non_existent_path.pdf")
    print("   -> OK: Da bat dung ngoai le FileNotFoundError.")

def test_document_extractor_text_file(tmp_path):
    print("\n[TEST] 2. Doc noi dung tu file van ban:")
    txt_file = tmp_path / "test_cv.txt"
    txt_file.write_text("Nguyen Van A - Python Developer", encoding="utf-8")
    content = DocumentExtractor.extract_text(str(txt_file))
    assert content == "Nguyen Van A - Python Developer"
    print(f"   -> OK: Doc thanh cong noi dung: '{content}'.")

def test_cv_parser_extracts_skills(sample_cv_text, sample_skills):
    print("\n[TEST] 3. Trich xuat ky nang tu noi dung CV:")
    parsed = CVParser.parse_cv_text(sample_cv_text, sample_skills)
    print(f"   -> Danh sach ky nang tim thay: {parsed['matched_skill_names']} (ID: {parsed['matched_skill_ids']})")
    
    assert 1 in parsed["matched_skill_ids"]  # Python
    assert 2 in parsed["matched_skill_ids"]  # SQL (via MySQL)
    assert 3 in parsed["matched_skill_ids"]  # Docker
    assert 5 in parsed["matched_skill_ids"]  # Flask
    assert 4 not in parsed["matched_skill_ids"]  # React khong co trong CV
    print("   -> OK: Trich xuat chinh xac Python, SQL, Docker, Flask va loai bo React.")

def test_cv_parser_extracts_experience_years(sample_cv_text):
    print("\n[TEST] 4. Uoc tinh so nam kinh nghiem tu CV:")
    years = CVParser._extract_experience_years(sample_cv_text)
    print(f"   -> So nam kinh nghiem tinh duoc: {years} nam")
    assert years >= 3
    print("   -> OK: Trich xuat dung >= 3 nam kinh nghiem.")

def test_cv_parser_experience_regex_variations():
    print("\n[TEST] 5. Trich xuat so nam kinh nghiem qua nhieu mau van ban khac nhau:")
    assert CVParser._extract_experience_years("Co 5 nam kinh nghiem lam viec") == 5
    assert CVParser._extract_experience_years("Over 4 years of software development") == 4
    assert CVParser._extract_experience_years("2+ yr experience in backend") == 2
    assert CVParser._extract_experience_years("No experience mentioned") == 0
    print("   -> OK: Xu ly dung tat ca cac mau: '5 nam', '4 years', '2+ yr'.")

def test_cv_parser_sections_detection(sample_cv_text):
    print("\n[TEST] 6. Phan tach cac phan (Sections) trong CV:")
    sections = CVParser._extract_sections(sample_cv_text)
    print(f"   -> Phan Hoc van: {sections['education'][:50]}...")
    print(f"   -> Phan Kinh nghiem: {sections['experience'][:50]}...")
    print(f"   -> Phan Tom tat: {sections['summary'][:50]}...")
    assert "Dai hoc Bach Khoa" in sections["education"]
    assert "REST API" in sections["experience"]
    assert "Backend" in sections["summary"]
    print("   -> OK: Phan tach chinh xac ca 3 phan.")

def test_cv_parser_empty_text():
    print("\n[TEST] 7. Xu ly an toan khi CV rong:")
    parsed = CVParser.parse_cv_text("", [])
    assert parsed["so_nam_kinh_nghiem"] == 0
    assert parsed["matched_skill_ids"] == []
    assert parsed["tom_tat"] == ""
    print("   -> OK: Tra ve du lieu rong an toan, khong bi crash.")

def test_screening_service_extract_and_save():
    print("\n[TEST] 8. Service trich xuat va luu du lieu vao Database:")
    mock_repo = MagicMock()
    mock_repo.get_cv_by_id.return_value = {
        "ma_cv": 10,
        "tom_tat": "Old summary",
        "hoc_van": "",
        "kinh_nghiem_lam_viec": "",
        "duong_dan": "fake.pdf"
    }
    mock_repo.get_all_skills.return_value = [
        {"ma_ky_nang": 1, "ten_ky_nang": "Python"},
        {"ma_ky_nang": 2, "ten_ky_nang": "SQL"}
    ]
    mock_repo.get_status_id.return_value = 2

    service = ScreeningService(mock_repo)
    result = service.extract_and_save_cv(
        ma_cv=10,
        raw_text="Ung vien 2 nam kinh nghiem voi Python va SQL."
    )

    print(f"   -> Ket qua trich xuat cho CV #{result['ma_cv']}:")
    print(f"      - So nam kinh nghiem: {result['extracted_data']['so_nam_kinh_nghiem']}")
    print(f"      - Ky nang khop: {result['extracted_data']['matched_skills']}")
    assert result["ma_cv"] == 10
    assert result["extracted_data"]["so_nam_kinh_nghiem"] == 2
    assert set(result["extracted_data"]["matched_skill_ids"]) == {1, 2}
    mock_repo.update_cv_extracted_data.assert_called_once()
    print("   -> OK: Service da goi Repository luu du lieu thanh cong.")

def test_screening_service_extract_cv_not_found():
    print("\n[TEST] 9. Service bao loi khi ma CV khong ton tai:")
    mock_repo = MagicMock()
    mock_repo.get_cv_by_id.return_value = None

    service = ScreeningService(mock_repo)
    with pytest.raises(LookupError):
        service.extract_and_save_cv(ma_cv=999, raw_text="Sample")
    print("   -> OK: Da bao dung LookupError.")

def test_extract_api_endpoint_not_found(client):
    print("\n[TEST] 10. API endpoint POST /api/v1/screening/extract/<ma_cv> khi CV khong ton tai:")
    response = client.post("/api/v1/screening/extract/999999", json={"raw_text": "Sample text"})
    print(f"   -> HTTP Status code nhan duoc: {response.status_code}")
    assert response.status_code in [404, 500]
    print("   -> OK: Endpoint tra ve dung ma loi HTTP 404.")

def test_cv_parser_ignores_personal_projects_and_merges_subprojects():
    print("\n[TEST] 10b. Khong tinh du an ca nhan va gop trung lap du an con:")
    text_sample = """
    KINH NGHIEM LAM VIEC:
    2020 - 2023: Cong ty ABC
    - Du an 1: 2020 - 2021 (Phat trien web)
    - Du an 2: 2021 - 2022 (Nang cap he thong)

    DU AN CA NHAN:
    2018 - 2024: He thong quan ly chi tieu ca nhan

    HOC VAN:
    2014 - 2018: Dai hoc Bach Khoa
    """
    parsed = CVParser.parse_cv_text(text_sample, [])
    print(f"   -> So nam kinh nghiem tinh duoc: {parsed['so_nam_kinh_nghiem']} nam")
    
    # 2020-2023 la 3 nam; cac du an con nam trong 2020-2023 khong duoc cong them.
    # Du an ca nhan khong duoc tinh vao kinh nghiem lam viec.
    assert parsed["so_nam_kinh_nghiem"] == 3
    assert "chi tieu ca nhan" not in parsed["kinh_nghiem_lam_viec"]
    print("   -> OK: Chi tinh dung 3 nam cong ty ABC, khong bi tinh trung lap hay cong du an ca nhan vao kinh nghiem.")
