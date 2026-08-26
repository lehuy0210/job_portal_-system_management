from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date

class JobRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_job(self, payload: dict, skill_ids: list[int] = None) -> int:
        query = text("""
            INSERT INTO tin_tuyen_dung (tieu_de, mo_ta, han_nop, luong, dia_chi, so_nam_kinh_nghiem, ma_nha_tuyen_dung, ma_trang_thai)
            VALUES (:tieu_de, :mo_ta, :han_nop, :luong, :dia_chi, :so_nam_kinh_nghiem, :ma_nha_tuyen_dung, :ma_trang_thai)
        """)
        
        result = self.db.execute(query, {
            "tieu_de": payload["tieu_de"],
            "mo_ta": payload["mo_ta"],
            "han_nop": payload["han_nop"],
            "luong": payload.get("luong"),
            "dia_chi": payload.get("dia_chi"),
            "so_nam_kinh_nghiem": payload.get("so_nam_kinh_nghiem"),
            "ma_nha_tuyen_dung": payload["ma_nha_tuyen_dung"],
            "ma_trang_thai": payload["ma_trang_thai"]
        })
        
        tin_id = result.lastrowid
        
        if skill_ids:
            for skill_id in skill_ids:
                skill_query = text("""
                    INSERT INTO tin_tuyen_dung_ky_nang (tin_id, ma_ky_nang)
                    VALUES (:tin_id, :ma_ky_nang)
                """)
                self.db.execute(skill_query, {"tin_id": tin_id, "ma_ky_nang": skill_id})
                
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
