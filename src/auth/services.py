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
            raise ValueError("USERNAME_EXISTS")

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(data.password.encode("utf-8"), salt).decode("utf-8")

        ma_vai_tro_mac_dinh = 1

        new_user = self.repository.create_user(
            username=data.username, password_hash=password_hash, ma_vai_tro=ma_vai_tro_mac_dinh
        )

        return {"id": new_user.id, "username": new_user.username, "ma_vai_tro": new_user.ma_vai_tro}

    def login(self, data: LoginRequestDTO):
        user = self.repository.get_user_by_username(data.username)
        if not user:
            raise ValueError("INVALID_CREDENTIALS")

        if not bcrypt.checkpw(data.password.encode("utf-8"), user.password.encode("utf-8")):
            raise ValueError("INVALID_CREDENTIALS")

        payload = {
            "user_id": user.id,
            "ma_vai_tro": user.ma_vai_tro,
            "exp": datetime.now(UTC) + timedelta(hours=1),
        }

        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")

        return {"access_token": token, "expires_in": 3600, "ma_vai_tro": user.ma_vai_tro}
