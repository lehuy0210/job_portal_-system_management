from .repositories import AdminRepository


class AdminService:
    def __init__(self, repository: AdminRepository):
        self.repository = repository

    def get_all_users(self) -> list[dict]:
        users = self.repository.get_all_users()
        for u in users:
            u["has_profile"] = bool(u["has_profile"])
        return users

    def create_account(self, payload: dict) -> int:
        return self.repository.insert_account(payload)

    def init_nha_tuyen_dung_profile(self, ma_nha_tuyen_dung: int):
        return self.repository.insert_nha_tuyen_dung(ma_nha_tuyen_dung)

    def init_cong_ty_profile(self, payload: dict) -> int:
        return self.repository.insert_cong_ty(payload)
