from .semantic import SemanticMatcher

class CandidateJobScorer:
    def __init__(self):
        self.semantic_matcher = SemanticMatcher()

    def calculate_score(self, cv_data: dict, job_data: dict) -> dict:
        job_skills = set(job_data.get("skill_ids") or [])
        cv_skills = set(cv_data.get("skill_ids") or [])

        matched_skills = job_skills.intersection(cv_skills)
        missing_skills = job_skills.difference(cv_skills)

        if not job_skills:
            skill_score = 100.0
        else:
            skill_score = round((len(matched_skills) / len(job_skills)) * 100, 2)

        job_exp = job_data.get("so_nam_kinh_nghiem") or 0
        cv_exp = cv_data.get("so_nam_kinh_nghiem") or 0

        if job_exp <= 0:
            exp_score = 100.0
        elif cv_exp >= job_exp:
            exp_score = 100.0
        else:
            exp_score = round((cv_exp / job_exp) * 100, 2)

        cv_text = f"{cv_data.get('tom_tat', '')} {cv_data.get('kinh_nghiem_lam_viec', '')} {cv_data.get('hoc_van', '')}"
        job_text = f"{job_data.get('tieu_de', '')} {job_data.get('mo_ta', '')}"

        sim = self.semantic_matcher.calculate_similarity(cv_text, job_text)
        semantic_score = round(sim * 100, 2)

        total_score = round(
            0.50 * skill_score + 0.30 * exp_score + 0.20 * semantic_score,
            2
        )

        return {
            "total_score": total_score,
            "breakdown": {
                "skill_score": skill_score,
                "experience_score": exp_score,
                "semantic_score": semantic_score,
                "matched_skill_ids": list(matched_skills),
                "missing_skill_ids": list(missing_skills)
            }
        }
