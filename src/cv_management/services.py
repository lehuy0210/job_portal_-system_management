class CVService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, payload: dict):
        new_id = self.repository.create_cv(payload)
        return {"ma_cv": new_id, **payload}

    def update(self, ma_cv: int, ma_ung_vien: int, payload: dict):
        cv = self.repository.get_by_id(ma_cv)
        if not cv:
            raise LookupError("CV không tồn tại")

        cv_owner_id = getattr(cv, 'ma_ung_vien', cv._mapping['ma_ung_vien'] if hasattr(cv, '_mapping') else None)
        if cv_owner_id != ma_ung_vien:
            raise PermissionError("Bạn không có quyền sửa CV này")

        update_payload = {field: value for field, value in payload.items() if value is not None}
        if not update_payload:
            return 0

        return self.repository.update_cv(ma_cv, update_payload)

    def delete(self, ma_cv: int, ma_ung_vien: int):
        cv = self.repository.get_by_id(ma_cv)
        if not cv:
            raise LookupError("CV không tồn tại")

        cv_owner_id = getattr(cv, 'ma_ung_vien', cv._mapping['ma_ung_vien'] if hasattr(cv, '_mapping') else None)
        if cv_owner_id != ma_ung_vien:
            raise PermissionError("Bạn không có quyền xóa CV này")

        return self.repository.delete_cv(ma_cv)

    def get_by_ung_vien(self, ma_ung_vien: int):
        return self.repository.get_by_ung_vien(ma_ung_vien)
