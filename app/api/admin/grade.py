from flask import Blueprint, request
from app import jsonify, db
from app.models import Grade, Branch
from app.utils import decorators
from app.utils.constants import StatusErrors as errs

api = Blueprint('admin_grade_api', __name__, url_prefix='/api/admin/grade')


@api.route('/add/<int:branchid>', methods=['POST'])
@decorators.login_required
def add(branchid):
    res = dict(status='fail')
    data = request.json or request.data or request.form
    print(data)
    req_values = 'min max grade comment'.split()
    for key in req_values:
        val = data.get(key)
        if not val:
            res['statusText'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
            res['statusData'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.type([key])
            return jsonify(res), 200
    lower = data.get('min')
    upper = data.get('max')
    gradeTxt = data.get('grade')
    comment = data.get('comment')
    try:
        lower = float(lower)
    except Exception:
        res['statusText'] = errs.INVALID_VALUE_TYPE.text
        res['statusData'] = errs.INVALID_VALUE_TYPE.type(('number or decimal', lower))
        return jsonify(res), 200
    try:
        upper = float(upper)
    except Exception:
        res['statusText'] = errs.INVALID_VALUE_TYPE.text
        res['statusData'] = errs.INVALID_VALUE_TYPE.type(('number or decimal', upper))
        return jsonify(res), 200

    grades = Grade.query.filter_by(branch_id=branchid).all()
    for grade in grades:
        if (grade.lower, grade.upper) == (lower, upper):
            res['statusText'] = errs.CUSTOM_ERROR.text
            res['statusData'] = errs.CUSTOM_ERROR.type('A Grade for this marks range already present')
            return jsonify(res), 200
    grade = Grade(lower, upper, gradeTxt, branchid, comment)
    db.session.add(grade)
    db.session.commit()
    res['status'] = 'success'
    res['grade'] = grade.serialize()
    return jsonify(res), 200


@api.route('/update/<int:branchid>/<int:gradeid>', methods=['POST'])
@decorators.login_required
def update(branchid, gradeid):
    res = dict(status='fail')
    data = request.json or request.data or request.form
    branch = Branch.query.get(branchid)
    grade = Grade.query.get(gradeid)
    if not grade:
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('No such Grade')
        return jsonify(res), 200
    if not branch:
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('No such Branch')
        return jsonify(res), 200
    req_key = ('grade', 'min', 'max', 'comment')
    for key in req_key:
        val = data.get(key)
        if not val:
            res['statusText'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
            res['statusData'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.type([key])
            return jsonify(res), 200
    if grade.branch_id != branch.id:
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('grade is not in this branch')
        return jsonify(res), 200
    gradeTxt = data.get('grade')
    lower = data.get('min')
    upper = data.get('max')
    comment = data.get('comment')
    try:
        lower = float(lower)
    except Exception:
        res['statusText'] = errs.INVALID_VALUE_TYPE.text
        res['statusData'] = errs.INVALID_VALUE_TYPE.type(('number or decimal', lower))
        return jsonify(res), 200
    try:
        upper = float(upper)
    except Exception:
        res['statusText'] = errs.INVALID_VALUE_TYPE.text
        res['statusData'] = errs.INVALID_VALUE_TYPE.type(('number or decimal', upper))
        return jsonify(res), 200
    grade.grade = gradeTxt
    grade.lower = lower
    grade.upper = upper
    grade.comment = comment
    db.session.add(grade)
    db.session.commit()
    res['status'] = 'success'
    res['grade'] = grade.serialize()
    return jsonify(res), 200
