import os
from pydantic import BaseModel, Field

from src.ai_engine.ocr.extractor import DocumentExtractor
from src.ai_engine.parsers.cv_parser import CVParser
from src.ai_engine.matching.scorer import CandidateJobScorer

class CVExtractRequestDTO(BaseModel):
    file_path: str | None = None
    raw_text: str | None = None

class CandidateScoreBreakdownDTO(BaseModel):
    skill_score: float
    experience_score: float
    semantic_score: float
    matched_skill_ids: list[int] = Field(default_factory=list)
    missing_skill_ids: list[int] = Field(default_factory=list)

class CandidateRankingDTO(BaseModel):
    ma_ho_so: int
    ma_ung_vien: int
    ho_ten: str
    email: str
    so_dien_thoai: str | None = None
    ma_cv: int
    so_nam_kinh_nghiem: int
    total_score: float
    breakdown: CandidateScoreBreakdownDTO

class JobRecommendationDTO(BaseModel):
    tin_id: int
    tieu_de: str
    ten_cong_ty: str | None = None
    dia_chi: str | None = None
    luong: int | None = None
    so_nam_kinh_nghiem_yeu_cau: int | None = None
    total_score: float
    breakdown: CandidateScoreBreakdownDTO

class ScreeningService:
    def __init__(self, repository, scorer=None, parser=None, extractor=None):
        self.repository = repository
        self.scorer = scorer or CandidateJobScorer()
        self.parser = parser or CVParser
        self.extractor = extractor or DocumentExtractor

    def extract_and_save_cv(self, ma_cv: int, data: CVExtractRequestDTO = None, file_path: str = None, raw_text: str = None) -> dict:
        cv = self.repository.get_cv_by_id(ma_cv)
        if not cv:
            raise LookupError(f"CV #{ma_cv} not found")

        req_raw_text = data.raw_text if data else raw_text
        req_file_path = data.file_path if data else file_path

        text_content = ""
        if req_raw_text and req_raw_text.strip():
            text_content = req_raw_text.strip()
        else:
            target_path = req_file_path or cv.get("duong_dan")
            if target_path and os.path.exists(target_path):
                text_content = self.extractor.extract_text(target_path)
            else:
                existing_parts = [cv.get("tom_tat") or "", cv.get("hoc_van") or "", cv.get("kinh_nghiem_lam_viec") or ""]
                text_content = " ".join([p for p in existing_parts if p.strip()])

        all_skills = self.repository.get_all_skills()
        parsed = self.parser.parse_cv_text(text_content, all_skills)

        update_payload = {
            "tom_tat": parsed["tom_tat"] or cv.get("tom_tat") or "",
            "hoc_van": parsed["hoc_van"] or cv.get("hoc_van") or "",
            "kinh_nghiem_lam_viec": parsed["kinh_nghiem_lam_viec"] or cv.get("kinh_nghiem_lam_viec") or ""
        }
        self.repository.update_cv_extracted_data(ma_cv, update_payload, parsed["matched_skill_ids"])

        status_id = self.repository.get_status_id("Đã trích xuất", 1)
        if status_id:
            pass

        return {
            "ma_cv": ma_cv,
            "extracted_data": {
                **update_payload,
                "so_nam_kinh_nghiem": parsed["so_nam_kinh_nghiem"],
                "matched_skills": parsed["matched_skill_names"],
                "matched_skill_ids": parsed["matched_skill_ids"]
            }
        }

    def screen_candidates_for_job(self, tin_id: int) -> dict:
        job = self.repository.get_job_by_id(tin_id)
        if not job:
            raise LookupError(f"Job #{tin_id} not found")

        applications = self.repository.get_applications_for_job(tin_id)
        ranked_candidates = []

        matched_status_id = self.repository.get_status_id("Đã khớp & xếp hạng", 1)

        for app in applications:
            cv_text = f"{app.get('tom_tat', '')} {app.get('kinh_nghiem_lam_viec', '')}"
            exp_years = self.parser._extract_experience_years(cv_text)

            cv_data = {
                "skill_ids": app.get("skill_ids", []),
                "so_nam_kinh_nghiem": exp_years,
                "tom_tat": app.get("tom_tat", ""),
                "hoc_van": app.get("hoc_van", ""),
                "kinh_nghiem_lam_viec": app.get("kinh_nghiem_lam_viec", "")
            }

            score_result = self.scorer.calculate_score(cv_data, job)

            if matched_status_id:
                self.repository.update_application_status(app["ma_ho_so"], matched_status_id)

            candidate_dto = CandidateRankingDTO(
                ma_ho_so=app["ma_ho_so"],
                ma_ung_vien=app["ma_ung_vien"],
                ho_ten=app["ho_ten"],
                email=app["email"],
                so_dien_thoai=app.get("so_dien_thoai"),
                ma_cv=app["ma_cv"],
                so_nam_kinh_nghiem=exp_years,
                total_score=score_result["total_score"],
                breakdown=score_result["breakdown"]
            )
            ranked_candidates.append(candidate_dto.model_dump())

        ranked_candidates.sort(key=lambda x: x["total_score"], reverse=True)

        return {
            "tin_id": tin_id,
            "tieu_de": job["tieu_de"],
            "total_candidates": len(ranked_candidates),
            "candidates": ranked_candidates
        }

    def recommend_jobs_for_cv(self, ma_cv: int, top_n: int = 5) -> dict:
        cv = self.repository.get_cv_by_id(ma_cv)
        if not cv:
            raise LookupError(f"CV #{ma_cv} not found")

        open_jobs = self.repository.get_open_jobs()
        scored_jobs = []

        cv_text = f"{cv.get('tom_tat', '')} {cv.get('kinh_nghiem_lam_viec', '')}"
        cv_exp = self.parser._extract_experience_years(cv_text)

        cv_data = {
            "skill_ids": cv.get("skill_ids", []),
            "so_nam_kinh_nghiem": cv_exp,
            "tom_tat": cv.get("tom_tat", ""),
            "hoc_van": cv.get("hoc_van", ""),
            "kinh_nghiem_lam_viec": cv.get("kinh_nghiem_lam_viec", "")
        }

        for job in open_jobs:
            score_result = self.scorer.calculate_score(cv_data, job)
            job_dto = JobRecommendationDTO(
                tin_id=job["tin_id"],
                tieu_de=job["tieu_de"],
                ten_cong_ty=job.get("ten_cong_ty"),
                dia_chi=job.get("dia_chi"),
                luong=job.get("luong"),
                so_nam_kinh_nghiem_yeu_cau=job.get("so_nam_kinh_nghiem"),
                total_score=score_result["total_score"],
                breakdown=score_result["breakdown"]
            )
            scored_jobs.append(job_dto.model_dump())

        scored_jobs.sort(key=lambda x: x["total_score"], reverse=True)

        return {
            "ma_cv": ma_cv,
            "total_matches": len(scored_jobs),
            "recommended_jobs": scored_jobs[:top_n]
        }
