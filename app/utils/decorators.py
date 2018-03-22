from functools import wraps
from app.models import Faculty
from flask import request, jsonify
import time
import jwt


def only_admins(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        res = dict(status='fail')
        faculty = Faculty.query.get(request.user.id)
        if all([faculty, faculty.admin]):
            return func(*args, **kwargs)
        res['message'] = 'You are not authorized to access this page.'
        return jsonify(res), 401
    return decorated


def login_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        authorization = request.headers.get('Authorization', '')
        authorization = authorization.split()
        if len(authorization) > 1:
            auth_code = authorization[1]
            try:
                email = Faculty.decode_auth_token(auth_code)
                user = Faculty.query.filter_by(email=email).first()
                if user and user.isActive:
                    request.user = user
                    return func(*args, **kwargs)
                status = 'Fail'
                msg = 'Invalid Authorization'
                status = 401
            except jwt.ExpiredSignatureError:
                status = 'Fail'
                msg = 'Signature expired. Please log in again.'
                status = 401
            except jwt.InvalidTokenError:
                status = 'Fail'
                msg = 'Invalid token. Please log in again.'
                status = 401
        else:
            status = 'Fail'
            msg = 'No authorization token provided'
            status = 401
        return jsonify(dict(status=status, message=msg)), status
    return decorated


def addLag(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        time.sleep(2)
        return func(*args, **kwargs)
    return decorated
