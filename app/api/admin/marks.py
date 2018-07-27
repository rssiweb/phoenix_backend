from flask import Blueprint
from app import jsonify
from app.models import Marks, Exam
from app.utils import decorators
from app.utils.constants import StatusErrors as errs

api = Blueprint('admin_marks_api', __name__, url_prefix='/api/admin/marks')


@api.route('/exam/<int:examid>', methods=['GET'])
@decorators.login_required
@decorators.only_admins
def get_by_exam(examid):
    res = dict(status='fail')
    exam = Exam.query.get(examid)
    if not exam:
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('No Such exam')
        return jsonify(res), 200
    marks = {test.id: [m.serialize() for m in Marks.query.filter_by(test_id=test.id).all()] for test in exam.tests}
    res['marks'] = marks
    res['status'] = 'success'
    return jsonify(res), 200
