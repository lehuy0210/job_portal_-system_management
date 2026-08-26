from sqlalchemy import text


class CVRepository:
    def __init__(self, db_session):
        self.db = db_session

    def create_cv(self, payload: dict):
        query = text(
            """
			INSERT INTO cv (tom_tat, duong_dan, source, hoc_van, kinh_nghiem_lam_viec, ngay_tao, ma_ung_vien)
			VALUES (:tom_tat, :duong_dan, :source, :hoc_van, :kinh_nghiem_lam_viec, NOW(), :ma_ung_vien)
			"""
        )
        result = self.db.execute(query, payload)
        self.db.commit()
        return result.lastrowid

    def get_by_id(self, ma_cv: int):
        query = text("SELECT * FROM cv WHERE ma_cv = :ma_cv")
        return self.db.execute(query, {"ma_cv": ma_cv}).fetchone()

    def update_cv(self, ma_cv: int, payload: dict):
        set_parts = []
        params = {"ma_cv": ma_cv}
        for field, value in payload.items():
            set_parts.append(f"{field} = :{field}")
            params[field] = value

        if not set_parts:
            return 0

        query = text(f"UPDATE cv SET {', '.join(set_parts)}, ngay_sua = NOW() WHERE ma_cv = :ma_cv")  # noqa: S608
        result = self.db.execute(query, params)
        self.db.commit()
        return result.rowcount

    def delete_cv(self, ma_cv: int):
        query = text("DELETE FROM cv WHERE ma_cv = :ma_cv")
        result = self.db.execute(query, {"ma_cv": ma_cv})
        self.db.commit()
        return result.rowcount

    def get_by_ung_vien(self, user_id: int):
        query = text("""
            SELECT * FROM cv
            WHERE ma_ung_vien = :user_id
        """)
        rows = self.db.execute(query, {"user_id": user_id}).fetchall()
        return [dict(row._mapping) for row in rows]
