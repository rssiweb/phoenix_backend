from flask import Blueprint
from app import jsonify
from app.models import Test
from app.utils import decorators

api = Blueprint("test_api", __name__, url_prefix="/api/test")


@api.route("/<int:examid>/list", methods=["GET"])
@decorators.login_required
def get_by_exam(examid):
    tests = [t.serialize() for t in Test.query.filter_by(exam_id=examid)]
    data = dict(status="success", tests=tests)
    return jsonify(data), 200


@api.route("/<int:testid>", methods=["GET"])
@decorators.login_required
def get_test(testid):
    test = Test.query.get(testid)
    if test:
        data = dict(status="success", test=test.serialize())
    else:
        data = dict(status="fail", message="No such Test found")
    return jsonify(data), 200
