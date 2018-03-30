from flask import request, Blueprint
from app import db, jsonify, bcrypt
from app.models import Faculty, Student, Attendance
from datetime import datetime
from app.utils import decorators, parseDate

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/get_token', methods=['POST'])
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
                return jsonify(res), 202
        except Exception as e:
            print str(e)
            res = {
                'status': 'fail',
                'message': 'Some error occurred. Please try again.'
            }
            return jsonify(res), 401

    res = {
        'status': 'fail',
        'message': 'Username or password is incorrect.',
    }
    return jsonify(res), 401


@api.route('/student')
@decorators.login_required
def list_students():
    students = [s.serialize() for s in Student.query.all()]
    data = dict(status='Success', students=students)
    return jsonify(data), 200


@api.route('/attendance/<string:date>', methods=['GET'])
@decorators.login_required
def get_attendance(date):
    date = datetime.strptime(date, '%d%m%Y').date()
    attendance = Attendance.query.filter_by(date=date).all()
    attendance = [att.serialize() for att in attendance]
    data = dict(status=True, date=date, attendance=attendance)
    return jsonify(data), 200


def set_punch_in(attendance, inTime, studentid=None):
    if attendance and attendance.punch_in:
        return jsonify(dict(status='fail',
                            message='student already punched in'
                            )), 200
    isValid, dateOrError = parseDate(inTime, '%H:%M:%S')
    if not isValid:
        return jsonify(dict(status='fail',
                            message='time is not valid {}'.format(inTime)
                            )), 200

    attendance = Attendance(date=datetime.today(),
                            student_id=studentid,
                            punch_in=inTime,
                            punch_in_by_id=request.user.id)
    db.session.add(attendance)
    db.session.commit()
    return jsonify(dict(status='success',
                        message='student successfuly puched in',
                        attendance=attendance.serialize()
                        )), 200


def set_punch_out(attendance, outTime):
    print attendance
    if not attendance or not attendance.punch_in:
        return jsonify(dict(status='fail',
                            message='Cannot puch out before puch in'
                            )), 200
    if attendance.punch_out:
        return jsonify(dict(status='fail',
                            message='student already punched out'
                            )), 200
    isValid, dateOrError = parseDate(outTime, '%H:%M:%S')
    if not isValid:
        return jsonify(dict(status='fail',
                            message='time is not valid {}'.format(outTime)
                            )), 200

    attendance.punch_out = outTime
    attendance.punch_out_by_id = request.user.id
    db.session.add(attendance)
    db.session.commit()
    return jsonify(dict(status='success',
                        message='student successfuly puched out',
                        attendance=attendance.serialize()
                        )), 200


def set_comment(attendance, comment):
    if not attendance or not attendance.punch_in:
        return jsonify(dict(status='fail',
                            message='Cannot add comment now'
                            )), 200
    if attendance and not attendance.punch_out:
        attendance.comments = comment
        db.session.add(attendance)
        db.session.commit()
        return jsonify(dict(status='success',
                            message='comment saved successfuly',
                            attendance=attendance.serialize()
                            )), 200


@api.route('/attendance/<int:studentid>/<string:what>',
           methods=['POST'])
@decorators.login_required
def set_attendance(studentid, what):
    res = dict(status='fail')
    res_code = 200

    if what not in ['in', 'out', 'comment']:
        res['message'] = 'Invalid url'
        return jsonify(res), res_code

    faculty = Faculty.query.get(request.user.id)
    print faculty

    data = request.json or request.data or request.form
    print data

    if what in ('in', 'out'):
        isValid, timeOrError = parseDate(data.get(what), '%H:%M:%S')
        if not isValid:
            print timeOrError
            res['message'] = 'Invalid time format '
            return jsonify(res), res_code

    student = Student.query.get(studentid)
    print student
    if not student:
        res['message'] = 'Invalid student id'
        return jsonify(res), res_code

    attendance = Attendance.query.filter_by(date=datetime.today().date(),
                                            student_id=student.id).first()

    if what == 'in':
        return set_punch_in(attendance, data.get('in'), studentid=studentid)
    elif what == 'out':
        return set_punch_out(attendance, data.get('out'))
    elif what == 'comment':
        return set_comment(attendance, data.get('comment'))
