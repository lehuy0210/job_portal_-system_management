from datetime import datetime


class JobService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, payload: dict) -> dict:
        ten_ky_nangs = payload.pop("ten_ky_nangs", [])

        if isinstance(payload.get("han_nop"), str):
            payload["han_nop"] = datetime.strptime(payload["han_nop"], "%Y-%m-%d").date()

        new_job_id = self.repository.create_job(payload, ten_ky_nangs)

        return self.repository.get_job_by_id(new_job_id)

    def search(self, filters: dict) -> list[dict]:
        return self.repository.search_and_filter_jobs(filters)

    def update_status(self, tin_id: int, ma_trang_thai: int, user_id: int) -> bool:
        job = self.repository.get_job_by_id(tin_id)
        if not job:
            raise LookupError("Không tìm thấy tin tuyển dụng")

        if job["ma_nha_tuyen_dung"] != user_id:
            raise PermissionError("Bạn không có quyền sửa trạng thái tin này")

        return self.repository.update_job_status(tin_id, ma_trang_thai)

    def get_all_skills(self) -> list[dict]:
        return self.repository.get_all_skills()

    # --- JOB APPLICATIONS METHODS ---

    def apply_job(self, user_id: int, tin_id: int, ma_cv: int) -> dict:
        # 1. Kiem tra tin co dang mo ko
        if not self.repository.check_job_exists_and_open(tin_id):
            raise ValueError("Tin tuyển dụng không tồn tại hoặc đã đóng.")
        
        # 2. Kiem tra ma_cv co thuoc user ko
        if not self.repository.check_cv_ownership(ma_cv, user_id):
            raise ValueError("CV không tồn tại hoặc không thuộc quyền sở hữu của bạn.")
        
        # 3. Kiem tra da nop chua
        if self.repository.check_already_applied(user_id, tin_id):
            raise ValueError("Bạn đã nộp hồ sơ vào tin tuyển dụng này rồi.")
        
        # 4. Tao ho so
        ma_ho_so = self.repository.create_application(user_id, tin_id, ma_cv)
        return {"ma_ho_so": ma_ho_so, "status": "Mới nộp"}

    def get_job_applications(self, user_id: int, tin_id: int) -> list[dict]:
        # Repository function handles ownership check (throws PermissionError)
        return self.repository.get_applications_by_job(tin_id, user_id)

    def get_my_applications(self, user_id: int) -> list[dict]:
        return self.repository.get_candidate_applications(user_id)

    def update_application_status(self, user_id: int, ma_ho_so: int, ma_trang_thai: int) -> bool:
        # Repository function handles ownership check
        return self.repository.update_app_status(ma_ho_so, ma_trang_thai, user_id)
