from flask import request, Blueprint, make_response
from app import db, jsonify, bcrypt
from app.models import Faculty, Student, Attendance
from datetime import datetime
from functools import wraps
from operator import itemgetter
import jwt
import time
import csv

mod_api = Blueprint('api', __name__, url_prefix='/api')


def addLag(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        time.sleep(2)
        return func(*args, **kwargs)
    return decorated


def only_admins(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        res = dict(status='fail')
        faculty = Faculty.query.get(request.user.id)
        if all([faculty, faculty.admin]):
            return func(*args, **kwargs)
        res['message'] = 'You are not authorized to access this page.'
        return make_response(jsonify(res)), 401
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
    data = dict(status='success', faculties=faculties)
    return make_response(jsonify(data)), 200


@mod_api.route('/faculty/add', methods=['POST'])
@login_required
@only_admins
def add_faculty():
    required_fileds = ['email', 'password', 'name']
    res = dict(status='fail')
    res_code = 200

    data = request.json or request.data or request.form
    if not data:
        res['message'] = 'No data received.'
        return make_response(jsonify(res)), res_code

    keys = [str(key) for key in data.keys()]
    if required_fileds != keys:
        res['message'] = 'expected atleast {0} got only {1}'\
                         .format(required_fileds, keys)
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
            res['message'] = '{0} successfully registered.'\
                             .format(faculty.name)
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


@mod_api.route('/student/<string:action>', methods=['POST'])
@login_required
@only_admins
def add_update_student(action):
    res = dict(status='fail')
    res_code = 200
    if action not in ['add', 'update']:
        res['message'] = 'Invalid url'
        return jsonify(res), 401

    required_fields = ['dob', 'name', 'category', 'id']

    data = request.json or request.data or request.form
    if not data:
        res['message'] = 'No data received.'
        return make_response(jsonify(res)), res_code

    keys = [str(key) for key in data.keys()]
    if not set(required_fields).issubset(set(keys)):
        res['message'] = 'expected atleast {0} got only {1}'\
                         .format(required_fields, keys)
        return jsonify(res), res_code

    dob = data.get('dob').strip()
    name = data.get('name').strip()
    category = data.get('category').strip()
    contact = data.get('contact').strip()
    student_id = data.get('id').strip()
    if not all([dob, name, category, student_id]):
        res['message'] = 'required fields are missing or blank'
        return jsonify(res), res_code
    try:
        dob = datetime.strptime(dob, '%Y-%m-%d')
    except Exception:
        res['message'] = 'Invalid date: {0}'.format(dob)
        return jsonify(res), res_code

    student = Student.query.filter_by(student_id=student_id).first()
    if not student and action == 'add':
        try:
            student = Student(
                name=name,
                student_id=student_id,
                category=category)
            # insert the user
            db.session.add(student)
            res['message'] = '{0} Successfully registered.'\
                             .format(student.name)
            res_code = 201
        except Exception as e:
            print e
            res['message'] = 'Some error occurred. Please try again.'
    elif action == 'add':
        res['message'] = 'Student ID {} alreay exists'.format(student_id)
        res_code = 201
    else:
        student.name = name
        student.dob = dob
        student.category = category
        student.contact = contact
        db.session.commit()
        res['status'] = 'success'
        res['student'] = student.serialize()
    return jsonify(res), res_code


@mod_api.route('/student/delete/<int:studentid>', methods=['GET'])
@login_required
@only_admins
def delete_student(studentid):
    res = dict(status='fail')
    res_code = 200
    student = Student.query.get(studentid)
    if student:
        db.session.delete(student)
        db.session.commit()
        res['message'] = 'Student deleted'
        res['studentid'] = studentid
        res['status'] = 'success'
    else:
        res['message'] = 'No such student'
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
                    'auth_token': faculty.encode_auth_token(email).decode(),
                    'is_admin': faculty.admin
                }
                print res
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


@mod_api.route('/attendance/<string:date>', methods=['GET'])
@login_required
def get_attendance(date):
    date = datetime.strptime(date, '%d%m%Y').date()
    attendance = Attendance.query.filter_by(date=date).all()
    attendance = [att.serialize() for att in attendance]
    data = dict(result=True, date=date, attendance=attendance)
    return make_response(jsonify(data)), 200


@mod_api.route('/attendance/<string:date>/<int:studentid>/<string:what>',
               methods=['POST'])
@login_required
def set_attendance(date, studentid, what):
    res = dict(status='fail')
    res_code = 200
    if what not in ['in', 'out', 'comment']:
        res['message'] = 'Invalid url'
        return make_response(jsonify(res)), res_code
    data = request.json or request.data or request.form
    res_code = 200
    try:
        date = datetime.strptime(date, '%d%m%Y').date()
        dataToSave = data.get(what)
        # if its a time then should be parsellable to the specific format
        if what in ['in', 'out']:
            datetime.strptime(dataToSave, '%H:%M:%S')
    except Exception as e:
        print e
        res['message'] = 'Invalid date or punch in time [{},{}]'\
                         .format(date, data['in'])
        return make_response(jsonify(res)), res_code
    student = Student.query.get(studentid)
    faculty = Faculty.query.get(request.user.id)
    msg = check_student_faculty(student, faculty, date)
    if msg:
        res['message'] = msg
        return make_response(jsonify(res)), res_code

    attendance = Attendance.query.filter_by(date=date,
                                            student_id=student.id).first()
    if attendance:
        if faculty.admin:
            if what == 'in':
                attendance.punch_in = dataToSave
                attendance.punch_in_by_id = request.user.id
            elif what == 'out':
                attendance.punch_out = dataToSave
                attendance.punch_out_by_id = request.user.id
            else:
                attendance.comments = dataToSave
            res['message'] = 'Updated existing record'
            db.session.commit()
            res['attendance'] = attendance.serialize()
            res['status'] = 'success'
            res_code = 200
        else:
            res['message'] = 'Record already exists, Request admin \
            to update the record.'
    else:
        # If the record does not exist that means the dataToSave is intime
        attendance = Attendance(date=date,
                                student_id=studentid,
                                punch_in=dataToSave,
                                punch_in_by_id=request.user.id)
        db.session.add(attendance)
        db.session.commit()
        res['attendance'] = attendance.serialize()
        res['message'] = 'Record created.'
        res['status'] = 'success'
        res_code = 200
    return make_response(jsonify(res)), res_code


@mod_api.route('/student/import', methods=['POST'])
@login_required
@only_admins
def import_students():
    res = dict(status='fail')
    file = request.files.get('studentsListFile')
    csvreader = csv.reader(file, delimiter=',', quotechar='"')
    # TODO: check type of file
    heading = [title.strip().lower() for title in csvreader.next()]
    getName = itemgetter(heading.index('name of the student'))
    getCategory = itemgetter(heading.index('category'))
    getStudentId = itemgetter(heading.index('student id'))
    getDob = itemgetter(heading.index('date of birth'))
    getContact = itemgetter(heading.index('telephone no.'))
    getBranch = itemgetter(heading.index('preferred branch'))

    added = []
    updated = []
    for row in csvreader:
        student = Student.query.filter_by(student_id=getStudentId(row)).first()
        dob = datetime.strptime('%d/%m/%Y', getDob(row))
        category, student_id = getCategory(row), getStudentId(row)
        name, contact = getName(row), getContact(row)
        branch = getBranch(row)
        if student:
            unchanged = all([student.category == category,
                             student.dob == dob,
                             student.name == name,
                             student.contact == contact,
                             student.branch == branch])
            if not unchanged:
                student.category = category
                student.dob = dob
                student.name = name
                student.contact = contact
                student.branch = branch
                updated.append(student)
        else:
            student = Student(student_id=student_id,
                              category=category,
                              dob=dob,
                              name=name,
                              contact=contact,
                              branch=branch)
            db.session.add(student)
            added.append(student)
    db.session.commit()
    res['status'] = 'success'
    res['added'] = [std.serialize() for std in added]
    res['updated'] = [std.serialize() for std in updated]
    res['message'] = 'Added {0} student(s), Udpated {1} student(s)'\
                     .format(len(added), len(updated))
    return jsonify(res), 200


def check_student_faculty(student, faculty, date):
    if not faculty:
        return 'You are not a Faculty'
    if not any([faculty.admin, date != datetime.today()]):
        return 'Invalid date {}'.format(date)
    if not student:
        return 'No such student'
