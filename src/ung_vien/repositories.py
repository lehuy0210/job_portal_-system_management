from sqlalchemy import text


class UngVienRepository:
    def __init__(self, db_session):
        self.db = db_session

    def get_by_id(self, ma_ung_vien: int):
        query = text("SELECT * FROM ung_vien WHERE ma_ung_vien = :ma_ung_vien")
        row = self.db.execute(query, {"ma_ung_vien": ma_ung_vien}).fetchone()
        return dict(row._mapping) if row else None

    def upsert_profile(self, ma_ung_vien: int, payload: dict):
        existing = self.get_by_id(ma_ung_vien)

        if existing:
            query = text("""
                UPDATE ung_vien
                SET ho_ten = :ho_ten,
                    email = :email,
                    gioi_tinh = :gioi_tinh,
                    so_dien_thoai = :so_dien_thoai,
                    ngay_sinh = :ngay_sinh,
                    dia_chi = :dia_chi
                WHERE ma_ung_vien = :ma_ung_vien
            """)
        else:
            query = text("""
                INSERT INTO ung_vien (ma_ung_vien, ho_ten, email, gioi_tinh, so_dien_thoai, ngay_sinh, dia_chi)
                VALUES (:ma_ung_vien, :ho_ten, :email, :gioi_tinh, :so_dien_thoai, :ngay_sinh, :dia_chi)
            """)

        params = {"ma_ung_vien": ma_ung_vien, **payload}
        self.db.execute(query, params)
        self.db.commit()
        return ma_ung_vien
