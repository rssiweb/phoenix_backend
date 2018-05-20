from flask import request, Blueprint
from app import db, jsonify
from app.models import Category
from app.utils import decorators

api = Blueprint('admin_category_api', __name__, url_prefix='/api/admin/category')


@api.route('/add', methods=['POST'])
@decorators.login_required
@decorators.only_admins
@decorators.addLag
def add_category():
    data = request.json or request.data or request.form
    res_code = 200
    res = dict(status='fail')
    catName = data.get('name')
    if not catName:
        res['error'] = 'Empty Category name'
        return jsonify(res), res_code
    cat = Category.query.filter_by(name=catName).first()
    print cat
    if cat:
        res['error'] = 'Category with this name already present'
        return jsonify(res), res_code
    cat = Category(name=catName)
    db.session.add(cat)
    db.session.commit()
    res['status'] = 'success'
    res['category'] = cat.serialize()
    return jsonify(res), res_code
