from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field, ValidationError
from src.common.middleware import token_required
from src.database import get_db_session

from .repositories import CVRepository
from .services import CVService

cv_bp = Blueprint("cv", __name__, url_prefix="/api/v1/cv")


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


import os
from werkzeug.utils import secure_filename
import time
from flask import current_app

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
