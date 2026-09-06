from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from src.database import get_db_session

from .repositories import ScreeningRepository
from .services import CVExtractRequestDTO, ScreeningService

screening_bp = Blueprint("screening", __name__, url_prefix="/api/v1/screening")

@screening_bp.route("/extract/<int:ma_cv>", methods=["POST"])
def extract_cv(ma_cv: int):
    payload = request.get_json(silent=True, force=True) or {}
    try:
        dto = CVExtractRequestDTO(**payload)
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400

    db_session = get_db_session()
    try:
        service = ScreeningService(ScreeningRepository(db_session))
        result = service.extract_and_save_cv(ma_cv, data=dto)
        return jsonify({"data": result}), 200
    except LookupError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": f"Error during extraction: {str(e)}"}), 500
    finally:
        db_session.close()

@screening_bp.route("/jobs/<int:tin_id>/candidates", methods=["GET"])
def screen_candidates(tin_id: int):
    db_session = get_db_session()
    try:
        service = ScreeningService(ScreeningRepository(db_session))
        result = service.screen_candidates_for_job(tin_id)
        return jsonify({"data": result}), 200
    except LookupError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": f"Error during screening: {str(e)}"}), 500
    finally:
        db_session.close()

@screening_bp.route("/candidates/<int:ma_cv>/recommended-jobs", methods=["GET"])
def recommend_jobs(ma_cv: int):
    top_n = request.args.get("top_n", default=5, type=int)

    db_session = get_db_session()
    try:
        service = ScreeningService(ScreeningRepository(db_session))
        result = service.recommend_jobs_for_cv(ma_cv, top_n=top_n)
        return jsonify({"data": result}), 200
    except LookupError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": f"Error during recommendation: {str(e)}"}), 500
    finally:
        db_session.close()
