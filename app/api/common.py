from flask import request, Blueprint
from app import db, jsonify, bcrypt
from app.models import Faculty
from app.utils import decorators, isValidPassword
import cloudinary

api = Blueprint('common_api', __name__, url_prefix='/api')


@api.route('/get_token', methods=['POST'])
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
                image = None
                if faculty.image:
                    url = faculty.image.split('/image/upload/')[1]
                    url = '/'.join(url.split('/')[1:]) if url else url
                    image = cloudinary.CloudinaryImage(url).build_url(transformation=[
                        {'width': 150, 'height': 150},
                    ])
                res = {
                    'status': 'success',
                    'message': 'log in successful.',
                    'auth_token': faculty.encode_auth_token(email).decode(),
                    'is_admin': faculty.admin,
                    'name': faculty.name,
                    'profile_image': image,
                }
                return jsonify(res), 202
        except Exception as e:
            print(str(e))
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


@api.route('/myprofile', methods=['GET'])
@decorators.login_required
def get_profile():
    res = dict(status='success')
    res['me'] = request.user.serialize()
    return jsonify(res), 200


@api.route('/changepassword', methods=['POST'])
@decorators.login_required
def reset_password():
    data = request.json or request.data or request.form
    print(data)
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
