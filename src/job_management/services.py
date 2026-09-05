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
