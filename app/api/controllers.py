from flask import request, Blueprint, make_response
from app import db, jsonify, bcrypt
from app.models import Faculty, Student, Attendance
from datetime import datetime

from functools import wraps
import jwt
import time

mod_api = Blueprint('api', __name__, url_prefix='/api')


def addLag(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        time.sleep(2)
        return func(*args, **kwargs)
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
                if user:
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
        return make_response(jsonify(dict(status=status, message=msg))), status
    return decorated


@mod_api.route('/faculty')
@login_required
def list_faculties():
    faculties = [f.serialize() for f in Faculty.query.all()]
    data = dict(status='Success', faculties=faculties)
    return make_response(jsonify(data)), 200


@mod_api.route('/faculty/add', methods=['POST'])
@login_required
def add_faculty():
    required_fileds = ['email', 'password', 'name']
    res = dict(status='fail')
    res_code = 401

    data = request.json or request.data or request.form
    if not data:
        res['message'] = 'No data received.'
        return make_response(jsonify(res)), res_code

    keys = [str(key) for key in data.keys()]
    if required_fileds != keys:
        res['message'] = 'expected atleast {0} got only {1}'.format(required_fileds, keys)
        return make_response(jsonify(res)), res_code

    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    if not all([email, name, password]):
        res['message'] = 'missing required data.'
        return make_response(jsonify(res)), res_code

    faculty = Faculty.query.filter_by(email=email).first()
    if not faculty:
        try:
            faculty = Faculty(
                name=name,
                email=email,
                password=password)
            # insert the user
            db.session.add(faculty)
            db.session.commit()
            res['status'] = 'success'
            res['message'] = '{0} successfully registered.'.format(faculty.name)
            res_code = 201
        except Exception as e:
            print e
            res['message'] = 'Some error occurred. Please try again.'
    else:
        res['meassage'] = 'Faculty already exists.'
        res_code = 202
    return make_response(jsonify(res)), res_code


@mod_api.route('/student')
@login_required
def list_students():
    students = [s.serialize() for s in Student.query.all()]
    data = dict(status='Success', students=students)
    return make_response(jsonify(data)), 200


@mod_api.route('/student/add', methods=['POST'])
@login_required
def add_student():
    required_fields = ['dob', 'name', 'category', 'id']
    res = dict(status='fail')
    res_code = 401

    data = request.json or request.data or request.form
    if not data:
        res['message'] = 'No data received.'
        return make_response(jsonify(res)), res_code

    keys = [str(key) for key in data.keys()]
    if set(required_fields) != set(keys):
        res['message'] = 'expected atleast {0} got only {1}'.format(required_fields, keys)
        return make_response(jsonify(res)), res_code

    dob = data.get('dob').strip()
    name = data.get('name').strip()
    category = data.get('category').strip()
    student_id = data.get('id').strip()
    if not all([dob, name, category, student_id]):
        res['message'] = 'missing required data.'
        return make_response(jsonify(res)), res_code

    parsed_dob = datetime.strptime(dob, '%Y-%m-%d')
    if not parsed_dob:
        res['message'] = 'Invalid date {0}.'.format(dob)
        return make_response(jsonify(res)), res_code
    dob = parsed_dob

    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        try:
            student = Student(
                student_id=student_id,
                category=category,
                name=name,
                dob=dob)
            # insert the user
            db.session.add(student)
            db.session.commit()
            res['status'] = 'success'
            res['message'] = '{0} Successfully registered.'.format(student.name)
            res_code = 201
        except Exception as e:
            print e
            res['message'] = 'Some error occurred. Please try again.'
    else:
        res['meassage'] = 'Student already exists.'
        res_code = 202
    return make_response(jsonify(res)), res_code


@mod_api.route('/')
@login_required
def index():
    return jsonify(dict(content='Hello World'))


@mod_api.route('/get_token', methods=['POST'])
def get_token():
    # get the post data
    data = request.json or request.data or request.form
    # check if user already exists
    email = data.get('email')
    faculty = Faculty.query.filter_by(email=email).first()
    if faculty:
        try:
            password = data.get('password')
            if bcrypt.check_password_hash(faculty.password, password):
                res = {
                    'status': 'success',
                    'message': 'log in successful.',
                    'auth_token': faculty.encode_auth_token(email).decode()
                }
                return make_response(jsonify(res)), 202
        except Exception as e:
            print str(e)
            res = {
                'status': 'fail',
                'message': 'Some error occurred. Please try again.'
            }
            return make_response(jsonify(res)), 401

    res = {
        'status': 'fail',
        'message': 'Username or password is incorrect.',
    }
    return make_response(jsonify(res)), 401


@mod_api.route('/attendance/<int:date>', methods=['GET'])
@login_required
def get_attendance(date):
    date = datetime.strptime(str(date), '%d%m%Y').date()
    print date
    attendance = Attendance.query.filter_by(date=date).all()
    attendance = [att.serialize() for att in attendance]
    data = dict(result=True, date=date, attendance=attendance)
    return make_response(jsonify(data))


@mod_api.route('/attendance/set/<int:date>', methods=['POST'])
@login_required
def set_attendance(date):
    data = request.json or request.data or request.form
    date = datetime.strptime(str(date), '%d%m%Y')
    res = dict(status='fail')
    res_code = 400
    if not isinstance(data, list):
        res['message'] = 'expect a list got {0}.'.format(data)
        return make_response(jsonify(res)), res_code
    std_updated = []
    std_added = []
    for student in data:
        student_id = student.get('student_id')
        punchIn = student.get('in')
        punchOut = student.get('out')
        comments = student.get('comment')
        attendance = Attendance.query.filter_by(date=date, student_id=student_id).first()
        if not attendance:
            attendance = Attendance(date=date,
                                    comments=comments,
                                    punchOut=punchOut,
                                    punchIn=punchIn,
                                    student_id=student_id)
            db.session.add(attendance)
            std_added.append(student_id)
        else:
            attendance.punchIn = punchIn
            attendance.punchOut = punchOut
            std_updated.append(student_id)
    db.session.commit()
    res['status'] = 'Success'
    res['meassage'] = 'Attendance saved successfully'
    res['updatedIds'] = std_updated
    res['addedIds'] = std_added
    res_code = 200
    return make_response(jsonify(res)), res_code
