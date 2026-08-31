from datetime import date

from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field, ValidationError
from src.database import get_db_session

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


def _validation_error(error: ValidationError):
    return jsonify({"errors": error.errors()}), 400


def _get_dto_dict(dto):
    if hasattr(dto, "model_dump"):
        return dto.model_dump()
    return dto.dict()


@job_bp.route("/", methods=["POST"])
def create_job():
    try:
        dto = JobCreateDTO(**(request.get_json() or {}))
    except ValidationError as error:
        return _validation_error(error)

    db_session = get_db_session()
    try:
        service = JobService(JobRepository(db_session))
        result = service.create(_get_dto_dict(dto))
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
                {"errors": [{"loc": ["query", "skill_ids"], "msg": "Kỹ năng phải là danh sách số nguyên"}]}
            ), 400

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
def update_job_status(tin_id: int):
    try:
        dto = UpdateStatusDTO(**(request.get_json() or {}))
    except ValidationError as error:
        return jsonify({"errors": error.errors()}), 400

    db_session = get_db_session()
    try:
        service = JobService(JobRepository(db_session))
        success = service.update_status(tin_id, dto.ma_trang_thai)
        if success:
            return jsonify({"message": "Cập nhật trạng thái thành công"}), 200
        return jsonify({"message": "Không tìm thấy tin tuyển dụng"}), 404
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
