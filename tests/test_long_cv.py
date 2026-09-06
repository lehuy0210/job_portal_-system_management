import pytest
from src.ai_engine.parsers.cv_parser import CVParser
from src.ai_engine.matching.scorer import CandidateJobScorer

LONG_REALISTIC_CV = """
NGUYEN HOANG LONG
Vi tri ung tuyen: Senior Python Backend Engineer
Email: hoanglong.dev@gmail.com | Dien thoai: 0987.654.321
Dia chi: Quan Cau Giay, Ha Noi | LinkedIn: linkedin.com/in/hoanglong-dev | GitHub: github.com/longdev

MUC TIEU NGHIEP VU & TOM TAT BAN THAN
Ky su phan mem Backend voi hon 5 nam kinh nghiem chuyen sau trong thiet ke kien truc microservices, phat trien cac he thong RESTful API co kha nang chiu tai cao va xu ly giao dich quy mo lon.
Co kinh nghiem thuc chien voi Python (Flask, FastAPI, Django), co so du lieu quan he PostgreSQL, MySQL va toi uu hoa he thong caching voi Redis.
Thanh thao cac quy trinh DevOps co ban gom Docker, Kubernetes, CI/CD pipelines va trien khai ha tang tren AWS.
Mong muon dong gop vao cac du an Fintech va E-commerce quy mo lon voi vai tro Backend Lead.

KY NANG CHUYEN MON
- Ngon ngu lap trinh: Python, JavaScript, SQL, Bash shell
- Web Frameworks: Flask, FastAPI, Django, Celery
- Co so du lieu: PostgreSQL, MySQL, MongoDB, Redis
- DevOps & Tools: Docker, Kubernetes, Docker-Compose, Git, GitLab CI, Linux, AWS (EC2, S3, RDS)
- Kien truc & Quy trinh: Microservices, RESTful API, Domain-Driven Design (DDD), Agile/Scrum

KINH NGHIEM LAM VIEC
01/2021 - Nay: Tech Lead / Senior Backend Engineer tai Cong ty Co phan Giai phap Thanh toan VNPAY
- Chu tri thiet ke va trien khai he thong thanh toan Microservices bang Python FastAPI va Flask, phuc vu hon 5 trieu nguoi dung voi 15,000 requests/giay vao gio cao diem.
- Truc tiep toi uu hoa truy van SQL, thiet ke database partitioning tren PostgreSQL va MySQL giup giam thoi gian phan hoi trung binh tu 350ms xuong con 85ms.
- Xay dung he thong background task va message broker su dung Celery va Redis de xu ly doi soat giao dich tu dong.
- Dong goi toan bo he thong thanh cac container Docker, thiet lap CI/CD tu dong build va deploy len cum Kubernetes.
- Huong dan (mentor) 6 thanh vien Junior va Mid-level trong team ve Clean Code va quy chuan REST API.

06/2018 - 12/2020: Backend Developer tai Cong ty FPT Software
- Tham gia phat trien du an he thong quan ly chuoi cung ung Logistic cho khach hang Nhat Ban su dung Python Flask va MySQL.
- Thiet ke va viet hon 100 endpoints RESTful API bao mat su dung JWT va OAuth2.
- Viet unit tests va integration tests dat do bao phu code coverage tren 85% bang Pytest.
- Phối hợp chat che voi doi ngu Frontend React va QA de dam bao tien do release san pham dung han.

HOC VAN
09/2014 - 06/2018: Dai hoc Bach Khoa Ha Noi
- Chuyen nganh: Cong nghe Thong tin & Khoa hoc May tinh
- Xep loai tot nghiep: Gioi (GPA: 3.45 / 4.0)
- De tai tot nghiep: Xay dung he thong phan tich va canh bao log tap trung su dung Python va Elasticsearch.

CHUNG CHI & HOAT DONG
- AWS Certified Solutions Architect - Associate (2022)
- Chung chi Tieng Anh TOEIC 850 / 990 (2020)
- Dien gia chia se ve "Building Scalable APIs with Python" tai Tech Talk Ha Noi (2023)
"""

def test_long_cv_parsing():
    print("\n=======================================================")
    print("TEST: BOCK TACH THONG TIN TU CV THUC TE (GAN 1000 TU)")
    print("=======================================================")

    mock_skills = [
        {"ma_ky_nang": 1, "ten_ky_nang": "Python"},
        {"ma_ky_nang": 2, "ten_ky_nang": "SQL"},
        {"ma_ky_nang": 3, "ten_ky_nang": "Docker"},
        {"ma_ky_nang": 4, "ten_ky_nang": "React"},
        {"ma_ky_nang": 5, "ten_ky_nang": "Flask"},
        {"ma_ky_nang": 6, "ten_ky_nang": "Java"},
        {"ma_ky_nang": 7, "ten_ky_nang": "NodeJS"}
    ]

    parsed = CVParser.parse_cv_text(LONG_REALISTIC_CV, mock_skills)

    print("\n1. KET QUA TRICH XUAT KY NANG:")
    print(f"   - Danh sach ky nang tim thay: {parsed['matched_skill_names']}")
    print(f"   - ID ky nang khop voi DB:     {parsed['matched_skill_ids']}")

    print("\n2. KET QUA TRICH XUAT SO NAM KINH NGHIEM:")
    print(f"   - So nam kinh nghiem uoc tinh: {parsed['so_nam_kinh_nghiem']} nam")

    print("\n3. PHAN TACH CAC SECTION:")
    print("   [A] Tom tat:")
    print(f"       {parsed['tom_tat'][:160]}...")
    print("   [B] Hoc van:")
    print(f"       {parsed['hoc_van'][:160]}...")
    print("   [C] Kinh nghiem lam viec:")
    print(f"       {parsed['kinh_nghiem_lam_viec'][:220]}...")

    # Assertions
    assert 1 in parsed["matched_skill_ids"]  # Python
    assert 2 in parsed["matched_skill_ids"]  # SQL (via PostgreSQL / MySQL / SQL)
    assert 3 in parsed["matched_skill_ids"]  # Docker
    assert 5 in parsed["matched_skill_ids"]  # Flask
    assert 6 not in parsed["matched_skill_ids"]  # Java khong co trong CV
    assert parsed["so_nam_kinh_nghiem"] >= 5
    assert "Dai hoc Bach Khoa" in parsed["hoc_van"]
    assert "VNPAY" in parsed["kinh_nghiem_lam_viec"]
    assert "FPT Software" in parsed["kinh_nghiem_lam_viec"]

    print("\n4. THU NGHIEM TINH DIEM VOI TIN TUYEN DUNG SENIOR PYTHON:")
    job_senior = {
        "tieu_de": "Senior Python Backend Engineer",
        "mo_ta": "Tuyen dung lap trinh vien Python co kinh nghiem Flask, SQL, Docker, xay dung he thong microservices.",
        "so_nam_kinh_nghiem": 4,
        "skill_ids": [1, 2, 3, 5]  # Python, SQL, Docker, Flask
    }

    scorer = CandidateJobScorer()
    cv_data = {
        "skill_ids": parsed["matched_skill_ids"],
        "so_nam_kinh_nghiem": parsed["so_nam_kinh_nghiem"],
        "tom_tat": parsed["tom_tat"],
        "hoc_van": parsed["hoc_van"],
        "kinh_nghiem_lam_viec": parsed["kinh_nghiem_lam_viec"]
    }
    score_result = scorer.calculate_score(cv_data, job_senior)

    print(f"   - Tong diem phu hop:         {score_result['total_score']} / 100")
    print(f"     + Diem Ky nang (50%):      {score_result['breakdown']['skill_score']}%")
    print(f"     + Diem Kinh nghiem (30%):  {score_result['breakdown']['experience_score']}%")
    print(f"     + Diem Ngu nghia (20%):    {score_result['breakdown']['semantic_score']}%")

    assert score_result["total_score"] >= 85.0
    print("\n=> KET QUA: CV DAI THUC TE DUOC TRICH XUAT VA DANH GIA CHINH XAC 100%!")
