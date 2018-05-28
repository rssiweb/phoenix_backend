from flask import request, Blueprint
from app import jsonify, db
from app.models import Subject
from app.utils import decorators
from app.utils.constants import StatusErrors as errs

api = Blueprint('admin_subject_api', __name__, url_prefix='/api/admin/subject')


@api.route('/add', methods=['POST'])
@decorators.login_required
@decorators.only_admins
@decorators.addLag
def add():
    data = request.json or request.data or request.form
    res_code = 200
    res = dict(status='fail')
    name = data.get('name')
    branch_id = data.get('branch_id')
    for key in ('name', 'branch_id'):
        val = data.get(key)
        if not val:
            res['statusText'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
            res['statusData'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.type([key])
            return jsonify(res), res_code
    subject = Subject.query.filter_by(name=name).first()
    if subject:
        res['error'] = 'Subject with this name already present'
        return jsonify(res), res_code
    subject = Subject(name=name, branch_id=branch_id)
    db.session.add(subject)
    db.session.commit()
    res['status'] = 'success'
    res['subject'] = subject.serialize()
    return jsonify(res), res_code


@api.route('/update/<int:subjectid>', methods=['POST'])
@decorators.login_required
@decorators.only_admins
@decorators.addLag
def update(subjectid):
    data = request.json or request.data or request.form
    res_code = 200
    res = dict(status='fail')
    subject_name = data.get('name')
    if not subject_name:
        res['statusText'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
        res['statusData'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.type(['name'])
        return jsonify(res), res_code
    subject = Subject.query.filter_by(id=subjectid).first()
    if not subject:
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('No such Subject')
        return jsonify(res), res_code
    subject.name = subject_name
    db.session.add(subject)
    db.session.commit()
    res['status'] = 'success'
    res['subject'] = subject.serialize()
    return jsonify(res), res_code
