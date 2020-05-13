from flask import Blueprint
from app import jsonify
from app.models import Grade
from app.utils import decorators

api = Blueprint("grade_api", __name__, url_prefix="/api/grade")


@api.route("/<int:branchid>/list", methods=["GET"])
@decorators.login_required
def get_all_by_branch(branchid):
    grades = Grade.query.filter_by(branch_id=branchid).all()
    grades = [grade.serialize() for grade in grades]
    if grades:
        data = dict(status="success", grades=grades)
    else:
        data = dict(status="fail", message="No grades for this branch")
    return jsonify(data), 200
