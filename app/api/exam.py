from flask import Blueprint
from app import jsonify
from app.models import Exam
from app.utils import decorators

api = Blueprint('exam_api', __name__, url_prefix='/api/exam')


@api.route('/list', methods=['GET'])
@decorators.login_required
def list():
    exams = [e.serialize() for e in Exam.query.all()]
    data = dict(status='success', exams=exams)
    return jsonify(data), 200


@api.route('/<int:examid>', methods=['GET'])
@decorators.login_required
def get_exam(examid):
    exam = Exam.query.get(examid)
    if exam:
        data = dict(status='success', exam=exam.serialize())
    else:
        data = dict(status='fail', message='No such Exam found')
    return jsonify(data), 200


@api.route('/<int:branchid>/list', methods=['GET'])
@decorators.login_required
def get_all_by_branch(branchid):
    exams = Exam.query.filter_by(branch_id=branchid).all()
    exams = [e.serialize() for e in exams]
    data = dict(status='success', exams=exams)
    return jsonify(data), 200
