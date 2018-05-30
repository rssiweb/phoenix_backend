from flask import Blueprint
from app import jsonify
from app.models import Marks, Test
from app.utils import decorators
from app.utils.constants import StatusErrors as errs

api = Blueprint('marks_api', __name__, url_prefix='/api/marks')


@api.route('/<int:testid>', methods=['GET'])
@decorators.login_required
def get_by_test(testid):
    res = dict(status='fail')
    test = Test.query.get(testid)
    if not test:
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('No such Test')
        return jsonify(res), 200
    marks = Marks.query.filter_by(test_id=test.id).all()
    marks = [mark.serialize() for mark in marks]
    res['status'] = 'success'
    return jsonify(res), 200
