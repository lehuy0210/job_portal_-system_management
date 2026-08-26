import os
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from pydantic import BaseModel, Field


class RegisterRequestDTO(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=6)


class LoginRequestDTO(BaseModel):
    username: str = Field(..., min_length=4)
    password: str = Field(..., min_length=6)


class AuthService:
    def __init__(self, repository):
        self.repository = repository
        self.jwt_secret = os.environ.get("JWT_SECRET")

    def register(self, data: RegisterRequestDTO):
        existing_user = self.repository.get_user_by_username(data.username)
        if existing_user:
            raise ValueError("Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác!")

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(data.password.encode("utf-8"), salt).decode("utf-8")

        ma_vai_tro_mac_dinh = 1

        new_user = self.repository.create_user(
            username=data.username, password_hash=password_hash, ma_vai_tro=ma_vai_tro_mac_dinh
        )

        return new_user

    def login(self, data: LoginRequestDTO):
        user = self.repository.get_user_by_username(data.username)
        if not user:
            raise ValueError("Tên đăng nhập hoặc mật khẩu không chính xác!")

        if not bcrypt.checkpw(data.password.encode("utf-8"), user.password.encode("utf-8")):
            raise ValueError("Tên đăng nhập hoặc mật khẩu không chính xác!")

        payload = {
            "user_id": user.id,
            "ma_vai_tro": user.ma_vai_tro,
            "exp": datetime.now(UTC) + timedelta(hours=1),
        }

        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")

        return {
            "access_token": token,
            "expires_in": 3600,
            "ma_vai_tro": user.ma_vai_tro,
            "id": user.id
        }
