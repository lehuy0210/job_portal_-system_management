import io
import os
import re
import time
import unicodedata

from flask import Blueprint, current_app, jsonify, request
from pydantic import BaseModel, Field, ValidationError
from src.common.middleware import token_required
from src.database import get_db_session
from werkzeug.utils import secure_filename

from .repositories import CVRepository
from .services import CVService

cv_bp = Blueprint("cv", __name__, url_prefix="/api/v1/cv")

# ---------------------------------------------------------------------------
# Helpers: trích xuất text từ PDF / DOCX
# ---------------------------------------------------------------------------

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """Dùng pypdf để đọc text từ file PDF."""
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _extract_text_from_docx(file_bytes: bytes) -> str:
    """Dùng python-docx để đọc text từ file DOCX."""
    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


# Từ khoá tiêu đề section phổ biến trong CV (không dấu, không khoảng trắng)
_SECTION_PATTERNS = {
    "hoc_van": re.compile(
        r"(hocvan|trinhdo|education|academic|bangcap|chuyennganh)"
    ),
    "kinh_nghiem": re.compile(
        r"(kinhnghiem|workexperience|experience|congviec|duan|project)"
    ),
    "tom_tat": re.compile(
        r"(tomtat|muctieu|objective|summary|profile|gioithieu|aboutme)"
    ),
}


def _remove_accents(input_str: str) -> str:
    """Loại bỏ dấu tiếng Việt và đưa về in thường."""
    s = unicodedata.normalize("NFD", input_str)
    return s.encode("ascii", "ignore").decode("utf-8").lower()


def _split_cv_sections(raw_text: str) -> dict:
    """
    Phân tách nội dung CV thô thành các mục:
    - tom_tat  : phần đầu hoặc mục "Tóm tắt / Mục tiêu"
    - hoc_van  : phần "Học vấn / Education"
    - kinh_nghiem : phần "Kinh nghiệm làm việc"
    Trả về dict với 3 key trên.
    """
    lines = raw_text.splitlines()

    # Gom các dòng thành block theo tiêu đề section
    sections: dict[str, list[str]] = {"tom_tat": [], "hoc_van": [], "kinh_nghiem": [], "_other": []}
    current_section = "_other"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Loại bỏ header/footer rác khi in PDF từ trình duyệt (ví dụ Chrome Print)
        if re.search(r"(Xem trước CV|127\.0\.0\.1:\d+|localhost:\d+)", stripped, re.IGNORECASE):
            continue
        if re.search(r"^\d{1,2}/\d{1,2}/\d{2,4}.*\d{1,2}:\d{2}\s*[AP]M", stripped, re.IGNORECASE):
            continue

        # Đưa về không dấu, chữ thường để regex
        normalized_line = _remove_accents(stripped)
        
        # Xóa luôn khoảng trắng (xử lý lỗi PDF extract bị cách chữ như 'H Ọ C V Ấ N')
        no_space_line = re.sub(r"\s+", "", normalized_line)

        # Kiểm tra xem dòng này có phải là tiêu đề section không
        matched_section = None
        for sec, pattern in _SECTION_PATTERNS.items():
            if pattern.search(no_space_line):
                # Chỉ coi là tiêu đề nếu dòng khá ngắn (tính theo ký tự gốc)
                if len(normalized_line) < 80:
                    matched_section = sec
                    break

        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(stripped)

    result = {}
    for key in ("tom_tat", "hoc_van", "kinh_nghiem"):
        content = "\n".join(sections[key]).strip()
        if not content:
            # Fallback: lấy từ _other nếu section trống
            other = "\n".join(sections["_other"]).strip()
            content = other[:500] if key == "tom_tat" else other
        result[key] = content or "(Không trích xuất được, vui lòng nhập tay)"

    # Nếu tom_tat quá dài, cắt bớt
    if len(result["tom_tat"]) > 500:
        result["tom_tat"] = result["tom_tat"][:500] + "..."

    return result


class CVCreateDTO(BaseModel):
    tom_tat: str = Field(..., min_length=1)
    duong_dan: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    hoc_van: str = Field(..., min_length=1)
    kinh_nghiem_lam_viec: str = Field(..., min_length=1)


class CVUpdateDTO(BaseModel):
    tom_tat: str | None = Field(None, min_length=1)
    duong_dan: str | None = Field(None, min_length=1)
    source: str | None = Field(None, min_length=1)
    hoc_van: str | None = Field(None, min_length=1)
    kinh_nghiem_lam_viec: str | None = Field(None, min_length=1)


def _validation_error(error: ValidationError):
    return jsonify({"errors": error.errors()}), 400


@cv_bp.route("/ung-vien", methods=["GET"])
@token_required
def get_my_cvs():
    db_session = get_db_session()
    try:
        service = CVService(CVRepository(db_session))
        user_id = request.current_user["user_id"]
        data = service.get_by_ung_vien(user_id)
        return jsonify({"data": data}), 200
    finally:
        db_session.close()



@cv_bp.route("/", methods=["POST"])
@token_required
def create_cv():
    if request.is_json:
        # User input text manually
        payload = request.get_json() or {}
        try:
            dto = CVCreateDTO(**payload)
        except ValidationError as error:
            return _validation_error(error)
    else:
        # User uploaded a file
        if "cv_file" not in request.files:
            return jsonify({"message": "Thiếu file CV"}), 400
            
        file = request.files["cv_file"]
        if file.filename == "":
            return jsonify({"message": "Chưa chọn file"}), 400

        try:
            dto = CVCreateDTO(
                tom_tat=request.form.get("tom_tat", ""),
                duong_dan="temp",
                source="Upload",
                hoc_van=request.form.get("hoc_van", ""),
                kinh_nghiem_lam_viec=request.form.get("kinh_nghiem", "")
            )
        except ValidationError as error:
            return _validation_error(error)

        # Lưu file vào static/uploads/cv/
        filename = secure_filename(file.filename)
        filename = f"{int(time.time())}_{filename}"
        upload_folder = os.path.join(current_app.root_path, "static", "uploads", "cv")
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Cập nhật đường dẫn
        dto.duong_dan = f"/static/uploads/cv/{filename}"

    db_session = get_db_session()
    try:
        service = CVService(CVRepository(db_session))
        payload = dto.model_dump()
        payload["ma_ung_vien"] = request.current_user["user_id"]
        result = service.create(payload)
    except Exception as e:
        return jsonify({"message": f"Lỗi hệ thống: {str(e)}"}), 500
    finally:
        db_session.close()

    return jsonify({"data": result}), 201


# ---------------------------------------------------------------------------
# Endpoint: phân tích file CV → trả về nội dung trích xuất
# ---------------------------------------------------------------------------

@cv_bp.route("/parse", methods=["POST"])
@token_required
def parse_cv_file():
    """
    Nhận file CV (PDF/DOCX), trích xuất text và trả về:
    { tom_tat, hoc_van, kinh_nghiem, raw_text }
    """
    if "cv_file" not in request.files:
        return jsonify({"message": "Thiếu file CV"}), 400

    file = request.files["cv_file"]
    if not file or file.filename == "":
        return jsonify({"message": "Chưa chọn file"}), 400

    filename = secure_filename(file.filename or "")
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"message": "Chỉ hỗ trợ file PDF, DOC, DOCX"}), 400

    file_bytes = file.read()

    try:
        if ext == ".pdf":
            raw_text = _extract_text_from_pdf(file_bytes)
        else:  # .doc / .docx
            raw_text = _extract_text_from_docx(file_bytes)
    except Exception as e:
        return jsonify({"message": f"Không đọc được file: {str(e)}"}), 422

    if not raw_text.strip():
        return jsonify({"message": "File không có nội dung text (có thể là CV dạng ảnh scan)"}), 422

    sections = _split_cv_sections(raw_text)
    return jsonify({
        "tom_tat": sections["tom_tat"],
        "hoc_van": sections["hoc_van"],
        "kinh_nghiem": sections["kinh_nghiem"],
        "raw_text": raw_text[:2000],   # preview 2000 ký tự đầu
    }), 200


@cv_bp.route("/<int:ma_cv>", methods=["PUT"])
@token_required
def update_cv(ma_cv: int):
    try:
        dto = CVUpdateDTO(**(request.get_json() or {}))
    except ValidationError as error:
        return _validation_error(error)

    db_session = get_db_session()
    try:
        service = CVService(CVRepository(db_session))
        user_id = request.current_user["user_id"]
        updated = service.update(ma_cv, user_id, dto.model_dump())
    except LookupError as error:
        return jsonify({"message": str(error)}), 404
    except PermissionError as error:
        return jsonify({"message": str(error)}), 403
    finally:
        db_session.close()

    if updated == 0:
        return jsonify({"message": "Không có gì thay đổi"}), 200
    return jsonify({"message": "Cập nhật thành công", "updated_rows": updated}), 200


@cv_bp.route("/<int:ma_cv>", methods=["DELETE"])
@token_required
def delete_cv(ma_cv: int):
    db_session = get_db_session()
    try:
        service = CVService(CVRepository(db_session))
        user_id = request.current_user["user_id"]
        deleted = service.delete(ma_cv, user_id)
    except LookupError as error:
        return jsonify({"message": str(error)}), 404
    except PermissionError as error:
        return jsonify({"message": str(error)}), 403
    finally:
        db_session.close()

    return jsonify({"message": "Xóa thành công", "deleted_rows": deleted}), 200
