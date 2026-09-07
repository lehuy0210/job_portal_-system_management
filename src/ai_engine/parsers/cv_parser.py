import re
from datetime import datetime

class CVParser:
    @staticmethod
    def parse_cv_text(text: str, available_skills: list[dict] = None) -> dict:
        if not text:
            return {
                "tom_tat": "",
                "hoc_van": "",
                "kinh_nghiem_lam_viec": "",
                "so_nam_kinh_nghiem": 0,
                "matched_skill_ids": [],
                "matched_skill_names": []
            }

        matched_ids = []
        matched_names = []
        if available_skills:
            text_lower = text.lower()
            for skill in available_skills:
                skill_name = skill.get("ten_ky_nang", "")
                if not skill_name:
                    continue

                lower_skill = skill_name.lower()
                if lower_skill == "sql":
                    pattern = r'(?<!\w)(sql|mysql|postgresql|sqlite|plsql|t-sql)(?!\w)'
                else:
                    pattern = r'(?<!\w)' + re.escape(lower_skill) + r'(?!\w)'

                if re.search(pattern, text_lower):
                    matched_ids.append(skill.get("ma_ky_nang"))
                    matched_names.append(skill_name)

        sections = CVParser._extract_sections(text)
        exp_years = CVParser._extract_experience_years(text, exp_text=sections.get("experience", ""))

        return {
            "tom_tat": sections.get("summary", ""),
            "hoc_van": sections.get("education", ""),
            "kinh_nghiem_lam_viec": sections.get("experience", ""),
            "so_nam_kinh_nghiem": exp_years,
            "matched_skill_ids": matched_ids,
            "matched_skill_names": matched_names
        }

    @staticmethod
    def _extract_experience_years(text: str, exp_text: str = None) -> int:
        match = re.search(r'(\d+)\s*(?:\+|năm|nam|years?|yr)\s*(?:kinh nghiệm|kinh nghiem|experience)?', text, re.IGNORECASE)
        if match:
            try:
                val = int(match.group(1))
                if 0 <= val <= 40:
                    return val
            except ValueError:
                pass

        # Chi tinh ngay thang trong phan kinh nghiem lam viec chinh thuc
        target_text = exp_text if exp_text and exp_text.strip() else text

        year_ranges = re.findall(
            r'(?:[01]?\d[\/\.-])?(20\d\d|19\d\d)\s*[-–—tođến]+\s*(?:(?:[01]?\d[\/\.-])?(20\d\d)|present|hiện tại|hien tai|nay)',
            target_text,
            re.IGNORECASE
        )

        current_year = datetime.now().year
        intervals = []
        for start_str, end_str in year_ranges:
            try:
                start_yr = int(start_str)
                if any(x in end_str.lower() for x in ["present", "hiện", "hien", "nay"]):
                    end_yr = current_year
                else:
                    end_yr = int(end_str)
                if end_yr >= start_yr:
                    intervals.append((start_yr, end_yr))
            except ValueError:
                continue

        return CVParser._calculate_non_overlapping_years(intervals)

    @staticmethod
    def _calculate_non_overlapping_years(intervals: list[tuple[int, int]]) -> int:
        if not intervals:
            return 0

        # Sap xep theo nam bat dau
        intervals.sort(key=lambda x: x[0])

        # Hop nhat cac khoang thoi gian trung lap (Merge Overlapping Intervals)
        merged = [intervals[0]]
        for current_start, current_end in intervals[1:]:
            last_start, last_end = merged[-1]
            if current_start <= last_end:
                # Du an con hoac cong viec trung lap -> Gop lai, khong cong don
                merged[-1] = (last_start, max(last_end, current_end))
            else:
                merged.append((current_start, current_end))

        total_years = sum(end - start for start, end in merged)
        return min(total_years, 35)

    @staticmethod
    def _extract_sections(text: str) -> dict:
        lines = text.splitlines()
        clean_lines = [line.strip() for line in lines if line.strip()]

        summary_lines = []
        edu_lines = []
        exp_lines = []

        current_section = "intro"
        for line in clean_lines:
            lower = line.lower()
            is_header_candidate = len(line.split()) <= 6 or line.endswith(":")

            if is_header_candidate:
                if any(h in lower for h in ["học vấn", "hoc van", "education", "đào tạo", "dao tao", "bằng cấp", "bang cap"]):
                    current_section = "education"
                    continue
                # Du an ca nhan hoac ky nang/hoat dong khac duoc xep vao 'other' de khong tinh vao kinh nghiem lam viec
                elif any(h in lower for h in ["dự án cá nhân", "du an ca nhan", "personal project", "side project", "pet project"]):
                    current_section = "other"
                    continue
                elif any(h in lower for h in ["kinh nghiệm", "kinh nghiem", "experience", "lịch sử làm việc", "work history", "quá trình làm việc", "qua trinh lam viec"]):
                    current_section = "experience"
                    continue
                elif any(h in lower for h in ["mục tiêu", "muc tieu", "tóm tắt", "tom tat", "summary", "about me", "giới thiệu", "gioi thieu", "profile"]):
                    current_section = "summary"
                    continue
                elif any(h in lower for h in ["kỹ năng", "ky nang", "skills", "chứng chỉ", "chung chi", "certifications", "hoạt động", "activities"]):
                    current_section = "other"
                    continue

            if current_section in ["summary", "intro"]:
                summary_lines.append(line)
            elif current_section == "education":
                edu_lines.append(line)
            elif current_section == "experience":
                exp_lines.append(line)

        summary_text = "\n".join(summary_lines[:15]).strip()
        if not summary_text and clean_lines:
            summary_text = "\n".join(clean_lines[:6]).strip()

        return {
            "summary": summary_text,
            "education": "\n".join(edu_lines).strip(),
            "experience": "\n".join(exp_lines).strip()
        }
