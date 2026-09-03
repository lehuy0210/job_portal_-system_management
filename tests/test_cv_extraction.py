import os
import pytest
from unittest.mock import MagicMock

from src.ai_engine.ocr.extractor import DocumentExtractor
from src.ai_engine.parsers.cv_parser import CVParser
from src.cv_screening.services import ScreeningService

def test_document_extractor_file_not_found():
    with pytest.raises(FileNotFoundError):
        DocumentExtractor.extract_text("non_existent_path.pdf")

def test_document_extractor_text_file(tmp_path):
    txt_file = tmp_path / "test_cv.txt"
    txt_file.write_text("Nguyen Van A - Python Developer", encoding="utf-8")
    content = DocumentExtractor.extract_text(str(txt_file))
    assert content == "Nguyen Van A - Python Developer"

def test_cv_parser_extracts_skills(sample_cv_text, sample_skills):
    parsed = CVParser.parse_cv_text(sample_cv_text, sample_skills)
    
    assert 1 in parsed["matched_skill_ids"]  # Python
    assert 2 in parsed["matched_skill_ids"]  # SQL
    assert 3 in parsed["matched_skill_ids"]  # Docker
    assert 5 in parsed["matched_skill_ids"]  # Flask
    assert 4 not in parsed["matched_skill_ids"]  # React not mentioned

def test_cv_parser_extracts_experience_years(sample_cv_text):
    years = CVParser._extract_experience_years(sample_cv_text)
    assert years >= 3

def test_cv_parser_experience_regex_variations():
    assert CVParser._extract_experience_years("Co 5 nam kinh nghiem lam viec") == 5
    assert CVParser._extract_experience_years("Over 4 years of software development") == 4
    assert CVParser._extract_experience_years("2+ yr experience in backend") == 2
    assert CVParser._extract_experience_years("No experience mentioned") == 0

def test_cv_parser_sections_detection(sample_cv_text):
    sections = CVParser._extract_sections(sample_cv_text)
    assert "Dai hoc Bach Khoa" in sections["education"]
    assert "REST API" in sections["experience"]
    assert "Backend" in sections["summary"]

def test_cv_parser_empty_text():
    parsed = CVParser.parse_cv_text("", [])
    assert parsed["so_nam_kinh_nghiem"] == 0
    assert parsed["matched_skill_ids"] == []
    assert parsed["tom_tat"] == ""

def test_screening_service_extract_and_save():
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

    assert result["ma_cv"] == 10
    assert result["extracted_data"]["so_nam_kinh_nghiem"] == 2
    assert set(result["extracted_data"]["matched_skill_ids"]) == {1, 2}
    mock_repo.update_cv_extracted_data.assert_called_once()

def test_screening_service_extract_cv_not_found():
    mock_repo = MagicMock()
    mock_repo.get_cv_by_id.return_value = None

    service = ScreeningService(mock_repo)
    with pytest.raises(LookupError):
        service.extract_and_save_cv(ma_cv=999, raw_text="Sample")

def test_extract_api_endpoint_not_found(client):
    response = client.post("/api/v1/screening/extract/999999", json={"raw_text": "Sample text"})
    assert response.status_code in [404, 500]
