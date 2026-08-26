from flask import jsonify
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError


def register_error_handlers(app):
    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return jsonify({"error": {"message": str(error)}}), 400

    @app.errorhandler(ValidationError)
    def handle_pydantic_validation_error(error):
        errors = error.errors()
        err_msg = errors[0].get('msg', 'Dữ liệu không hợp lệ') if errors else 'Dữ liệu không hợp lệ'
        return jsonify({"error": {"message": f"Lỗi dữ liệu: {err_msg}"}}), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        error_info = str(error.orig) if hasattr(error, 'orig') else str(error)

        if "Duplicate entry" in error_info or "UNIQUE constraint" in error_info:
            return jsonify(
                {"error": {"message": "Email hoặc thông tin định danh này đã được sử dụng bởi tài khoản khác!"}}), 400

        return jsonify({"error": {"message": "Lỗi dữ liệu cơ sở dữ liệu, vui lòng kiểm tra lại!"}}), 400

    @app.errorhandler(Exception)
    def handle_exception(error):
        import traceback
        traceback.print_exc()
        return jsonify({"error": {"message": f"🔍 LỖI THẬT: {str(error)}"}}), 500
