class CVService:
	def __init__(self, repository):
		self.repository = repository

	def create(self, payload: dict):
		new_id = self.repository.create_cv(payload)
		return {"ma_cv": new_id, **payload}

	def update(self, ma_cv: int, payload: dict):
		if not self.repository.get_by_id(ma_cv):
			raise LookupError("CV không tồn tại")

		update_payload = {field: value for field, value in payload.items() if value is not None}
		if not update_payload:
			return 0

		return self.repository.update_cv(ma_cv, update_payload)

	def delete(self, ma_cv: int):
		if not self.repository.get_by_id(ma_cv):
			raise LookupError("CV không tồn tại")

		return self.repository.delete_cv(ma_cv)
