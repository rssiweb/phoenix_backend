from flask import request, Blueprint
from app import db, jsonify
from app.models import Branch
from app.utils import decorators

api = Blueprint('admin_branch_api', __name__, url_prefix='/api/admin/branch')


@api.route('/add', methods=['POST'])
@decorators.login_required
@decorators.only_admins
@decorators.addLag
def add_branch():
    data = request.json or request.data or request.form
    res_code = 200
    res = dict(status='fail')
    branch_name = data.get('name')
    print branch_name
    if not branch_name:
        res['error'] = 'cannot create branch with Empty name'
        return jsonify(res), res_code
    branch = Branch.query.filter_by(name=branch_name).first()
    print branch
    if branch:
        res['error'] = 'Branch with this name already present'
        return jsonify(res), res_code
    branch = Branch(name=branch_name)
    db.session.add(branch)
    db.session.commit()
    res['status'] = 'success'
    res['branch'] = branch.serialize()
    return jsonify(res), res_code
