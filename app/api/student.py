from flask import Blueprint
from app import jsonify
from app.models import Student
from datetime import datetime
from app.utils import decorators
from sqlalchemy import or_

api = Blueprint('student_api', __name__, url_prefix='/api/student')


@api.route('/<string:month>')
@decorators.login_required
def list_students_month(month):
    print month
    endDate = datetime.strptime(month, '%d%B%Y')
    print endDate
    # monthsLastDay = calendar.monthrange(endDate.year, endDate.month)[1]
    # endDate = endDate.replace(day=1)
    # print endDate
    students = Student.query.filter(or_(Student.effective_end_date == None,
                                        Student.effective_end_date >= endDate))
    students = [s.serialize() for s in students]
    data = dict(status='Success', students=students)
    return jsonify(data), 200


@api.route('/all')
@decorators.login_required
def list_allstudents():
    students = [s.serialize() for s in Student.query.all()]
    data = dict(status='Success', students=students)
    return jsonify(data), 200


@api.route('/')
@decorators.login_required
def list_students():
    students = Student.query.filter(Student.isActive != False)
    students = [s.serialize() for s in students]
    data = dict(status='Success', students=students)
    return jsonify(data), 200
