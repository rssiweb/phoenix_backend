from flask import Blueprint
from app import jsonify
from app.models import Branch
from app.utils import decorators

api = Blueprint("branch_api", __name__, url_prefix="/api/branch")


@api.route("/list", methods=["GET"])
@decorators.login_required
def list():
    branches = [branch.serialize() for branch in Branch.query.all()]
    data = dict(status="success", branches=branches)
    return jsonify(data), 200


@api.route("/<int:branchid>", methods=["GET"])
@decorators.login_required
def get_branch(branchid):
    branch = Branch.query.get(branchid)
    if branch:
        data = dict(status="success", branch=branch.serialize())
    else:
        data = dict(status="fail", message="No such Branch found")
    return jsonify(data), 200
