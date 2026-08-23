import os

import bcrypt
from pydantic import BaseModel, Field


class RegisterRequestDTO(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
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
