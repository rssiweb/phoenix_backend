from flask import Blueprint
from app import jsonify
from app.models import Test
from app.utils import decorators

api = Blueprint('test_api', __name__, url_prefix='/api/test')


@api.route('/list', methods=['GET'])
@decorators.login_required
def list():
    tests = [t.serialize() for t in Test.query.all()]
    data = dict(status='success', tests=tests)
    return jsonify(data), 200


@api.route('/<int:testid>', methods=['GET'])
@decorators.login_required
def get_test(testid):
    test = Test.query.get(testid)
    if test:
        data = dict(status='success', test=test.serialize())
    else:
        data = dict(status='fail', message='No such Test found')
    return jsonify(data), 200
