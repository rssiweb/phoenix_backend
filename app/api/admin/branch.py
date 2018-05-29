from flask import request, Blueprint
from app import db, jsonify
from app.models import Branch
from app.utils import decorators
from app.utils.constants import StatusErrors as errs

api = Blueprint('admin_branch_api', __name__, url_prefix='/api/admin/branch')


@api.route('/add', methods=['POST'])
@decorators.login_required
@decorators.only_admins
def add():
    data = request.json or request.data or request.form
    res_code = 200
    res = dict(status='fail')
    branch_name = data.get('name')
    if not branch_name:
        res['error'] = 'cannot create branch with Empty name'
        return jsonify(res), res_code
    branch = Branch.query.filter_by(name=branch_name).first()
    if branch:
        res['error'] = 'Branch with this name already present'
        return jsonify(res), res_code
    branch = Branch(name=branch_name)
    db.session.add(branch)
    db.session.commit()
    res['status'] = 'success'
    res['branch'] = branch.serialize()
    return jsonify(res), res_code


@api.route('/update/<int:branchid>', methods=['POST'])
@decorators.login_required
@decorators.only_admins
def update(branchid):
    data = request.json or request.data or request.form
    res_code = 200
    res = dict(status='fail')
    branch_name = data.get('name')
    if not branch_name:
        res['statusText'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
        res['statusData'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.type(['name'])
        return jsonify(res), res_code
    branch = Branch.query.filter_by(id=branchid).first()
    if not branch:
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('No such Branch')
        return jsonify(res), res_code
    branch.name = branch_name
    db.session.add(branch)
    db.session.commit()
    res['status'] = 'success'
    res['branch'] = branch.serialize()
    return jsonify(res), res_code
