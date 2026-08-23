from sqlalchemy import text
from sqlalchemy.orm import Session


class AuthRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_user_by_username(self, username: str):
        query = text("SELECT id, username, password, ma_vai_tro FROM nguoi_dung WHERE username = :username")
        return self.db.execute(query, {"username": username}).fetchone()

    def create_user(self, username: str, password_hash: str, ma_vai_tro: int):
        query = text("""
                     INSERT INTO nguoi_dung (username, password, ma_vai_tro)
                     VALUES (:username, :password, :ma_vai_tro) RETURNING id, username, ma_vai_tro
                     """)
        result = self.db.execute(
            query, {"username": username, "password": password_hash, "ma_vai_tro": ma_vai_tro}
        ).fetchone()
        self.db.commit()
        return result
