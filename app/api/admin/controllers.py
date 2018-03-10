from flask import request, Blueprint, make_response
from app import db, jsonify
from app.models import Faculty, Student, Attendance
from datetime import datetime
from operator import itemgetter
from app.utils import decorators, parseDate, validEmail
import csv


adminapi = Blueprint('adminapi', __name__, url_prefix='/api/admin')


@adminapi.route('/faculty')
@decorators.login_required
@decorators.only_admins
def list_faculties():
    faculties = [f.serialize() for f in Faculty.query.all()]
    data = dict(status='success', faculties=faculties)
    return jsonify(data), 200


@adminapi.route('/faculty/add', methods=['POST'])
@decorators.login_required
@decorators.only_admins
def add_faculty():
    required_fields = ('facultyId', 'email', 'password', 'name', 'gender')
    res = dict(status='fail')
    res_code = 200

    data = request.json or request.data or request.form
    if not data:
        res['message'] = 'No data received.'
        return jsonify(res), res_code

    keys = data.keys()
    missing_required_fields = set(required_fields) - set(keys)
    if missing_required_fields:
        res['message'] = 'expected fields {0} not found'\
                         .format(missing_required_fields)
        return jsonify(res), res_code

    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    gender = data.get('gender')
    facultyId = data.get('facultyId')
    blank_values = [key for key in required_fields
                    if not data.get(key, '').strip()]
    if blank_values:
        res['message'] = 'values for field(s) {0} is required'\
                         .format(blank_values)
        return jsonify(res), res_code
    if not validEmail(email):
        res['message'] = 'Invalid Email address %s'.format(email)
        return jsonify(res), res_code

    faculty = Faculty.query.filter_by(facultyId=facultyId).first()
    if not faculty:
        try:
            faculty = Faculty(
                facultyId=facultyId,
                name=name,
                email=email,
                password=password,
                gender=gender)
            # insert the user
            db.session.add(faculty)
            db.session.commit()
            res['status'] = 'success'
            res['faculty'] = faculty.serialize()
            res['message'] = '{0} successfully registered.'\
                             .format(faculty.name)
            res_code = 201
        except Exception as e:
            print e
            res['message'] = 'Some error occurred. Please try again.'
    else:
        res['meassage'] = 'Faculty already exists.'
        res_code = 202
    return jsonify(res), res_code


@adminapi.route('/faculty/<string:facid>/active/<string:active>', methods=['PUT'])
@decorators.login_required
@decorators.only_admins
def set_faculty_state(facid, active):
    # TODO: fill this placeholder
    print facid, active
    return jsonify(dict(status='fail', message='Cannot mark him inactive'))


@adminapi.route('/student/<string:action>', methods=['POST'])
@decorators.login_required
@decorators.only_admins
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


@adminapi.route('/student/delete/<int:studentid>', methods=['GET'])
@decorators.login_required
@decorators.only_admins
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


@adminapi.route('/student/import', methods=['POST'])
@decorators.login_required
@decorators.only_admins
def import_students():
    res = dict(status='fail')
    file = request.files.get('studentsListFile')
    csvreader = csv.reader(file, delimiter=',', quotechar='"')
    # TODO: check type of file
    heading = [title.strip().lower() for title in csvreader.next()]
    required_headers = ('name of the student', 'category', 'student id',
                        'date of birth', 'telephone number', 'preferred branch')
    missing_headers = set(required_headers) - set(heading)
    if missing_headers:
        res['message'] = 'Missing %s required column(s)' % ', '.join(missing_headers)
        return jsonify(res), 200

    getName = itemgetter(heading.index('name of the student'))
    getCategory = itemgetter(heading.index('category'))
    getStudentId = itemgetter(heading.index('student id'))
    getDob = itemgetter(heading.index('date of birth'))
    getContact = itemgetter(heading.index('telephone number'))
    getBranch = itemgetter(heading.index('preferred branch'))

    added = []
    updated = []
    for row in csvreader:
        student = Student.query.filter_by(student_id=getStudentId(row)).first()
        category, student_id = getCategory(row), getStudentId(row)
        name, contact = getName(row), getContact(row)
        dob = datetime.strptime(getDob(row), '%d/%m/%Y').date()
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


def set_punch_in(attendance, date, inTime, studentid=None):
    if inTime != '':
        isValid, dateOrError = parseDate(inTime, '%H:%M:%S')
        if not isValid:
            return jsonify(dict(status='fail',
                                message='time is not valid {}'.format(inTime)
                                )), 200

    if attendance:
        attendance.punch_in = inTime
    else:
        attendance = Attendance(date=date,
                                student_id=studentid,
                                punch_in=inTime,
                                punch_in_by_id=request.user.id)
        db.session.add(attendance)
    db.session.commit()
    return jsonify(dict(status='success',
                        message='student successfuly puched in',
                        attendance=attendance.serialize()
                        )), 200


def set_punch_out(attendance, date, outTime):
    if not attendance or not attendance.punch_in:
        return jsonify(dict(status='fail',
                            message='Cannot puch out before puch in'
                            )), 200
    if outTime != '':
        isValid, dateOrError = parseDate(outTime, '%H:%M:%S')
        if not isValid:
            return jsonify(dict(status='fail',
                                message='{} is not valid time'.format(outTime)
                                )), 200

    attendance.punch_out = outTime
    attendance.punch_out_by_id = request.user.id
    db.session.add(attendance)
    db.session.commit()
    return jsonify(dict(status='success',
                        message='student successfuly puched out',
                        attendance=attendance.serialize()
                        )), 200


def set_comment(attendance, date, comment):
    if not attendance or not attendance.punch_in:
        return jsonify(dict(status='fail',
                            message='Cannot add comment now'
                            )), 200

    attendance.comments = comment
    db.session.add(attendance)
    db.session.commit()
    return jsonify(dict(status='success',
                        message='comment saved successfuly',
                        attendance=attendance.serialize()
                        )), 200


@adminapi.route('/attendance/<string:date>/<int:studentid>/<string:what>',
                methods=['POST'])
@decorators.login_required
@decorators.only_admins
def set_attendance(date, studentid, what):
    res = dict(status='fail')
    res_code = 200

    if what not in ['in', 'out', 'comment']:
        res['message'] = 'Invalid url'
        return jsonify(res), res_code

    data = request.json or request.data or request.form
    print data
    res_code = 200

    isValid, dateOrError = parseDate(date, '%d%m%Y')
    if not isValid:
        res['message'] = 'Invalid date format {0}'.format(date)
        return jsonify(res), res_code
    date = dateOrError.date()
    print date

    student = Student.query.get(studentid)
    print student
    if not student:
        res['message'] = 'Invalid student id'
        return jsonify(res), res_code

    attendance = Attendance.query.filter_by(date=date,
                                            student_id=student.id).first()
    print attendance
    if what == 'in':
        return set_punch_in(attendance, date, data.get('in'), studentid=studentid)
    elif what == 'out':
        return set_punch_out(attendance, date, data.get('out'))
    elif what == 'comment':
        return set_comment(attendance, date, data.get('comment'))
