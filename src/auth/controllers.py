from flask import Blueprint, jsonify, request
from src.database import get_db_session

from .repositories import AuthRepository
from .services import AuthService, LoginRequestDTO, RegisterRequestDTO

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    raw_data = request.get_json()
    dto = RegisterRequestDTO(**raw_data)

    db_session = get_db_session()
    service = AuthService(AuthRepository(db_session))

    result = service.register(dto)

    return jsonify({"data": result}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    raw_data = request.get_json()
    dto = LoginRequestDTO(**raw_data)

    db_session = get_db_session()
    service = AuthService(AuthRepository(db_session))

    result = service.login(dto)

    return jsonify({"data": result}), 200
