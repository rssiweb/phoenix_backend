from flask import request, Blueprint
from app import db, jsonify
from app.models import Category, Association, Subject
from app.utils import decorators
from app.utils.constants import StatusErrors as errors

api = Blueprint("admin_category_api", __name__, url_prefix="/api/admin/category")


@api.route("/add", methods=["POST"])
@decorators.login_required
@decorators.only_admins
def add():
    data = request.json or request.data or request.form
    res_code = 200
    res = dict(status="fail")
    catName = data.get("name")
    subjects = data.get("subjects")
    branch_id = data.get("branch_id")
    for key in ("name", "branch_id"):
        val = data.get(key)
        if not val:
            res["statusText"] = errors.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
            res["statusData"] = errors.BLANK_VALUES_FOR_REQUIRED_FIELDS.type([key])
            return jsonify(res), res_code
    cat = Category.query.filter_by(name=catName).first()
    if cat:
        res["error"] = "Category with this name already present"
        return jsonify(res), res_code
    cat = Category(name=catName, branch_id=branch_id)
    print(subjects, data)
    for subid in subjects:
        a = Association()
        sub = Subject.query.filter_by(id=int(subid)).first()
        print(a, sub)
        if a and sub:
            a.subject = sub
            cat.subjects.append(a)
    print(cat, cat.serialize())
    db.session.add(cat)
    db.session.commit()
    res["status"] = "success"
    res["category"] = cat.serialize()
    return jsonify(res), res_code


@api.route("/update/<int:catid>", methods=["POST"])
@decorators.login_required
@decorators.only_admins
def update(catid):
    # cannot update subjects because user might remove the subject from category,
    # in such cases an existing test for that cat-sub would become invalid
    data = request.json or request.data or request.form
    res_code = 200
    res = dict(status="fail")
    cat_name = data.get("name")
    subjects = data.get("subjects")
    if not cat_name:
        res["statusText"] = errors.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
        res["statusData"] = errors.BLANK_VALUES_FOR_REQUIRED_FIELDS.type(["name"])
        return jsonify(res), res_code
    cat = Category.query.filter_by(id=catid).first()
    if not cat:
        res["statusText"] = errors.CUSTOM_ERROR.text
        res["statusData"] = errors.CUSTOM_ERROR.type("No such Category")
        return jsonify(res), res_code
    cat.name = cat_name
    already_added_subs = [a.subject for a in cat.subjects]
    for subid in subjects:
        a = Association()
        sub = Subject.query.filter_by(id=int(subid)).first()
        print(a, sub)
        if a and sub and sub not in already_added_subs:
            a.subject = sub
            cat.subjects.append(a)
    db.session.add(cat)
    db.session.commit()
    res["status"] = "success"
    res["category"] = cat.serialize()
    return jsonify(res), res_code
