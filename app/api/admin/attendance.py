from flask import request, Blueprint
from app import db, jsonify
from app.models import Student, Attendance
from app.utils import decorators, parseDate

api = Blueprint('admin_attendance_api', __name__, url_prefix='/api/admin/attendance')


@api.route('/<string:date>/<int:studentid>/<string:what>', methods=['POST'])
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


def set_punch_in(attendance, date, inTime, studentid=None):
    msg = 'student successfuly puched in',
    if inTime == '' and attendance:
        attendance.punch_in = None
        db.session.delete(attendance)
        msg = 'attendance delete'
    else:
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
                        message=msg,
                        attendance=attendance.serialize()
                        )), 200


def set_punch_out(attendance, date, outTime):
    if not attendance or not attendance.punch_in:
        return jsonify(dict(status='fail',
                            message='Cannot puch out before puch in',
                            attendance=attendance.serialize()
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
