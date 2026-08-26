# Hướng dẫn sử dụng API Tuyển dụng (Job Management)

Base URL: `http://127.0.0.1:5000/api/v1/jobs`

---

## 1. API Đăng tin tuyển dụng

Dùng để tạo mới một tin đăng tuyển dụng trong hệ thống.

* **Method:** `POST`
* **Path:** `/`
* **Headers:** `Content-Type: application/json`

### Body Request mẫu:
```json
{
  "tieu_de": "Lập trình viên Python (Flask/MySQL)",
  "mo_ta": "Xây dựng các REST API backend, tối ưu hóa câu lệnh MySQL và thiết kế hệ thống.",
  "han_nop": "2026-10-31",
  "luong": 25000000,
  "dia_chi": "Cầu Giấy, Hà Nội",
  "so_nam_kinh_nghiem": 2,
  "ma_nha_tuyen_dung": 1,
  "ma_trang_thai": 8,
  "ky_nangs": [1, 2]
}
```

### Response mẫu (201 Created):
```json
{
  "data": {
    "tin_id": 12,
    "tieu_de": "Lập trình viên Python (Flask/MySQL)",
    "mo_ta": "Xây dựng các REST API backend, tối ưu hóa câu lệnh MySQL và thiết kế hệ thống.",
    "han_nop": "2026-10-31",
    "luong": 25000000,
    "dia_chi": "Cầu Giấy, Hà Nội",
    "so_nam_kinh_nghiem": 2,
    "ma_nha_tuyen_dung": 1,
    "ma_trang_thai": 8,
    "ky_nangs": [
      {
        "ma_ky_nang": 1,
        "ten_ky_nang": "Python"
      },
      {
        "ma_ky_nang": 2,
        "ten_ky_nang": "SQL"
      }
    ]
  }
}
```

---

## 2. API Tìm kiếm và Lọc tin tuyển dụng

Dùng để lọc danh sách các tin tuyển dụng theo các tiêu chí khác nhau. Trả về danh sách được sắp xếp theo tin mới nhất ở đầu.

* **Method:** `GET`
* **Path:** `/search`

### Các Query Parameters hỗ trợ (Tùy chọn):
| Parameter | Kiểu dữ liệu | Mô tả | Ví dụ |
|---|---|---|---|
| `keyword` | String | Tìm theo từ khóa trong tiêu đề/mô tả | `?keyword=Python` |
| `dia_chi` | String | Tìm theo địa điểm | `?dia_chi=Hà Nội` |
| `min_experience` | Integer | Số năm kinh nghiệm tối thiểu | `?min_experience=1` |
| `max_experience` | Integer | Số năm kinh nghiệm tối đa | `?max_experience=3` |
| `min_salary` | Integer | Mức lương tối thiểu | `?min_salary=15000000` |
| `max_salary` | Integer | Mức lương tối đa | `?max_salary=30000000` |
| `ma_trang_thai` | Integer | Lọc theo ID trạng thái | `?ma_trang_thai=8` |
| `skill_ids` | String (ids cách nhau bởi dấu phẩy) | Lọc tin chứa bất kỳ kỹ năng nào | `?skill_ids=1,2,3` |

### URL gọi mẫu:
`GET http://127.0.0.1:5000/api/v1/jobs/search?keyword=Python&dia_chi=Hà Nội&min_experience=2&skill_ids=1,2`

### Response mẫu (200 OK):
```json
{
  "data": [
    {
      "tin_id": 12,
      "tieu_de": "Lập trình viên Python (Flask/MySQL)",
      "mo_ta": "Xây dựng các REST API backend, tối ưu hóa câu lệnh MySQL và thiết kế hệ thống.",
      "han_nop": "2026-10-31",
      "luong": 25000000,
      "dia_chi": "Cầu Giấy, Hà Nội",
      "so_nam_kinh_nghiem": 2,
      "ma_nha_tuyen_dung": 1,
      "ma_trang_thai": 8,
      "ten_nha_tuyen_dung": "Nguyễn Văn A",
      "ten_cong_ty": "VinaTech Corp",
      "ky_nangs": [
        {
          "ma_ky_nang": 1,
          "ten_ky_nang": "Python"
        },
        {
          "ma_ky_nang": 2,
          "ten_ky_nang": "SQL"
        }
      ]
    }
  ]
}
```
