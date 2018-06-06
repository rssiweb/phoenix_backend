from flask import Blueprint, request
from app import jsonify, db
from app.models import Marks, Test, Student
from app.utils import decorators
from app.utils.constants import StatusErrors as errs

api = Blueprint('marks_api', __name__, url_prefix='/api/marks')


@api.route('/<int:testid>', methods=['GET'])
@decorators.login_required
def get_by_test(testid):
    res = dict(status='fail')
    test = Test.query.get(testid)
    if not test:
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('No such Test')
        return jsonify(res), 200
    marks = Marks.query.filter_by(test_id=test.id).all()
    marks = [mark.serialize() for mark in marks]
    res['marks'] = marks
    res['status'] = 'success'
    return jsonify(res), 200


@api.route('/set/<int:testid>/<int:studentid>', methods=['POST'])
@decorators.login_required
def set_marks(testid, studentid):
    res = dict(status='fail')
    data = request.json or request.data or request.form
    test = Test.query.get(testid)
    if not test:
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('No such Test')
        return jsonify(res), 200
    if not request.user or (not request.user.admin and request.user.id != test.evaluator_id):
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('You are not authrized.')
        return jsonify(res), 200
    student = Student.query.get(studentid)
    if not student:
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('No such Student')
        return jsonify(res), 200
    comments = data.get('comment')
    marksObjtained = data.get('marks')
    try:
        marksObjtained = float(marksObjtained)
    except Exception:
        marksObjtained = None
    comments = data.get('comment')
    marks = Marks.query.filter_by(test_id=test.id, student_id=student.id).first()
    if not marks:
        if not marksObjtained:
            res['statusText'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
            res['statusData'] = errs.BLANK_VALUES_FOR_REQUIRED_FIELDS.type(['marks'])
            return jsonify(res), 200
        if comments:
            marks = Marks(test_id=test.id, student_id=student.id, marks=marksObjtained, comments=comments)
        else:
            marks = Marks(test_id=test.id, student_id=student.id, marks=marksObjtained)
    else:
        if marksObjtained:
            marks.marks = marksObjtained
        if comments:
            marks.comments = comments
    db.session.add(marks)
    db.session.commit()
    res['status'] = 'success'
    res['marks'] = marks.serialize()
    res['message'] = 'Marks and Comments saved'
    return jsonify(res), 200


@api.route('/delete/<int:testid>', methods=['GET'])
@decorators.login_required
def delete_marks(testid):
    res = dict(status='fail')
    test = Test.query.get(testid)
    if not test:
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('No such Test')
        return jsonify(res), 200
    if not request.user or (not request.user.admin and request.user.id != test.evaluator_id):
        res['statusText'] = errs.CUSTOM_ERROR.text
        res['statusData'] = errs.CUSTOM_ERROR.type('You are not authrized.')
        return jsonify(res), 200
    Marks.query.filter_by(test_id=test.id).delete()
    db.session.commit()
    res['status'] = 'success'
    res['message'] = 'All Marks deleted'
    return jsonify(res), 200
