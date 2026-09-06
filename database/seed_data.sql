-- =================================================================
-- SEED DATA - HỆ THỐNG QUẢN LÝ CV & TUYỂN DỤNG
-- Mục đích: Test đầy đủ tất cả chức năng
-- 
-- Tài khoản test (tất cả dùng chung password: admin123):
--   Admin    : admin
--   NTD 1    : congty_tech   (VinaTech Corp)
--   NTD 2    : congty_edu    (EduSoft Vietnam)
--   Ứng viên 1: nguyen_van_a (3 năm Python)
--   Ứng viên 2: tran_thi_b   (5 năm Java)
--   Ứng viên 3: le_van_c     (1 năm fresher)
-- =================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------------------
-- 1. NGUOI_DUNG
--    admin (id=1) đã có sẵn trong schema
--    Thêm: NTD (id=2,3), ứng viên (id=4,5,6)
--    Hash bcrypt dưới đây tương ứng password: admin123
-- -----------------------------------------------------------------
INSERT INTO nguoi_dung (username, password, ma_vai_tro) VALUES
  ('congty_tech',  '$2b$12$hEOLfsnzYuyx0o79mSg6WOqqSLic5w62bbz55J0ZcRQbMjLDf73du', 2),
  ('congty_edu',   '$2b$12$hEOLfsnzYuyx0o79mSg6WOqqSLic5w62bbz55J0ZcRQbMjLDf73du', 2),
  ('nguyen_van_a', '$2b$12$hEOLfsnzYuyx0o79mSg6WOqqSLic5w62bbz55J0ZcRQbMjLDf73du', 1),
  ('tran_thi_b',   '$2b$12$hEOLfsnzYuyx0o79mSg6WOqqSLic5w62bbz55J0ZcRQbMjLDf73du', 1),
  ('le_van_c',     '$2b$12$hEOLfsnzYuyx0o79mSg6WOqqSLic5w62bbz55J0ZcRQbMjLDf73du', 1);

-- -----------------------------------------------------------------
-- 2. NHÀ TUYỂN DỤNG
-- -----------------------------------------------------------------
INSERT INTO nha_tuyen_dung (ma_nha_tuyen_dung, ten_nha_tuyen_dung, email, so_dien_thoai) VALUES
  (2, 'Trần Văn Nam', 'ntd.vinatech@example.com', '0901234567'),
  (3, 'Lê Thị Hoa',  'ntd.edusoft@example.com',  '0912345678');

-- -----------------------------------------------------------------
-- 3. CÔNG TY
-- -----------------------------------------------------------------
INSERT INTO cong_ty (ten_cong_ty, ma_so_thue, mo_ta, dia_chi, ma_nha_tuyen_dung) VALUES
  ('VinaTech Corp',
   '0100000001',
   'Công ty phần mềm hàng đầu chuyên phát triển giải pháp ERP và ứng dụng web.',
   'Số 10 Láng Hạ, Đống Đa, Hà Nội',
   2),
  ('EduSoft Vietnam',
   '0100000002',
   'Công ty EdTech chuyên xây dựng nền tảng học trực tuyến và quản lý giáo dục.',
   'Lầu 5, 123 Nguyễn Huệ, Quận 1, TP.HCM',
   3);

-- -----------------------------------------------------------------
-- 4. ỨNG VIÊN
-- -----------------------------------------------------------------
INSERT INTO ung_vien (ma_ung_vien, ho_ten, email, gioi_tinh, so_dien_thoai, ngay_sinh, dia_chi) VALUES
  (4, 'Nguyễn Văn A', 'nguyen.van.a@gmail.com', 'Nam', '0977111222', '1997-05-15', 'Cầu Giấy, Hà Nội'),
  (5, 'Trần Thị B',   'tran.thi.b@gmail.com',  'Nữ', '0977333444', '1994-08-20', 'Quận 3, TP.HCM'),
  (6, 'Lê Văn C',     'le.van.c@gmail.com',    'Nam', '0977555666', '2000-11-10', 'Bình Thạnh, TP.HCM');

-- -----------------------------------------------------------------
-- 5. KỸ NĂNG (master data)
-- -----------------------------------------------------------------
INSERT INTO ky_nang (ten_ky_nang) VALUES
  ('Python'),           -- id=1
  ('SQL'),              -- id=2
  ('Flask'),            -- id=3
  ('Docker'),           -- id=4
  ('REST API'),         -- id=5
  ('Java'),             -- id=6
  ('Spring Boot'),      -- id=7
  ('JavaScript'),       -- id=8
  ('React'),            -- id=9
  ('Node.js'),          -- id=10
  ('Git'),              -- id=11
  ('Linux'),            -- id=12
  ('Machine Learning'), -- id=13
  ('PostgreSQL'),       -- id=14
  ('Redis');            -- id=15

-- -----------------------------------------------------------------
-- 6. CV (nội dung thực tế để test trích xuất AI)
-- -----------------------------------------------------------------
INSERT INTO cv (ma_cv, tom_tat, duong_dan, source, hoc_van, kinh_nghiem_lam_viec, so_nam_kinh_nghiem, ngay_tao, ngay_sua, ma_ung_vien) VALUES
(
  1,
  'Nguyễn Văn A - Python Backend Developer với 3 năm kinh nghiệm. Chuyên xây dựng REST API và microservices với Flask, FastAPI. Đam mê tối ưu hiệu năng hệ thống.',
  '/uploads/cv/cv_nguyen_van_a.pdf',
  'upload',
  'Cử nhân Công nghệ Thông tin - Đại học Bách Khoa Hà Nội (2015-2019).',
  '2021 - 2024: Python Backend Developer tại ABC Tech. Phát triển REST API với Flask, Docker, Linux.\n2019 - 2021: Junior Python Developer tại XYZ Corp. Xây dựng script automation và ETL pipeline.',
  3,
  NOW(), NOW(), 4
),
(
  2,
  'Trần Thị B - Java Senior Developer, 5 năm kinh nghiệm xây dựng hệ thống enterprise. Thành thạo Spring Boot, Microservices. Kinh nghiệm lead team 5 người.',
  '/uploads/cv/cv_tran_thi_b.pdf',
  'upload',
  'Thạc sĩ Khoa học Máy tính - Đại học Quốc gia TP.HCM (2014-2018).',
  '2019 - 2024: Senior Java Developer tại DEF Solutions. Thiết kế microservices với Spring Boot, SQL, Docker.\n2017 - 2019: Java Developer tại GHI Corp. Phát triển ứng dụng web Java EE, REST API.',
  5,
  NOW(), NOW(), 5
),
(
  3,
  'Lê Văn C - Fresher lập trình viên JavaScript/React. Tốt nghiệp loại Giỏi ngành CNTT. Có kinh nghiệm thực tập 6 tháng tại startup công nghệ.',
  '/uploads/cv/cv_le_van_c.pdf',
  'upload',
  'Cử nhân Kỹ thuật Phần mềm - Đại học FPT (2019-2023), GPA 3.5/4.0.',
  '2023 - 2024: Thực tập sinh Frontend tại JKL Startup. Phát triển UI với React, JavaScript, tích hợp REST API với Node.js, Git.',
  1,
  NOW(), NOW(), 6
);

-- -----------------------------------------------------------------
-- 7. KỸ NĂNG CỦA CV
-- -----------------------------------------------------------------
INSERT INTO cv_ky_nang (ma_cv, ma_ky_nang) VALUES
  -- CV 1 - Nguyễn Văn A: Python, SQL, Flask, Docker, REST API, Git, Linux
  (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 11), (1, 12),
  -- CV 2 - Trần Thị B: Java, Spring Boot, SQL, Docker, REST API, Git, Redis
  (2, 6), (2, 7), (2, 2), (2, 4), (2, 5), (2, 11), (2, 15),
  -- CV 3 - Lê Văn C: JavaScript, React, Node.js, Git, REST API
  (3, 8), (3, 9), (3, 10), (3, 11), (3, 5);

-- -----------------------------------------------------------------
-- 8. TIN TUYỂN DỤNG
--    ma_trang_thai: 7=Nháp | 8=Đang mở | 9=Tạm dừng | 10=Đã đóng
-- -----------------------------------------------------------------
INSERT INTO tin_tuyen_dung (tin_id, tieu_de, mo_ta, han_nop, min_salary, max_salary, dia_chi, so_nam_kinh_nghiem, ma_nha_tuyen_dung, ma_trang_thai) VALUES
(1,
  'Python Backend Developer (Senior)',
  'VinaTech tuyển Python Backend Developer có kinh nghiệm xây dựng hệ thống phân tán, REST API. Thành thạo Python, Flask, SQL, Docker. Kinh nghiệm Linux/Cloud là lợi thế. Phúc lợi: 13 tháng lương, bảo hiểm sức khỏe, WFH 2 ngày/tuần.',
  '2026-12-31', 20000000, 35000000, 'Đống Đa, Hà Nội', 3, 2, 8),
(2,
  'Java Spring Boot Developer',
  'EduSoft tuyển Java Developer xây dựng backend cho nền tảng e-learning. Yêu cầu: Java, Spring Boot, SQL, REST API, Docker. Kinh nghiệm microservices là ưu tiên. Startup năng động, cơ hội thăng tiến nhanh.',
  '2026-12-31', 18000000, 30000000, 'Quận 1, TP.HCM', 2, 3, 8),
(3,
  'Frontend Developer (React)',
  'VinaTech tuyển Frontend Developer phát triển dashboard quản trị nội bộ. Yêu cầu: React, JavaScript, REST API, Git. Fresher/Junior đều có thể ứng tuyển. Hỗ trợ mentor 1-1.',
  '2026-12-31', 10000000, 18000000, 'Đống Đa, Hà Nội', 0, 2, 8),
(4,
  'Data Engineer / ML Engineer',
  'VinaTech mở rộng team AI, tuyển Data Engineer. Yêu cầu: Python, SQL, Machine Learning, Docker. Kinh nghiệm Spark, Kafka là lợi thế. Lương cạnh tranh, dự án thú vị.',
  '2026-12-31', 25000000, 45000000, 'Đống Đa, Hà Nội', 2, 2, 8),
(5,
  'Full Stack Node.js Developer',
  'EduSoft tuyển Full Stack Developer xây dựng tính năng mới cho nền tảng học trực tuyến. Yêu cầu: Node.js, React, SQL, REST API, Git. Remote-friendly.',
  '2026-12-31', 15000000, 25000000, 'Remote / TP.HCM', 1, 3, 8),
(6,
  'DevOps Engineer (Tạm dừng)',
  'Vị trí DevOps đang tạm dừng tuyển dụng. Docker, Linux, Git, Redis.',
  '2026-12-31', 20000000, 40000000, 'Hà Nội', 2, 2, 9),
(7,
  'Backend PHP Developer (Đã đóng)',
  'Vị trí đã đóng tuyển dụng.',
  '2025-06-30', 12000000, 20000000, 'Hà Nội', 1, 2, 10);

-- -----------------------------------------------------------------
-- 9. KỸ NĂNG YÊU CẦU CỦA TIN TUYỂN DỤNG
-- -----------------------------------------------------------------
INSERT INTO tin_tuyen_dung_ky_nang (tin_id, ma_ky_nang) VALUES
  -- Tin 1 - Python Senior: Python, SQL, Flask, Docker, REST API, Linux
  (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 12),
  -- Tin 2 - Java Spring Boot: Java, Spring Boot, SQL, REST API, Docker
  (2, 6), (2, 7), (2, 2), (2, 5), (2, 4),
  -- Tin 3 - Frontend React: JavaScript, React, REST API, Git
  (3, 8), (3, 9), (3, 5), (3, 11),
  -- Tin 4 - ML Engineer: Python, SQL, Machine Learning, Docker
  (4, 1), (4, 2), (4, 13), (4, 4),
  -- Tin 5 - Full Stack Node.js: Node.js, React, SQL, REST API, Git
  (5, 10), (5, 9), (5, 2), (5, 5), (5, 11),
  -- Tin 6 - DevOps: Docker, Linux, Git, Redis
  (6, 4), (6, 12), (6, 11), (6, 15);

-- -----------------------------------------------------------------
-- 10. HỒ SƠ ỨNG TUYỂN
--     ma_trang_thai: 1=Mới nộp | 2=Đã trích xuất | 6=Từ chối
-- -----------------------------------------------------------------
INSERT INTO ho_so_ung_tuyen (ma_ho_so, ngay_nop, ma_ung_vien, tin_id, ma_cv, ma_trang_thai) VALUES
  -- Nguyễn Văn A (CV1) nộp Tin 1 (Python) - đã trích xuất → test sàng lọc Tin 1
  (1, NOW(), 4, 1, 1, 2),
  -- Trần Thị B (CV2) nộp Tin 1 (Python) - mới nộp → cũng hiện khi sàng lọc Tin 1
  (2, NOW(), 5, 1, 2, 1),
  -- Nguyễn Văn A (CV1) nộp Tin 4 (ML) - mới nộp
  (3, NOW(), 4, 4, 1, 1),
  -- Trần Thị B (CV2) nộp Tin 2 (Java) - đã trích xuất
  (4, NOW(), 5, 2, 2, 2),
  -- Lê Văn C (CV3) nộp Tin 3 (Frontend) - mới nộp
  (5, NOW(), 6, 3, 3, 1),
  -- Lê Văn C (CV3) nộp Tin 5 (Node.js) - đã trích xuất
  (6, NOW(), 6, 5, 3, 2),
  -- Trần Thị B (CV2) nộp Tin 3 (Frontend) - bị TỪ CHỐI → test filter, không hiện khi sàng lọc
  (7, NOW(), 5, 3, 2, 6);

SET FOREIGN_KEY_CHECKS = 1;

-- =================================================================
-- HƯỚNG DẪN TEST TỪNG CHỨC NĂNG
-- =================================================================

-- ▶ AUTH
-- POST /api/v1/auth/login  { "username": "nguyen_van_a", "password": "admin123" }
-- POST /api/v1/auth/login  { "username": "congty_tech",  "password": "admin123" }
-- POST /api/v1/auth/login  { "username": "admin",        "password": "admin123" }

-- ▶ PROFILE ỨNG VIÊN (cần token ứng viên)
-- GET  /api/v1/ung-vien/profile
-- POST /api/v1/ung-vien/profile

-- ▶ QUẢN LÝ CV (cần token ứng viên)
-- GET    /api/v1/cv/ung-vien
-- POST   /api/v1/cv/
-- PUT    /api/v1/cv/1
-- DELETE /api/v1/cv/1

-- ▶ QUẢN LÝ TIN TUYỂN DỤNG
-- GET  /api/v1/jobs/skills
-- GET  /api/v1/jobs/search
-- GET  /api/v1/jobs/search?ma_trang_thai=8           → chỉ tin Đang mở (5 tin)
-- GET  /api/v1/jobs/search?keyword=Python
-- GET  /api/v1/jobs/search?skill_ids=1,3             → Python + Flask
-- GET  /api/v1/jobs/search?min_salary=20000000
-- PUT  /api/v1/jobs/6/status  { "ma_trang_thai": 8 } → mở lại Tin 6 (cần token NTD)

-- ▶ CV SCREENING
-- POST /api/v1/screening/extract/1   → Trích xuất CV Nguyễn Văn A
-- POST /api/v1/screening/extract/2   → Trích xuất CV Trần Thị B
-- POST /api/v1/screening/extract/3   → Trích xuất CV Lê Văn C
-- 
-- GET  /api/v1/screening/jobs/1/candidates → Sàng lọc Tin 1 (Python)
--      → Kỳ vọng: Nguyễn Văn A (100% kỹ năng) xếp trên Trần Thị B (0% kỹ năng)
-- GET  /api/v1/screening/jobs/2/candidates → Sàng lọc Tin 2 (Java)
--      → Chỉ có Trần Thị B (100% kỹ năng Java)
-- GET  /api/v1/screening/jobs/3/candidates → Sàng lọc Tin 3 (Frontend React)
--      → Chỉ có Lê Văn C (hồ sơ Trần Thị B bị Từ chối → không hiện)
-- 
-- GET  /api/v1/screening/candidates/1/recommended-jobs?top_n=5
--      → Gợi ý việc cho CV 1 (Python): Tin 1 nên score cao nhất
-- GET  /api/v1/screening/candidates/3/recommended-jobs?top_n=5
--      → Gợi ý việc cho CV 3 (React): Tin 3, Tin 5 nên score cao nhất

-- ▶ ADMIN
-- GET  /api/v1/admin/users
-- POST /api/v1/admin/insert-account { "username": "test_ntd", "password": "abc123", "ma_vai_tro": 2 }
-- POST /api/v1/admin/insert-nha-tuyen-dung { "ma_nha_tuyen_dung": <id vừa tạo> }
-- POST /api/v1/admin/insert-cong-ty { "ma_nha_tuyen_dung": <id>, "ten_cong_ty": "Test Corp" }
