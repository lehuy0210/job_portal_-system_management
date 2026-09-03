import pytest
from unittest.mock import MagicMock

from src.ai_engine.matching.semantic import SemanticMatcher
from src.ai_engine.matching.scorer import CandidateJobScorer
from src.cv_screening.services import ScreeningService

def test_semantic_matcher_similar_text():
    matcher = SemanticMatcher()
    score = matcher.calculate_similarity(
        "Kinh nghiem lap trinh Python backend voi Flask va SQL",
        "Tuyen dung ky su Python backend Flask database SQL"
    )
    assert score > 0.1

def test_semantic_matcher_empty_text():
    matcher = SemanticMatcher()
    assert matcher.calculate_similarity("", "Sample text") == 0.0
    assert matcher.calculate_similarity("Sample", "") == 0.0

def test_scorer_full_match():
    scorer = CandidateJobScorer()
    job = {
        "skill_ids": [1, 2],
        "so_nam_kinh_nghiem": 2,
        "tieu_de": "Python Dev",
        "mo_ta": "Lap trinh he thong Python va SQL"
    }
    cv = {
        "skill_ids": [1, 2],
        "so_nam_kinh_nghiem": 3,
        "tom_tat": "Python Dev",
        "kinh_nghiem_lam_viec": "Lap trinh he thong Python va SQL",
        "hoc_van": ""
    }

    result = scorer.calculate_score(cv, job)
    assert result["breakdown"]["skill_score"] == 100.0
    assert result["breakdown"]["experience_score"] == 100.0
    assert result["breakdown"]["semantic_score"] > 80.0
    assert result["total_score"] >= 90.0

def test_scorer_partial_skill_match():
    scorer = CandidateJobScorer()
    job = {
        "skill_ids": [1, 2, 3, 4],
        "so_nam_kinh_nghiem": 2,
        "tieu_de": "Fullstack",
        "mo_ta": "Job description"
    }
    cv = {
        "skill_ids": [1, 2],
        "so_nam_kinh_nghiem": 2,
        "tom_tat": "",
        "kinh_nghiem_lam_viec": "",
        "hoc_van": ""
    }

    result = scorer.calculate_score(cv, job)
    assert result["breakdown"]["skill_score"] == 50.0

def test_scorer_experience_penalty():
    scorer = CandidateJobScorer()
    job = {
        "skill_ids": [],
        "so_nam_kinh_nghiem": 4,
        "tieu_de": "Senior",
        "mo_ta": ""
    }
    cv = {
        "skill_ids": [],
        "so_nam_kinh_nghiem": 2,
        "tom_tat": "",
        "kinh_nghiem_lam_viec": "",
        "hoc_van": ""
    }

    result = scorer.calculate_score(cv, job)
    assert result["breakdown"]["experience_score"] == 50.0

def test_scorer_senior_vs_fresher_ranking():
    scorer = CandidateJobScorer()
    job = {
        "skill_ids": [1, 2],
        "so_nam_kinh_nghiem": 3,
        "tieu_de": "Senior Python",
        "mo_ta": "Python SQL developer"
    }
    senior_cv = {
        "skill_ids": [1, 2],
        "so_nam_kinh_nghiem": 4,
        "tom_tat": "Senior engineer",
        "kinh_nghiem_lam_viec": "Python SQL developer",
        "hoc_van": ""
    }
    fresher_cv = {
        "skill_ids": [1],
        "so_nam_kinh_nghiem": 0,
        "tom_tat": "Fresher",
        "kinh_nghiem_lam_viec": "Student project",
        "hoc_van": ""
    }

    senior_res = scorer.calculate_score(senior_cv, job)
    fresher_res = scorer.calculate_score(fresher_cv, job)
    assert senior_res["total_score"] > fresher_res["total_score"]

def test_service_screen_candidates_ranking():
    mock_repo = MagicMock()
    mock_repo.get_job_by_id.return_value = {
        "tin_id": 1,
        "tieu_de": "Python Dev",
        "mo_ta": "Python SQL",
        "so_nam_kinh_nghiem": 2,
        "skill_ids": [1, 2]
    }
    mock_repo.get_status_id.return_value = 3
    mock_repo.get_applications_for_job.return_value = [
        {
            "ma_ho_so": 101,
            "ma_ung_vien": 1,
            "ho_ten": "Candidate Junior",
            "email": "junior@test.com",
            "so_dien_thoai": "0123",
            "ma_cv": 1,
            "skill_ids": [1],
            "tom_tat": "Junior",
            "kinh_nghiem_lam_viec": "1 nam",
            "hoc_van": ""
        },
        {
            "ma_ho_so": 102,
            "ma_ung_vien": 2,
            "ho_ten": "Candidate Senior",
            "email": "senior@test.com",
            "so_dien_thoai": "0456",
            "ma_cv": 2,
            "skill_ids": [1, 2],
            "tom_tat": "Senior",
            "kinh_nghiem_lam_viec": "3 nam kinh nghiem Python SQL",
            "hoc_van": ""
        }
    ]

    service = ScreeningService(mock_repo)
    result = service.screen_candidates_for_job(tin_id=1)

    assert result["total_candidates"] == 2
    assert result["candidates"][0]["ho_ten"] == "Candidate Senior"
    assert result["candidates"][1]["ho_ten"] == "Candidate Junior"
    assert result["candidates"][0]["total_score"] > result["candidates"][1]["total_score"]

def test_service_recommend_jobs():
    mock_repo = MagicMock()
    mock_repo.get_cv_by_id.return_value = {
        "ma_cv": 1,
        "skill_ids": [1, 2],
        "tom_tat": "Python Engineer",
        "kinh_nghiem_lam_viec": "3 nam kinh nghiem Python va SQL",
        "hoc_van": ""
    }
    mock_repo.get_open_jobs.return_value = [
        {
            "tin_id": 10,
            "tieu_de": "Python Lead",
            "mo_ta": "Yeu cau Python va SQL",
            "so_nam_kinh_nghiem": 3,
            "skill_ids": [1, 2],
            "ten_cong_ty": "Company A"
        },
        {
            "tin_id": 20,
            "tieu_de": "Java Architect",
            "mo_ta": "Yeu cau Java va Spring",
            "so_nam_kinh_nghiem": 5,
            "skill_ids": [99],
            "ten_cong_ty": "Company B"
        }
    ]

    service = ScreeningService(mock_repo)
    result = service.recommend_jobs_for_cv(ma_cv=1, top_n=2)

    assert len(result["recommended_jobs"]) == 2
    assert result["recommended_jobs"][0]["tin_id"] == 10
    assert result["recommended_jobs"][0]["total_score"] > result["recommended_jobs"][1]["total_score"]

def test_screen_job_not_found(client):
    response = client.get("/api/v1/screening/jobs/999999/candidates")
    assert response.status_code in [404, 500]

def test_recommend_jobs_not_found(client):
    response = client.get("/api/v1/screening/candidates/999999/recommended-jobs")
    assert response.status_code in [404, 500]
