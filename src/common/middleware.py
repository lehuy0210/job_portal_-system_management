import os
from functools import wraps

import jwt
from flask import jsonify, request


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({"message": "Thiếu token! Vui lòng đăng nhập."}), 401

        try:
            secret = os.environ.get("JWT_SECRET")
            data = jwt.decode(token, secret, algorithms=["HS256"])
            request.current_user = data
        except Exception:
            return jsonify({"message": "Token không hợp lệ hoặc đã hết hạn!"}), 401

        return f(*args, **kwargs)

    return decorated
