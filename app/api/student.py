from flask import Blueprint
from app import jsonify
from app.models import Student
from datetime import datetime
from app.utils import decorators
from sqlalchemy import or_

api = Blueprint('student_api', __name__, url_prefix='/api/student')


@api.route('/<string:endDate>/all')
@decorators.login_required
def list_all_by_endDate(endDate):
    print endDate
    endDate = datetime.strptime(endDate, '%d%B%Y')
    print endDate
    # monthsLastDay = calendar.monthrange(endDate.year, endDate.month)[1]
    # endDate = endDate.replace(day=1)
    # print endDate
    students = Student.query.filter(or_(Student.effective_end_date==None,
                                        Student.effective_end_date>=endDate))
    students = [s.serialize() for s in students]
    data = dict(status='success', students=students)
    return jsonify(data), 200


@api.route('/list')
@decorators.login_required
def list():
    students = Student.query.filter(Student.isActive!=False)
    students = [s.serialize() for s in students]
    data = dict(status='success', students=students)
    return jsonify(data), 200


@api.route('/all')
@decorators.login_required
def list_all():
    students = Student.query.all()
    students = [s.serialize() for s in students]
    data = dict(status='success', students=students)
    return jsonify(data), 200


@api.route('/<int:branchid>/list')
@decorators.login_required
def list_by_branch(branchid):
    students = Student.query.filter(Student.branch_id==branchid,
                                    Student.isActive!=False)
    students = [s.serialize() for s in students]
    data = dict(status='success', students=students)
    return jsonify(data), 200


@api.route('/<int:branchid>/all')
@decorators.login_required
def list_all_by_branch(branchid):
    students = [s.serialize() for s in Student.query.filter_by(branch_id=branchid)]
    data = dict(status='success', students=students)
    return jsonify(data), 200
