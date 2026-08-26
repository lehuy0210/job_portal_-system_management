from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field, ValidationError

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
	ma_ung_vien: int = Field(..., gt=0)


class CVUpdateDTO(BaseModel):
	tom_tat: str | None = Field(None, min_length=1)
	duong_dan: str | None = Field(None, min_length=1)
	source: str | None = Field(None, min_length=1)
	hoc_van: str | None = Field(None, min_length=1)
	kinh_nghiem_lam_viec: str | None = Field(None, min_length=1)


def _validation_error(error: ValidationError):
	return jsonify({"errors": error.errors()}), 400


@cv_bp.route("/", methods=["POST"])
def create_cv():
	try:
		dto = CVCreateDTO(**(request.get_json() or {}))
	except ValidationError as error:
		return _validation_error(error)

	db_session = get_db_session()
	try:
		service = CVService(CVRepository(db_session))
		result = service.create(dto.model_dump())
	finally:
		db_session.close()

	return jsonify({"data": result}), 201


@cv_bp.route("/<int:ma_cv>", methods=["PUT"])
def update_cv(ma_cv: int):
	try:
		dto = CVUpdateDTO(**(request.get_json() or {}))
	except ValidationError as error:
		return _validation_error(error)

	db_session = get_db_session()
	try:
		service = CVService(CVRepository(db_session))
		updated = service.update(ma_cv, dto.model_dump())
	except LookupError as error:
		return jsonify({"message": str(error)}), 404
	finally:
		db_session.close()

	if updated == 0:
		return jsonify({"message": "Không có gì thay đổi"}), 200
	return jsonify({"message": "Cập nhật thành công", "updated_rows": updated}), 200


@cv_bp.route("/<int:ma_cv>", methods=["DELETE"])
def delete_cv(ma_cv: int):
	db_session = get_db_session()
	try:
		service = CVService(CVRepository(db_session))
		deleted = service.delete(ma_cv)
	except LookupError as error:
		return jsonify({"message": str(error)}), 404
	finally:
		db_session.close()

	return jsonify({"message": "Xóa thành công", "deleted_rows": deleted}), 200
