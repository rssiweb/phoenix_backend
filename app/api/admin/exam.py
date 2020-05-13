from flask import request, Blueprint
from app import jsonify, db
from app.models import Exam
from app.utils import decorators
from app.utils.constants import StatusErrors as errors

api = Blueprint("admin_exam_api", __name__, url_prefix="/api/admin/exam")


@api.route("/add", methods=["POST"])
@decorators.login_required
@decorators.only_admins
def add():
    data = request.json or request.data or request.form
    res_code = 200
    res = dict(status="fail")
    name = data.get("name")
    branch_id = data.get("branch_id")
    for key in ("name", "branch_id"):
        val = data.get(key)
        if not val:
            res["statusText"] = errors.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
            res["statusData"] = errors.BLANK_VALUES_FOR_REQUIRED_FIELDS.type([key])
            return jsonify(res), res_code
    exam = Exam.query.filter_by(branch_id=branch_id, name=name).first()
    if exam:
        res["statusText"] = errors.CUSTOM_ERROR.text
        res["statusData"] = errors.CUSTOM_ERROR.type(
            'Exam with name "%s" already exists' % exam.name
        )
        return jsonify(res), res_code
    exam = Exam(name=name, branch_id=branch_id)
    db.session.add(exam)
    db.session.commit()
    res["status"] = "success"
    res["exam"] = exam.serialize()
    return jsonify(res), res_code


@api.route("/delete/<int:examid>", methods=["GET"])
@decorators.login_required
@decorators.only_admins
def delete(examid):
    exam = Exam.query.get(examid)
    res = dict(status="fail")
    if exam:
        db.session.delete(exam)
        db.session.commit()
        res["status"] = "success"
    res["id"] = exam.id
    return jsonify(res), 200
