from flask import Blueprint
from app import jsonify
from app.models import Category
from app.utils import decorators

api = Blueprint('category_api', __name__, url_prefix='/api/category')


@api.route('/list', methods=['GET'])
@decorators.login_required
def list():
    categories = [cat.serialize() for cat in Category.query.all()]
    data = dict(categories=categories, status='success')
    return jsonify(data), 200


@api.route('/<int:branchid>/list', methods=['GET'])
@decorators.login_required
@decorators.addLag
def list_by_branch(branchid):
    categories = [s.serialize() for s in Category.query.filter_by(branch_id=branchid)]
    data = dict(status='success', categories=categories)
    return jsonify(data), 200
