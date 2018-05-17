from flask import request, Blueprint, send_from_directory
from app import db, jsonify, bcrypt
from app.models import Faculty, Student, Branch, Category
from app.utils import decorators, isValidPassword
from app.utils import report

commonapi = Blueprint('commonapi', __name__, url_prefix='/api')


@commonapi.route('/get_token', methods=['POST'])
def get_token():
    # get the post data
    data = request.json or request.data or request.form
    # check if user already exists
    email = data.get('email')
    faculty = Faculty.query.filter_by(email=email).first()
    if faculty:
        try:
            password = data.get('password')
            if bcrypt.check_password_hash(faculty.password, password):
                res = {
                    'status': 'success',
                    'message': 'log in successful.',
                    'auth_token': faculty.encode_auth_token(email).decode(),
                    'is_admin': faculty.admin,
                    'name': faculty.name
                }
                print res
                return jsonify(res), 202
        except Exception as e:
            print str(e)
            res = {
                'status': 'fail',
                'message': 'Some error occurred. Please try again.'
            }
            return jsonify(res), 401

    res = {
        'status': 'fail',
        'message': 'Username or password is incorrect.',
    }
    return jsonify(res), 401


@commonapi.route('/myprofile', methods=['GET'])
@decorators.login_required
def get_profile():
    res = {}
    res['me'] = request.user.serialize()
    return jsonify(res), 200


@commonapi.route('/changepassword', methods=['POST'])
@decorators.login_required
def reset_password():
    data = request.json or request.data or request.form
    print data
    if not data:
        return jsonify(dict(status='fail', message='No data recevied')), 200
    currentPassword = data.get('currentPassword')
    if not currentPassword or not request.user.check_password(currentPassword):
        return jsonify(dict(status='fail', message='Invalid password')), 200
    new_pswd = data.get('password')
    valid = isValidPassword(new_pswd)
    if not valid or not valid[0]:
        return jsonify(dict(status='fail', message=valid[1])), 200
    fac = request.user
    if not fac:
        return jsonify(dict(status='fail', message='Invalid faculty')), 200
    fac.set_password(new_pswd)
    db.session.commit()
    data = dict(status='success', message='Password updated successfully')
    return jsonify(data), 200


@commonapi.route('/branches', methods=['GET'])
@decorators.login_required
def get_branches():
    data = dict(branches=[branch.serialize() for branch in Branch.query.all()],
                status='success')
    return jsonify(data), 200


@commonapi.route('/categories', methods=['GET'])
@decorators.login_required
def get_categories():
    data = dict(categories=[cat.serialize() for cat in Category.query.all()],
                status='success')
    return jsonify(data), 200


@commonapi.route('/exportReport', methods=['POST'])
@decorators.login_required
def export_report():
    data = request.json or request.data or request.form
    month = data.get('month')
    if not month:
        pass
    ids = data.get('students')
    categories = data.get('categories', [])
    branches = data.get('branches', [])
    students = db.session.query(Student)\
                         .join(Student.category)\
                         .filter(Student.id.in_(ids))\
                         .order_by(Category.name)\
                         .order_by(Student.name).all()
    if categories:
        categories = db.session.query(Category)\
                               .filter(Category.id.in_(categories)).all()
    else:
        categories = Category.query.all()
    if branches:
        branches = db.session.query(Branch)\
                             .filter(Branch.id.in_(branches)).all()
    else:
        branches = Branch.query.all()

    reportFileName = report.buildReport(students, month, categories, branches)
    return send_from_directory(directory='.', filename=reportFileName)
