from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from src.common.middleware import token_required
from src.database import get_db_session

from .repositories import UngVienRepository
from .services import UngVienProfileDTO, UngVienService

ung_vien_bp = Blueprint("ung_vien", __name__, url_prefix="/api/v1/ung-vien")


def _validation_error(error: ValidationError):
    return jsonify({"errors": error.errors()}), 400


@ung_vien_bp.route("/profile", methods=["GET"])
@token_required
def get_profile():
    db_session = get_db_session()
    try:
        service = UngVienService(UngVienRepository(db_session))
        user_id = request.current_user["user_id"]

        profile = service.get_profile(user_id)
        if not profile:
            return jsonify({"data": None, "message": "Chưa cập nhật thông tin cá nhân"}), 200

        return jsonify({"data": profile}), 200
    finally:
        db_session.close()


@ung_vien_bp.route("/profile", methods=["POST", "PUT"])
@token_required
def save_profile():
    try:
        dto = UngVienProfileDTO(**(request.get_json() or {}))
    except ValidationError as error:
        return _validation_error(error)

    db_session = get_db_session()
    try:
        service = UngVienService(UngVienRepository(db_session))
        user_id = request.current_user["user_id"]

        service.save_profile(user_id, dto.model_dump())
        return jsonify({"message": "Cập nhật thông tin cá nhân thành công!"}), 200
    finally:
        db_session.close()
