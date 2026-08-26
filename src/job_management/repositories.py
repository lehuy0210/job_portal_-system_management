from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


class JobRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_job(self, payload: dict, ten_ky_nangs: list[str] = None) -> int:
        query = text("""
                     INSERT INTO tin_tuyen_dung (tieu_de, mo_ta, han_nop, luong, dia_chi, so_nam_kinh_nghiem,
                                                 ma_nha_tuyen_dung, ma_trang_thai)
                     VALUES (:tieu_de, :mo_ta, :han_nop, :luong, :dia_chi, :so_nam_kinh_nghiem, :ma_nha_tuyen_dung,
                             :ma_trang_thai)
                     """)

        result = self.db.execute(
            query,
            {
                "tieu_de": payload["tieu_de"],
                "mo_ta": payload["mo_ta"],
                "han_nop": payload["han_nop"],
                "luong": payload.get("luong"),
                "dia_chi": payload.get("dia_chi"),
                "so_nam_kinh_nghiem": payload.get("so_nam_kinh_nghiem"),
                "ma_nha_tuyen_dung": payload["ma_nha_tuyen_dung"],
                "ma_trang_thai": payload["ma_trang_thai"],
            },
        )

        tin_id = result.lastrowid

        if ten_ky_nangs:
            for ten in ten_ky_nangs:
                ten = ten.strip()
                if not ten:
                    continue

                check_query = text("SELECT ma_ky_nang FROM ky_nang WHERE ten_ky_nang = :ten")
                row = self.db.execute(check_query, {"ten": ten}).fetchone()

                if row:
                    ma_ky_nang = row[0]
                else:
                    insert_skill = text("INSERT INTO ky_nang (ten_ky_nang) VALUES (:ten)")
                    res = self.db.execute(insert_skill, {"ten": ten})
                    ma_ky_nang = res.lastrowid

                skill_query = text("""
                                   INSERT INTO tin_tuyen_dung_ky_nang (tin_id, ma_ky_nang)
                                   VALUES (:tin_id, :ma_ky_nang)
                                   """)
                self.db.execute(skill_query, {"tin_id": tin_id, "ma_ky_nang": ma_ky_nang})

        self.db.commit()
        return tin_id

    def get_job_by_id(self, tin_id: int) -> dict | None:
        query = text("SELECT * FROM tin_tuyen_dung WHERE tin_id = :tin_id")
        job = self.db.execute(query, {"tin_id": tin_id}).fetchone()
        if not job:
            return None

        job_dict = dict(job._mapping)

        if isinstance(job_dict.get("han_nop"), (date, date)):
            job_dict["han_nop"] = job_dict["han_nop"].isoformat()

        skills_query = text("""
            SELECT k.ma_ky_nang, k.ten_ky_nang
            FROM ky_nang k
            JOIN tin_tuyen_dung_ky_nang tk ON k.ma_ky_nang = tk.ma_ky_nang
            WHERE tk.tin_id = :tin_id
        """)
        skills = self.db.execute(skills_query, {"tin_id": tin_id}).fetchall()
        job_dict["ky_nangs"] = [dict(s._mapping) for s in skills]

        return job_dict

    def search_and_filter_jobs(self, filters: dict) -> list[dict]:
        base_query = """
            SELECT DISTINCT t.tin_id, t.tieu_de, t.mo_ta, t.han_nop, t.luong, t.dia_chi,
                            t.so_nam_kinh_nghiem, t.ma_nha_tuyen_dung, t.ma_trang_thai,
                            c.ten_cong_ty, n.ten_nha_tuyen_dung
            FROM tin_tuyen_dung t
            JOIN nha_tuyen_dung n ON t.ma_nha_tuyen_dung = n.ma_nha_tuyen_dung
            LEFT JOIN cong_ty c ON n.ma_nha_tuyen_dung = c.ma_nha_tuyen_dung
            LEFT JOIN tin_tuyen_dung_ky_nang tk ON t.tin_id = tk.tin_id
            WHERE 1=1
        """
        params = {}

        if filters.get("keyword"):
            base_query += " AND (t.tieu_de LIKE :keyword OR t.mo_ta LIKE :keyword)"
            params["keyword"] = f"%{filters['keyword']}%"

        if filters.get("ma_trang_thai") is not None:
            base_query += " AND t.ma_trang_thai = :ma_trang_thai"
            params["ma_trang_thai"] = filters["ma_trang_thai"]

        if filters.get("dia_chi"):
            base_query += " AND t.dia_chi LIKE :dia_chi"
            params["dia_chi"] = f"%{filters['dia_chi']}%"

        if filters.get("min_experience") is not None:
            base_query += " AND t.so_nam_kinh_nghiem >= :min_experience"
            params["min_experience"] = filters["min_experience"]
        if filters.get("max_experience") is not None:
            base_query += " AND t.so_nam_kinh_nghiem <= :max_experience"
            params["max_experience"] = filters["max_experience"]

        if filters.get("min_salary") is not None:
            base_query += " AND t.luong >= :min_salary"
            params["min_salary"] = filters["min_salary"]
        if filters.get("max_salary") is not None:
            base_query += " AND t.luong <= :max_salary"
            params["max_salary"] = filters["max_salary"]

        if filters.get("skill_ids"):
            skill_ids = filters["skill_ids"]
            placeholders = []
            for i, sid in enumerate(skill_ids):
                key = f"skill_id_{i}"
                placeholders.append(f":{key}")
                params[key] = sid
            base_query += f" AND tk.ma_ky_nang IN ({', '.join(placeholders)})"

        base_query += " ORDER BY t.tin_id DESC"

        jobs = self.db.execute(text(base_query), params).fetchall()

        result = []
        for j in jobs:
            j_dict = dict(j._mapping)

            if isinstance(j_dict.get("han_nop"), (date, date)):
                j_dict["han_nop"] = j_dict["han_nop"].isoformat()

            skills_query = text("""
                SELECT k.ma_ky_nang, k.ten_ky_nang
                FROM ky_nang k
                JOIN tin_tuyen_dung_ky_nang tk ON k.ma_ky_nang = tk.ma_ky_nang
                WHERE tk.tin_id = :tin_id
            """)
            skills = self.db.execute(skills_query, {"tin_id": j_dict["tin_id"]}).fetchall()
            j_dict["ky_nangs"] = [dict(s._mapping) for s in skills]

            result.append(j_dict)

        return result

    def update_job_status(self, tin_id: int, ma_trang_thai: int) -> bool:
        query = text("""
                     UPDATE tin_tuyen_dung
                     SET ma_trang_thai = :ma_trang_thai
                     WHERE tin_id = :tin_id
                     """)
        result = self.db.execute(query, {"tin_id": tin_id, "ma_trang_thai": ma_trang_thai})
        self.db.commit()
        return result.rowcount > 0

    def get_all_skills(self) -> list[dict]:
        query = text("SELECT ma_ky_nang, ten_ky_nang FROM ky_nang")
        rows = self.db.execute(query).fetchall()
        return [dict(row._mapping) for row in rows]
