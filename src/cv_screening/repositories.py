from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date

class ScreeningRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_skills(self) -> list[dict]:
        query = text("SELECT ma_ky_nang, ten_ky_nang FROM ky_nang")
        rows = self.db.execute(query).fetchall()
        return [dict(r._mapping) for r in rows]

    def get_cv_by_id(self, ma_cv: int) -> dict | None:
        query = text("SELECT * FROM cv WHERE ma_cv = :ma_cv")
        cv = self.db.execute(query, {"ma_cv": ma_cv}).fetchone()
        if not cv:
            return None

        cv_dict = dict(cv._mapping)
        if isinstance(cv_dict.get("ngay_tao"), date):
            cv_dict["ngay_tao"] = cv_dict["ngay_tao"].isoformat()
        if isinstance(cv_dict.get("ngay_sua"), date):
            cv_dict["ngay_sua"] = cv_dict["ngay_sua"].isoformat()

        skills_query = text("""
            SELECT k.ma_ky_nang, k.ten_ky_nang 
            FROM ky_nang k 
            JOIN cv_ky_nang ck ON k.ma_ky_nang = ck.ma_ky_nang 
            WHERE ck.ma_cv = :ma_cv
        """)
        skills = self.db.execute(skills_query, {"ma_cv": ma_cv}).fetchall()
        cv_dict["ky_nangs"] = [dict(s._mapping) for s in skills]
        cv_dict["skill_ids"] = [s["ma_ky_nang"] for s in cv_dict["ky_nangs"]]
        return cv_dict

    def update_cv_extracted_data(self, ma_cv: int, payload: dict, skill_ids: list[int] = None):
        query = text("""
            UPDATE cv 
            SET tom_tat = :tom_tat, hoc_van = :hoc_van, kinh_nghiem_lam_viec = :kinh_nghiem_lam_viec, ngay_sua = NOW()
            WHERE ma_cv = :ma_cv
        """)
        self.db.execute(query, {
            "ma_cv": ma_cv,
            "tom_tat": payload.get("tom_tat"),
            "hoc_van": payload.get("hoc_van"),
            "kinh_nghiem_lam_viec": payload.get("kinh_nghiem_lam_viec")
        })

        if skill_ids:
            delete_skills = text("DELETE FROM cv_ky_nang WHERE ma_cv = :ma_cv")
            self.db.execute(delete_skills, {"ma_cv": ma_cv})

            for skill_id in skill_ids:
                insert_skill = text("INSERT INTO cv_ky_nang (ma_cv, ma_ky_nang) VALUES (:ma_cv, :ma_ky_nang)")
                self.db.execute(insert_skill, {"ma_cv": ma_cv, "ma_ky_nang": skill_id})

        self.db.commit()

    def get_job_by_id(self, tin_id: int) -> dict | None:
        query = text("SELECT * FROM tin_tuyen_dung WHERE tin_id = :tin_id")
        job = self.db.execute(query, {"tin_id": tin_id}).fetchone()
        if not job:
            return None

        job_dict = dict(job._mapping)
        if isinstance(job_dict.get("han_nop"), date):
            job_dict["han_nop"] = job_dict["han_nop"].isoformat()

        skills_query = text("""
            SELECT k.ma_ky_nang, k.ten_ky_nang 
            FROM ky_nang k 
            JOIN tin_tuyen_dung_ky_nang tk ON k.ma_ky_nang = tk.ma_ky_nang 
            WHERE tk.tin_id = :tin_id
        """)
        skills = self.db.execute(skills_query, {"tin_id": tin_id}).fetchall()
        job_dict["ky_nangs"] = [dict(s._mapping) for s in skills]
        job_dict["skill_ids"] = [s["ma_ky_nang"] for s in job_dict["ky_nangs"]]
        return job_dict

    def get_applications_for_job(self, tin_id: int) -> list[dict]:
        query = text("""
            SELECT h.ma_ho_so, h.ngay_nop, h.ma_ung_vien, h.tin_id, h.ma_cv, h.ma_trang_thai,
                   u.ho_ten, u.email, u.so_dien_thoai,
                   c.tom_tat, c.hoc_van, c.kinh_nghiem_lam_viec, c.duong_dan
            FROM ho_so_ung_tuyen h
            JOIN ung_vien u ON h.ma_ung_vien = u.ma_ung_vien
            JOIN cv c ON h.ma_cv = c.ma_cv
            WHERE h.tin_id = :tin_id
        """)
        rows = self.db.execute(query, {"tin_id": tin_id}).fetchall()

        result = []
        for r in rows:
            app_dict = dict(r._mapping)
            if isinstance(app_dict.get("ngay_nop"), date):
                app_dict["ngay_nop"] = app_dict["ngay_nop"].isoformat()

            skills_query = text("""
                SELECT k.ma_ky_nang, k.ten_ky_nang 
                FROM ky_nang k 
                JOIN cv_ky_nang ck ON k.ma_ky_nang = ck.ma_ky_nang 
                WHERE ck.ma_cv = :ma_cv
            """)
            skills = self.db.execute(skills_query, {"ma_cv": app_dict["ma_cv"]}).fetchall()
            app_dict["ky_nangs"] = [dict(s._mapping) for s in skills]
            app_dict["skill_ids"] = [s["ma_ky_nang"] for s in app_dict["ky_nangs"]]
            result.append(app_dict)

        return result

    def update_application_status(self, ma_ho_so: int, ma_trang_thai: int):
        query = text("UPDATE ho_so_ung_tuyen SET ma_trang_thai = :ma_trang_thai WHERE ma_ho_so = :ma_ho_so")
        self.db.execute(query, {"ma_ho_so": ma_ho_so, "ma_trang_thai": ma_trang_thai})
        self.db.commit()

    def get_open_jobs(self) -> list[dict]:
        query = text("""
            SELECT t.*, c.ten_cong_ty, n.ten_nha_tuyen_dung 
            FROM tin_tuyen_dung t
            JOIN nha_tuyen_dung n ON t.ma_nha_tuyen_dung = n.ma_nha_tuyen_dung
            LEFT JOIN cong_ty c ON n.ma_nha_tuyen_dung = c.ma_nha_tuyen_dung
            WHERE t.ma_trang_thai = 8
            ORDER BY t.tin_id DESC
        """)
        jobs = self.db.execute(query).fetchall()

        result = []
        for j in jobs:
            j_dict = dict(j._mapping)
            if isinstance(j_dict.get("han_nop"), date):
                j_dict["han_nop"] = j_dict["han_nop"].isoformat()

            skills_query = text("""
                SELECT k.ma_ky_nang, k.ten_ky_nang 
                FROM ky_nang k 
                JOIN tin_tuyen_dung_ky_nang tk ON k.ma_ky_nang = tk.ma_ky_nang 
                WHERE tk.tin_id = :tin_id
            """)
            skills = self.db.execute(skills_query, {"tin_id": j_dict["tin_id"]}).fetchall()
            j_dict["ky_nangs"] = [dict(s._mapping) for s in skills]
            j_dict["skill_ids"] = [s["ma_ky_nang"] for s in j_dict["ky_nangs"]]
            result.append(j_dict)

        return result

    def get_status_id(self, ten_trang_thai: str, ma_doi_tuong: int) -> int | None:
        query = text("SELECT ma_trang_thai FROM trang_thai WHERE ten_trang_thai = :name AND ma_doi_tuong = :obj LIMIT 1")
        row = self.db.execute(query, {"name": ten_trang_thai, "obj": ma_doi_tuong}).fetchone()
        return row[0] if row else None
