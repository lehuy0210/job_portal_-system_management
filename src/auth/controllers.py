from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from src.database import get_db_session

from .repositories import AuthRepository
from .services import AuthService, LoginRequestDTO, RegisterRequestDTO

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        raw_data = request.get_json() or {}
        dto = RegisterRequestDTO(**raw_data)
    except ValidationError as error:
        return jsonify({"errors": error.errors()}), 400

    db_session = get_db_session()
    try:
        service = AuthService(AuthRepository(db_session))
        result = service.register(dto)
        return jsonify({"data": result}), 201
    except ValueError as error:
        return jsonify({"message": str(error)}), 400
    finally:
        db_session.close()

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        raw_data = request.get_json() or {}
        dto = LoginRequestDTO(**raw_data)
    except ValidationError as error:
        return jsonify({"errors": error.errors()}), 400

    db_session = get_db_session()
    try:
        service = AuthService(AuthRepository(db_session))
        result = service.login(dto)
        return jsonify({"data": result}), 200
    except ValueError as error:
        return jsonify({"message": str(error)}), 401 # 401 Unauthorized cho đăng nhập sai
    finally:
        db_session.close()
