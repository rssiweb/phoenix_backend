from flask import request, Blueprint
from app import jsonify, db
from app.models import Exam
from app.utils import decorators

api = Blueprint('admin_exam_api', __name__, url_prefix='/api/admin/exam')


@api.route('/add', methods=['POST'])
@decorators.login_required
@decorators.only_admins
def add():
    data = request.json or request.data or request.form
    res_code = 200
    res = dict(status='fail')
    name = data.get('name')
    if not name:
        res['error'] = 'cannot create Exam with empty name'
        return jsonify(res), res_code
    exam = Exam.query.filter_by(name=name).first()
    if exam:
        res['error'] = 'Exam with this name already present'
        return jsonify(res), res_code
    exam = Exam(name=name)
    db.session.add(exam)
    db.session.commit()
    res['status'] = 'success'
    res['exam'] = exam.serialize()
    return jsonify(res), res_code


@api.route('/delete/<int:examid>', methods=['GET'])
@decorators.login_required
@decorators.only_admins
def delete(examid):
    exam = Exam.query.get(examid)
    res = dict(status='fail')
    if exam:
        db.session.delete(exam)
        db.session.commit()
        res['status'] = 'success'
    res['id'] = exam.id
    return jsonify(res), 200
