from sqlalchemy import text
from sqlalchemy.orm import Session


class AdminRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_users(self) -> list[dict]:
        query = text("""
            SELECT u.id, u.username, u.ma_vai_tro,
                   CASE WHEN n.ma_nha_tuyen_dung IS NOT NULL THEN 1 ELSE 0 END as has_profile
            FROM nguoi_dung u
            LEFT JOIN nha_tuyen_dung n ON u.id = n.ma_nha_tuyen_dung
            ORDER BY u.id DESC
        """)
        rows = self.db.execute(query).fetchall()
        return [dict(row._mapping) for row in rows]

    def insert_account(self, payload: dict) -> int:
        query = text("""
            INSERT INTO nguoi_dung (username, password, ma_vai_tro)
            VALUES (:username, :password, :ma_vai_tro)
        """)
        result = self.db.execute(query, payload)
        self.db.commit()
        return result.lastrowid

    def insert_nha_tuyen_dung(self, ma_nha_tuyen_dung: int) -> int:
        query = text("""
            INSERT INTO nha_tuyen_dung (ma_nha_tuyen_dung, ten_nha_tuyen_dung, email, so_dien_thoai)
            VALUES (:ma, :ten, :email, :sdt)
        """)
        self.db.execute(
            query,
            {
                "ma": ma_nha_tuyen_dung,
                "ten": f"Công ty chưa cập nhật ({ma_nha_tuyen_dung})",
                "email": f"chua_co_{ma_nha_tuyen_dung}@email.com",
                "sdt": "0000000000",
            },
        )
        self.db.commit()
        return ma_nha_tuyen_dung

    def insert_cong_ty(self, payload: dict) -> int:
        query = text("""
                     INSERT INTO cong_ty (ten_cong_ty, ma_so_thue, mo_ta, dia_chi, ma_nha_tuyen_dung)
                     VALUES (:ten_cong_ty, :ma_so_thue, :mo_ta, :dia_chi, :ma_nha_tuyen_dung)
                     """)

        result = self.db.execute(
            query,
            {
                "ten_cong_ty": payload["ten_cong_ty"],
                "ma_so_thue": payload.get("ma_so_thue"),
                "mo_ta": payload.get("mo_ta"),
                "dia_chi": payload.get("dia_chi"),
                "ma_nha_tuyen_dung": payload["ma_nha_tuyen_dung"],
            },
        )
        self.db.commit()

        return result.lastrowid
