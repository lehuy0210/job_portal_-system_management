from pydantic import BaseModel, Field


class UngVienProfileDTO(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    gioi_tinh: str = Field(..., pattern="^(Nam|Nữ|Khác)$")
    so_dien_thoai: str = Field(..., min_length=9, max_length=20)
    ngay_sinh: str = Field(...)
    dia_chi: str = Field(..., min_length=5)


class UngVienService:
    def __init__(self, repository):
        self.repository = repository

    def get_profile(self, ma_ung_vien: int):
        return self.repository.get_by_id(ma_ung_vien)

    def save_profile(self, ma_ung_vien: int, data: dict):
        return self.repository.upsert_profile(ma_ung_vien, data)
