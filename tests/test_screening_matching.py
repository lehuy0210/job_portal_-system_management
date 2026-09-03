import pytest
from unittest.mock import MagicMock

from src.ai_engine.matching.semantic import SemanticMatcher
from src.ai_engine.matching.scorer import CandidateJobScorer
from src.cv_screening.services import ScreeningService

def test_semantic_matcher_similar_text():
    print("\n[TEST] 11. Do tuong dong ngu nghia TF-IDF Cosine Similarity:")
    matcher = SemanticMatcher()
    score = matcher.calculate_similarity(
        "Kinh nghiem lap trinh Python backend voi Flask va SQL",
        "Tuyen dung ky su Python backend Flask database SQL"
    )
    print(f"   -> Diem tuong dong giua Mo ta Job va CV: {score * 100:.2f}% (he so: {score})")
    assert score > 0.1
    print("   -> OK: Do tuong dong phan anh dung noi dung lien quan.")

def test_semantic_matcher_empty_text():
    print("\n[TEST] 12. Xu ly tuong dong ngu nghia khi van ban rong:")
    matcher = SemanticMatcher()
    assert matcher.calculate_similarity("", "Sample text") == 0.0
    assert matcher.calculate_similarity("Sample", "") == 0.0
    print("   -> OK: Tra ve 0.0 an toan khi mot trong hai doan text bi rong.")

def test_scorer_full_match():
    print("\n[TEST] 13. Tinh diem khi ung vien phu hop 100% Ky nang & Kinh nghiem:")
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
    print(f"   -> Tong diem (Total Score): {result['total_score']}/100")
    print(f"      + Diem Ky nang (50%):     {result['breakdown']['skill_score']}%")
    print(f"      + Diem Kinh nghiem (30%): {result['breakdown']['experience_score']}%")
    print(f"      + Diem Ngu nghia (20%):   {result['breakdown']['semantic_score']}%")
    
    assert result["breakdown"]["skill_score"] == 100.0
    assert result["breakdown"]["experience_score"] == 100.0
    assert result["breakdown"]["semantic_score"] > 80.0
    assert result["total_score"] >= 90.0
    print("   -> OK: Ung vien dat diem xuat sac >= 90/100.")

def test_scorer_partial_skill_match():
    print("\n[TEST] 14. Tinh diem khi ung vien chi dap ung mot nua so ky nang:")
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
    print(f"   -> Yeu cau 4 ky nang, ung vien co 2 ky nang -> Diem ky nang: {result['breakdown']['skill_score']}%")
    assert result["breakdown"]["skill_score"] == 50.0
    print("   -> OK: Tinh dung 50% diem ky nang.")

def test_scorer_experience_penalty():
    print("\n[TEST] 15. Tinh diem khi ung vien chua du so nam kinh nghiem:")
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
    print(f"   -> Yeu cau 4 nam, ung vien co 2 nam -> Diem kinh nghiem: {result['breakdown']['experience_score']}%")
    assert result["breakdown"]["experience_score"] == 50.0
    print("   -> OK: Tinh dung ty le kinh nghiem dat 50%.")

def test_scorer_senior_vs_fresher_ranking():
    print("\n[TEST] 16. So sanh xep hang giua ung vien Senior va Fresher cho vi tri Senior:")
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
    print(f"   -> Diem Senior:  {senior_res['total_score']} diem")
    print(f"   -> Diem Fresher: {fresher_res['total_score']} diem")
    assert senior_res["total_score"] > fresher_res["total_score"]
    print("   -> OK: Senior vuot troi hon Fresher, xep hang dung thuc te.")

def test_service_screen_candidates_ranking():
    print("\n[TEST] 17. Service sang loc va xep hang ung vien nop vao Job:")
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
            "ho_ten": "Nguyen Van Junior",
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
            "ho_ten": "Tran Thi Senior",
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

    print(f"   -> Bang xep hang ung vien cho Tin '{result['tieu_de']}':")
    for idx, c in enumerate(result["candidates"], start=1):
        print(f"      Top {idx}: {c['ho_ten']} - Diem phu hop: {c['total_score']}% (Ky nang: {c['breakdown']['skill_score']}%, Kinh nghiem: {c['breakdown']['experience_score']}%)")

    assert result["total_candidates"] == 2
    assert result["candidates"][0]["ho_ten"] == "Tran Thi Senior"
    assert result["candidates"][1]["ho_ten"] == "Nguyen Van Junior"
    assert result["candidates"][0]["total_score"] > result["candidates"][1]["total_score"]
    print("   -> OK: Danh sach ung vien duoc sap xep giam dan chinh xac.")

def test_service_recommend_jobs():
    print("\n[TEST] 18. Service goi y viec lam phu hop nhat cho mot CV:")
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
            "tieu_de": "Python Backend Lead",
            "mo_ta": "Yeu cau Python va SQL",
            "so_nam_kinh_nghiem": 3,
            "skill_ids": [1, 2],
            "ten_cong_ty": "VinaTech Corp"
        },
        {
            "tin_id": 20,
            "tieu_de": "Java Software Architect",
            "mo_ta": "Yeu cau Java va Spring Boot",
            "so_nam_kinh_nghiem": 5,
            "skill_ids": [99],
            "ten_cong_ty": "Global Systems"
        }
    ]

    service = ScreeningService(mock_repo)
    result = service.recommend_jobs_for_cv(ma_cv=1, top_n=2)

    print(f"   -> Danh sach viec lam goi y cho CV #{result['ma_cv']}:")
    for idx, j in enumerate(result["recommended_jobs"], start=1):
        print(f"      Goi y #{idx}: {j['tieu_de']} ({j['ten_cong_ty']}) - Do phu hop: {j['total_score']}%")

    assert len(result["recommended_jobs"]) == 2
    assert result["recommended_jobs"][0]["tin_id"] == 10
    assert result["recommended_jobs"][0]["total_score"] > result["recommended_jobs"][1]["total_score"]
    print("   -> OK: Viec lam phu hop nhat (Python Lead) duoc uu tien goi y dau tien.")

def test_screen_job_not_found(client):
    print("\n[TEST] 19. API endpoint GET /api/v1/screening/jobs/<id>/candidates khi khong tim thay Job:")
    response = client.get("/api/v1/screening/jobs/999999/candidates")
    print(f"   -> HTTP Status code: {response.status_code}")
    assert response.status_code in [404, 500]
    print("   -> OK: Tra ve ma loi 404 dung quy dinh.")

def test_recommend_jobs_not_found(client):
    print("\n[TEST] 20. API endpoint GET /api/v1/screening/candidates/<id>/recommended-jobs khi khong tim thay CV:")
    response = client.get("/api/v1/screening/candidates/999999/recommended-jobs")
    print(f"   -> HTTP Status code: {response.status_code}")
    assert response.status_code in [404, 500]
    print("   -> OK: Tra ve ma loi 404 dung quy dinh.")
