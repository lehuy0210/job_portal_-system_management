from datetime import date
from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field, ValidationError
from src.database import get_db_session

from src.common.middleware import token_required  # Import middleware
from .repositories import JobRepository
from .services import JobService

job_bp = Blueprint("job", __name__, url_prefix="/api/v1/jobs")


class JobCreateDTO(BaseModel):
    tieu_de: str = Field(..., min_length=1, max_length=255)
    mo_ta: str = Field(..., min_length=1)
    han_nop: date
    min_salary: int | None = Field(None, ge=0)
    max_salary: int | None = Field(None, ge=0)
    dia_chi: str | None = Field(None, min_length=1)
    so_nam_kinh_nghiem: int | None = Field(None, ge=0)
    ma_nha_tuyen_dung: int = Field(..., gt=0)
    ma_trang_thai: int = Field(..., gt=0)
    ten_ky_nangs: list[str] = Field(default_factory=list)


class JobFilterDTO(BaseModel):
    keyword: str | None = None
    ma_trang_thai: int | None = None
    dia_chi: str | None = None
    min_experience: int | None = Field(None, ge=0)
    max_experience: int | None = Field(None, ge=0)
    min_salary: int | None = Field(None, ge=0)
    max_salary: int | None = Field(None, ge=0)
    skill_ids: list[int] | None = None


class UpdateStatusDTO(BaseModel):
    ma_trang_thai: int = Field(..., description="2: Đã mở, 9: Tạm dừng, 10: Đã đóng")


# --- DTOs cho Ứng tuyển ---
class ApplyJobDTO(BaseModel):
    ma_cv: int = Field(..., gt=0)


class UpdateAppStatusDTO(BaseModel):
    # Trang thai ung tuyen: 4: Phong van, 5: Trung tuyen, 6: Tu choi
    ma_trang_thai: int = Field(..., gt=0)


def _validation_error(error: ValidationError):
    return jsonify({"errors": error.errors()}), 400


def _get_dto_dict(dto):
    if hasattr(dto, "model_dump"):
        return dto.model_dump()
    return dto.dict()


@job_bp.route("/", methods=["POST"])
@token_required  # Bảo mật: Bắt buộc đăng nhập
def create_job():
    try:
        dto = JobCreateDTO(**(request.get_json() or {}))
    except ValidationError as error:
        return _validation_error(error)

    db_session = get_db_session()
    try:
        service = JobService(JobRepository(db_session))
        payload = _get_dto_dict(dto)

        # BẢO MẬT: Ghi đè ma_nha_tuyen_dung bằng user_id thực sự từ token
        payload["ma_nha_tuyen_dung"] = request.current_user["user_id"]

        result = service.create(payload)
    except Exception as e:
        return jsonify({"message": f"Lỗi hệ thống: {str(e)}"}), 500
    finally:
        db_session.close()

    return jsonify({"data": result}), 201


@job_bp.route("/search", methods=["GET"])
def search_jobs():
    args = request.args
    skill_ids = []

    skill_ids_str = args.get("skill_ids")
    if skill_ids_str:
        try:
            skill_ids.extend([int(x.strip()) for x in skill_ids_str.split(",") if x.strip()])
        except ValueError:
            return jsonify(
                {"errors": [{"loc": ["query", "skill_ids"], "msg": "Kỹ năng phải là danh sách số nguyên"}]}), 400

    skill_ids_list = args.getlist("skill_ids")
    for val in skill_ids_list:
        if "," in val:
            continue
        try:
            skill_ids.append(int(val))
        except ValueError:
            pass

    if skill_ids:
        skill_ids = list(set(skill_ids))
    else:
        skill_ids = None

    filter_data = {
        "keyword": args.get("keyword") or None,
        "ma_trang_thai": int(args.get("ma_trang_thai")) if args.get("ma_trang_thai") else None,
        "dia_chi": args.get("dia_chi") or None,
        "min_experience": int(args.get("min_experience")) if args.get("min_experience") else None,
        "max_experience": int(args.get("max_experience")) if args.get("max_experience") else None,
        "min_salary": int(args.get("min_salary")) if args.get("min_salary") else None,
        "max_salary": int(args.get("max_salary")) if args.get("max_salary") else None,
        "skill_ids": skill_ids,
    }

    try:
        dto = JobFilterDTO(**filter_data)
    except ValidationError as error:
        return _validation_error(error)

    db_session = get_db_session()
    try:
        service = JobService(JobRepository(db_session))
        result = service.search(_get_dto_dict(dto))
    except Exception as e:
        return jsonify({"message": f"Lỗi hệ thống: {str(e)}"}), 500
    finally:
        db_session.close()

    return jsonify({"data": result}), 200


@job_bp.route("/<int:tin_id>/status", methods=["PUT"])
@token_required  # Bảo mật: Bắt buộc đăng nhập
def update_job_status(tin_id: int):
    try:
        dto = UpdateStatusDTO(**(request.get_json() or {}))
    except ValidationError as error:
        return jsonify({"errors": error.errors()}), 400

    db_session = get_db_session()
    try:
        service = JobService(JobRepository(db_session))

        # BẢO MẬT: Lấy user_id từ token để service kiểm tra quyền
        user_id = request.current_user["user_id"]
        success = service.update_status(tin_id, dto.ma_trang_thai, user_id)

        if success:
            return jsonify({"message": "Cập nhật trạng thái thành công"}), 200
        return jsonify({"message": "Không tìm thấy tin tuyển dụng"}), 404

    except LookupError as e:
        return jsonify({"message": str(e)}), 404
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403
    except Exception as e:
        return jsonify({"message": f"Lỗi hệ thống: {str(e)}"}), 500
    finally:
        db_session.close()


@job_bp.route("/skills", methods=["GET"])
def get_all_skills():
    db_session = get_db_session()
    try:
        service = JobService(JobRepository(db_session))
        skills = service.get_all_skills()
        return jsonify({"data": skills}), 200
    except Exception as e:
        return jsonify({"message": f"Lỗi hệ thống: {str(e)}"}), 500
    finally:
        db_session.close()


# ==========================================
# API HỒ SƠ ỨNG TUYỂN (APPLICATIONS)
# ==========================================

@job_bp.route("/<int:tin_id>/apply", methods=["POST"])
@token_required
def apply_for_job(tin_id: int):
    # Chỉ ứng viên mới được nộp hồ sơ
    if request.current_user.get("ma_vai_tro") != 1:
        return jsonify({"message": "Chỉ ứng viên mới có quyền nộp hồ sơ."}), 403

    try:
        dto = ApplyJobDTO(**(request.get_json() or {}))
    except ValidationError as error:
        return _validation_error(error)

    db_session = get_db_session()
    try:
        service = JobService(JobRepository(db_session))
        user_id = request.current_user["user_id"]
        result = service.apply_job(user_id, tin_id, dto.ma_cv)
        return jsonify({"data": result, "message": "Nộp hồ sơ thành công"}), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Lỗi hệ thống: {str(e)}"}), 500
    finally:
        db_session.close()


@job_bp.route("/<int:tin_id>/applications", methods=["GET"])
@token_required
def get_job_applications(tin_id: int):
    # Chỉ NTD mới được xem
    if request.current_user.get("ma_vai_tro") != 2:
        return jsonify({"message": "Chỉ nhà tuyển dụng mới có quyền xem danh sách ứng viên."}), 403

    db_session = get_db_session()
    try:
        service = JobService(JobRepository(db_session))
        user_id = request.current_user["user_id"]
        result = service.get_job_applications(user_id, tin_id)
        return jsonify({"data": result}), 200
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403
    except Exception as e:
        return jsonify({"message": f"Lỗi hệ thống: {str(e)}"}), 500
    finally:
        db_session.close()


@job_bp.route("/applications/<int:ma_ho_so>/status", methods=["PUT"])
@token_required
def update_application_status(ma_ho_so: int):
    # Chỉ NTD mới được cập nhật
    if request.current_user.get("ma_vai_tro") != 2:
        return jsonify({"message": "Chỉ nhà tuyển dụng mới có quyền cập nhật trạng thái hồ sơ."}), 403

    try:
        dto = UpdateAppStatusDTO(**(request.get_json() or {}))
    except ValidationError as error:
        return _validation_error(error)

    db_session = get_db_session()
    try:
        service = JobService(JobRepository(db_session))
        user_id = request.current_user["user_id"]
        
        success = service.update_application_status(user_id, ma_ho_so, dto.ma_trang_thai)
        if success:
            return jsonify({"message": "Cập nhật trạng thái thành công"}), 200
        return jsonify({"message": "Cập nhật thất bại"}), 400
    except LookupError as e:
        return jsonify({"message": str(e)}), 404
    except PermissionError as e:
        return jsonify({"message": str(e)}), 403
    except Exception as e:
        return jsonify({"message": f"Lỗi hệ thống: {str(e)}"}), 500
    finally:
        db_session.close()
