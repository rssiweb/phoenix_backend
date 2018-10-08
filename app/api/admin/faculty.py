from flask import request, Blueprint
from app import db, jsonify
from app.models import Faculty
from app.utils import decorators, isValidPassword

api = Blueprint('admin_faculty_api', __name__, url_prefix='/api/admin/faculty')


@api.route('/list')
@decorators.login_required
@decorators.only_admins
def list():
    faculties = [f.serialize() for f in Faculty.query.all()]
    data = dict(status='success', faculties=faculties)
    return jsonify(data), 200


@api.route('/<int:branchid>/list')
@decorators.login_required
@decorators.only_admins
def list_by_branch(branchid):
    faculties = [f.serialize() for f in Faculty.query.filter_by(branch_id=branchid)]
    data = dict(status='success', faculties=faculties)
    return jsonify(data), 200


@api.route('/update', methods=['POST'])
@decorators.login_required
@decorators.only_admins
def update_faculty():
    res = dict(status='fail')
    res_code = 200
    required_fields = ('facultyId', 'email', 'name', 'gender')
    data = request.json or request.data or request.form
    if not data:
        res['message'] = 'No data received.'
        return jsonify(res), res_code
    keys = data.keys()
    missing_required_fields = set(required_fields) - set(keys)
    if missing_required_fields:
        res['message'] = 'expected fields {0} not found'\
                         .format(missing_required_fields)
        return jsonify(res), res_code

    email = data.get('email')
    name = data.get('name')
    gender = data.get('gender')
    facultyId = data.get('facultyId')
    blank_values = [key for key in required_fields
                    if not data.get(key, '').strip()]
    if blank_values:
        res['message'] = 'values for field(s) {0} is required'\
                         .format(blank_values)
        return jsonify(res), res_code
    faculty = Faculty.query.filter_by(facultyId=facultyId).first()
    if not faculty:
        res['message'] = 'Faculty does not exists'
        return jsonify(res), res_code
    faculty.email = email
    faculty.name = name
    faculty.gender = gender
    db.session.commit()
    res['message'] = 'Faculty updated successfully'
    res['status'] = 'success'
    res['faculty'] = faculty.serialize()
    return jsonify(res), res_code


@api.route('/add', methods=['POST'])
@decorators.login_required
@decorators.only_admins
def add():
    res = dict(status='fail')
    res_code = 200

    required_fields = ('facultyId', 'email', 'password', 'name', 'gender', 'branch_id')

    data = request.json or request.data or request.form
    if not data:
        res['message'] = 'No data received.'
        return jsonify(res), res_code

    keys = data.keys()
    missing_required_fields = set(required_fields) - set(keys)
    if missing_required_fields:
        res['message'] = 'expected fields {0} not found'\
                         .format(missing_required_fields)
        return jsonify(res), res_code

    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    gender = data.get('gender')
    facultyId = data.get('facultyId')
    branchId = data.get('branch_id')
    blank_values = [key for key in required_fields
                    if not data.get(key, '').strip()]
    if blank_values:
        res['message'] = 'values for field(s) {0} is required'\
                         .format(blank_values)
        return jsonify(res), res_code
    faculty = Faculty.query.filter_by(facultyId=facultyId).first()
    if not faculty:
        try:
            faculty = Faculty(
                facultyId=facultyId,
                name=name,
                email=email,
                password=password,
                gender=gender,
                branch_id=branchId)
            # insert the user
            db.session.add(faculty)
            db.session.commit()
            res['status'] = 'success'
            res['faculty'] = faculty.serialize()
            res['message'] = '{0} successfully registered.'\
                             .format(faculty.name)
            res_code = 201
        except Exception as e:
            print e
            res['message'] = 'Some error occurred. Please try again.'
    else:
        res['message'] = 'Faculty already exists.'
        res_code = 202
    return jsonify(res), res_code


@api.route('/reset', methods=['POST'])
@decorators.login_required
@decorators.only_admins
def reset_faculty_password():
    data = request.json or request.data or request.form
    if not data:
        return jsonify(dict(status='fail', message='No data recevied')), 200
    facId = data.get('facultyId')
    if not facId:
        return jsonify(dict(status='fail', message='Invalid faculty')), 200
    pswd = data.get('password')
    valid = isValidPassword(pswd)
    if not valid or not valid[0]:
        return jsonify(dict(status='fail', message=valid[1])), 200
    fac = Faculty.query.filter_by(facultyId=facId).first()
    if not fac:
        return jsonify(dict(status='fail', message='Invalid faculty')), 200
    fac.set_password(pswd)
    db.session.commit()
    return jsonify(dict(status='success', message='Password updated successfully')), 200


@api.route('/<string:facid>/active/<string:active>', methods=['PUT'])
@decorators.login_required
@decorators.only_admins
def set_faculty_state(facid, active):
    active = active == 'true'
    if not facid:
        return jsonify(dict(status='fail', message='Invalid faculty')), 200
    fac = Faculty.query.filter_by(facultyId=facid).first()
    if not fac:
        return jsonify(dict(status='fail', message='Invalid faculty')), 200
    if fac.superUser:
        return jsonify(dict(status='fail', message='Cannot mark him Inactive')), 200
    fac.isActive = active
    db.session.commit()
    return jsonify(dict(status='success', message='Successfully', active=fac.isActive))

@api.route('/<string:facid>/admin/<string:admin>', methods=['POST'])
@decorators.login_required
@decorators.only_admins
def set_faculty_admin(facid, admin):
    admin = str(admin).lower() == 'true'
    if not facid:
        return jsonify(dict(status='fail', message='Invalid faculty')), 200
    fac = Faculty.query.filter_by(facultyId=facid).first()
    if not fac:
        return jsonify(dict(status='fail', message='Invalid faculty')), 200
    if fac.superUser:
        return jsonify(dict(status='fail', message='Cannot update super user')), 200
    fac.admin = admin
    db.session.commit()
    return jsonify(dict(status='success',
                        message='{} is {} Admin'.format(fac.name, 'now an' if fac.admin else 'no longer an'),
                        admin=fac.admin))
