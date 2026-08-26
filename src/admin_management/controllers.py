from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field, ValidationError
from src.database import get_db_session

from .repositories import AdminRepository
from .services import AdminService

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


class AccountCreateDTO(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    ma_vai_tro: int = Field(..., ge=1, le=3)


class InsertCongTyDTO(BaseModel):
    ma_nha_tuyen_dung: int = Field(..., gt=0)
    ten_cong_ty: str = Field(..., min_length=1, max_length=255)
    ma_so_thue: str | None = None
    mo_ta: str | None = None
    dia_chi: str | None = None


class InsertNhaTuyenDungDTO(BaseModel):
    ma_nha_tuyen_dung: int = Field(..., gt=0)


def _validation_error(error: ValidationError):
    return jsonify({"errors": error.errors()}), 400


@admin_bp.route("/users", methods=["GET"])
def get_users():
    db_session = get_db_session()
    try:
        service = AdminService(AdminRepository(db_session))
        users = service.get_all_users()
        return jsonify({"data": users}), 200
    except Exception as e:
        return jsonify({"message": f"Lỗi hệ thống: {str(e)}"}), 500
    finally:
        db_session.close()


@admin_bp.route("/insert-account", methods=["POST"])
def api_insert_account():
    try:
        dto = AccountCreateDTO(**(request.get_json() or {}))
    except ValidationError as error:
        return _validation_error(error)

    db_session = get_db_session()
    try:
        service = AdminService(AdminRepository(db_session))
        new_id = service.create_account(dto.model_dump())
        return jsonify({"data": {"id": new_id}, "message": "Tạo tài khoản thành công"}), 201
    except Exception as e:
        return jsonify({"message": f"Tên đăng nhập đã tồn tại hoặc lỗi CSDL: {str(e)}"}), 400
    finally:
        db_session.close()


@admin_bp.route("/insert-nha-tuyen-dung", methods=["POST"])
def api_insert_ntd():
    try:
        dto = InsertNhaTuyenDungDTO(**(request.get_json() or {}))
    except ValidationError as error:
        return _validation_error(error)

    db_session = get_db_session()
    try:
        service = AdminService(AdminRepository(db_session))
        service.init_nha_tuyen_dung_profile(dto.ma_nha_tuyen_dung)
        return jsonify({"message": "Tạo hồ sơ gốc thành công"}), 201
    except Exception as e:
        return jsonify({"message": f"Lỗi hệ thống hoặc hồ sơ đã tồn tại: {str(e)}"}), 400
    finally:
        db_session.close()


@admin_bp.route("/insert-cong-ty", methods=["POST"])
def api_insert_cong_ty():
    try:
        dto = InsertCongTyDTO(**(request.get_json() or {}))
    except ValidationError as error:
        return _validation_error(error)

    db_session = get_db_session()
    try:
        service = AdminService(AdminRepository(db_session))
        service.init_cong_ty_profile(dto.model_dump())
        return jsonify({"message": "Tạo thông tin công ty thành công"}), 201
    except Exception as e:
        return jsonify({"message": f"Lỗi hệ thống hoặc công ty cho ID này đã tồn tại: {str(e)}"}), 400
    finally:
        db_session.close()
