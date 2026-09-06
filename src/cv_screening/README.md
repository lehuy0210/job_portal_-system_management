# Hướng dẫn sử dụng API Sàng lọc CV & Gợi ý việc làm (CV Screening)

Base URL: `http://127.0.0.1:5000/api/v1/screening`

---

## Cơ chế tính điểm phù hợp (Match Score)

$$\text{Total Score (100\%)} = \text{Skill (50\%)} + \text{Experience (30\%)} + \text{Semantic (20\%)}$$

* **Skill Score (50%):** Tỷ lệ phần trăm kỹ năng CV đáp ứng yêu cầu của tin tuyển dụng.
* **Experience Score (30%):** So sánh số năm kinh nghiệm của ứng viên với yêu cầu của tin tuyển dụng (đủ hoặc thừa nhận 100% điểm).
* **Semantic Score (20%):** Độ tương đồng ngữ nghĩa giữa mô tả công việc và phần tóm tắt / kinh nghiệm làm việc trong CV (TF-IDF Cosine Similarity).

---

## 1. API Trích xuất thông tin tự động từ CV

Dùng để đọc file CV (PDF/Text) hoặc đoạn text đầu vào, bóc tách kỹ năng, học vấn, kinh nghiệm và cập nhật vào bảng `cv`.

* **Method:** `POST`
* **Path:** `/extract/<int:ma_cv>`
* **Headers:** `Content-Type: application/json`

### Body Request mẫu:
```json
{
  "raw_text": "Họ và tên: Nguyễn Văn B\nKinh nghiệm: 3 năm làm việc vị trí Python Backend Developer.\nHọc vấn: Cử nhân Công nghệ thông tin - ĐH Bách Khoa.\nKỹ năng: Python, SQL, Docker, Flask, REST API."
}
```
*(Hoặc truyền `"file_path": "path/to/cv.pdf"` nếu muốn đọc trực tiếp từ file trên server)*

### Response mẫu (200 OK):
```json
{
  "data": {
    "ma_cv": 1,
    "extracted_data": {
      "hoc_van": "Cử nhân Công nghệ thông tin - ĐH Bách Khoa.",
      "kinh_nghiem_lam_viec": "3 năm làm việc vị trí Python Backend Developer.",
      "matched_skill_ids": [1, 2],
      "matched_skills": ["Python", "SQL"],
      "so_nam_kinh_nghiem": 3,
      "tom_tat": "Họ và tên: Nguyễn Văn B"
    }
  }
}
```

---

## 2. API Sàng lọc & Xếp hạng ứng viên theo Tin tuyển dụng

Dùng cho Nhà tuyển dụng xem danh sách ứng viên đã nộp hồ sơ vào tin tuyển dụng, được sắp xếp theo điểm phù hợp từ cao xuống thấp.

* **Method:** `GET`
* **Path:** `/jobs/<int:tin_id>/candidates`

### Response mẫu (200 OK):
```json
{
  "data": {
    "tin_id": 1,
    "tieu_de": "Lập trình viên Python Senior",
    "total_candidates": 2,
    "candidates": [
      {
        "ma_ho_so": 5,
        "ma_ung_vien": 1,
        "ho_ten": "Nguyễn Văn B",
        "email": "nguyenvanb@example.com",
        "so_dien_thoai": "0912345678",
        "ma_cv": 1,
        "so_nam_kinh_nghiem": 3,
        "total_score": 85.4,
        "breakdown": {
          "skill_score": 100.0,
          "experience_score": 100.0,
          "semantic_score": 27.0,
          "matched_skill_ids": [1, 2],
          "missing_skill_ids": []
        }
      }
    ]
  }
}
```

---

## 3. API Gợi ý việc làm phù hợp cho Ứng viên

Dùng cho Ứng viên xem danh sách các tin tuyển dụng đang mở (`Đang mở`) phù hợp nhất với CV của mình.

* **Method:** `GET`
* **Path:** `/candidates/<int:ma_cv>/recommended-jobs?top_n=5`

### Query Parameters:
* `top_n`: Số lượng công việc tối đa muốn nhận về (mặc định: 5).

### Response mẫu (200 OK):
```json
{
  "data": {
    "ma_cv": 1,
    "total_matches": 10,
    "recommended_jobs": [
      {
        "tin_id": 1,
        "tieu_de": "Lập trình viên Python Senior",
        "ten_cong_ty": "VinaTech Corp",
        "dia_chi": "Cầu Giấy, Hà Nội",
        "luong": 28000000,
        "so_nam_kinh_nghiem_yeu_cau": 3,
        "total_score": 85.4,
        "breakdown": {
          "skill_score": 100.0,
          "experience_score": 100.0,
          "semantic_score": 27.0,
          "matched_skill_ids": [1, 2],
          "missing_skill_ids": []
        }
      }
    ]
  }
}
```
