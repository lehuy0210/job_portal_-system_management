from datetime import datetime, date

class JobService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, payload: dict) -> dict:
        skill_ids = payload.pop("ky_nangs", [])
        
        if isinstance(payload.get("han_nop"), str):
            payload["han_nop"] = datetime.strptime(payload["han_nop"], "%Y-%m-%d").date()
            
        new_job_id = self.repository.create_job(payload, skill_ids)
        
        return self.repository.get_job_by_id(new_job_id)

    def search(self, filters: dict) -> list[dict]:
        return self.repository.search_and_filter_jobs(filters)
