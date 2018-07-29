from flask import request, Blueprint
from app import db, jsonify
from app.models import Test, Exam, Subject, Category, Association, Faculty, Student, StudentTestAssociation
from app.utils import decorators
from app.utils.constants import StatusErrors as error
from datetime import datetime

api = Blueprint('admin_test_api', __name__, url_prefix='/api/admin/test')


@api.route('/add', methods=['POST'])
@decorators.login_required
@decorators.only_admins
@decorators.addLag
def add():
    data = request.json or request.data or request.form
    print data
    res_code = 200
    res = dict(status='fail')
    required_fields = set(['name', 'maxMarks', 'examId', 'subject', 'category', 'date'])
    missing_keys = required_fields.difference(set(data.keys()))
    if missing_keys:
        res['statusText'] = error.MISSING_REQUIRED_FIELDS.text
        res['statusData'] = error.MISSING_REQUIRED_FIELDS.type(missing_keys)
        return jsonify(res), res_code

    # validate data

    blank_value_keys = [k for k in required_fields if not data.get(k)]
    if blank_value_keys:
        res['statusText'] = error.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
        res['statusData'] = error.BLANK_VALUES_FOR_REQUIRED_FIELDS.type(blank_value_keys)
        return jsonify(res), res_code

    name = data.get('name')
    max_marks = data.get('maxMarks')
    exam_id = data.get('examId')
    subject_id = data.get('subject')
    category_id = data.get('category')
    date = data.get('date')
    evaluator_id = data.get('evaluator')

    keys = ['subject', 'category', 'examId', 'maxMarks']
    if evaluator_id:
        keys.append('evaluator')
    for key in keys:
        if not data.get(key).isdigit():
            res['statusText'] = error.INVALID_VALUE_TYPE.text
            res['statusData'] = error.INVALID_VALUE_TYPE.type(['number', key])
            return jsonify(res), res_code
    try:
        date = datetime.strptime(date, '%d/%m/%Y').date()
    except ValueError:
        res['statusText'] = error.INVALID_FORMAT.text
        res['statusData'] = error.INVALID_FORMAT.type(['dd/mm/yyyy', date])
        return jsonify(res), res_code

    if date < datetime.today().date():
        res['statusText'] = error.CUSTOM_ERROR.text
        res['statusData'] = error.CUSTOM_ERROR.type('Test date %s is not a future date' % date.strftime('%d/%m/%Y'))
        return jsonify(res), res_code

    subject_id = int(subject_id)
    category_id = int(category_id)
    exam_id = int(exam_id)
    max_marks = float(max_marks)
    if evaluator_id:
        evaluator_id = int(evaluator_id)

    exam = Exam.query.get(exam_id)
    subject = Subject.query.get(subject_id)
    category = Category.query.get(category_id)
    objs = [exam, subject, category]
    names = ['Exam', 'Subject', 'Category']
    evaluator = None
    if evaluator_id:
        evaluator = Faculty.query.get(evaluator_id)
        objs.append(evaluator)
        names.append('Evaluator')
    for obj, modalName in zip(objs, names):
        if not obj:
            res['statusText'] = error.CUSTOM_ERROR.text
            res['statusData'] = error.CUSTOM_ERROR.type('Cannot create Test for non-existing %s' % modalName)
            return jsonify(res), res_code

    test = Test.query.filter_by(name=name, exam_id=exam_id).first()
    if test:
        res['statusText'] = error.DUPLICATE_ID.text
        res['statusData'] = error.DUPLICATE_ID.type(['Test Code', name])
        return jsonify(res), res_code
    cat_sub_association = Association.query.filter_by(category=category, subject=subject).first()
    if not cat_sub_association:
        res['statusText'] = error.CUSTOM_ERROR.text
        msg = 'Category %s does not have Subject %s' % (category.name, subject.name)
        res['statusData'] = error.CUSTOM_ERROR.type(msg)

    test = Test(name=name, max_marks=max_marks, exam_id=exam_id, cat_sub_id=cat_sub_association.id, test_date=date)
    if (evaluator is not None):
        test.evaluator_id = evaluator.id

    for std in Student.query.filter_by(category=category, branch_id=exam.branch_id, isActive=True).all():
        association = StudentTestAssociation()
        association.student = std
        association.exam = exam
        test.students.append(association)

    db.session.add(test)
    db.session.commit()
    res['status'] = 'success'
    res['test'] = test.serialize()
    return jsonify(res), res_code


@api.route('/update/<int:testid>', methods=['POST'])
@decorators.login_required
@decorators.only_admins
@decorators.addLag
def update(testid):
    data = request.json or request.data or request.form
    print data
    res_code = 200
    res = dict(status='fail')

    test = Test.query.get(testid)
    if not test:
        res['statusText'] = error.CUSTOM_ERROR.text
        res['statusData'] = error.CUSTOM_ERROR.type('No such test')
        return jsonify(res), res_code

    required_fields = set(['maxMarks', 'subject', 'category', 'date'])
    missing_keys = required_fields.difference(set(data.keys()))
    if missing_keys:
        res['statusText'] = error.MISSING_REQUIRED_FIELDS.text
        res['statusData'] = error.MISSING_REQUIRED_FIELDS.type(missing_keys)
        return jsonify(res), res_code

    # validate data

    blank_value_keys = [k for k in required_fields if not data.get(k)]
    if blank_value_keys:
        res['statusText'] = error.BLANK_VALUES_FOR_REQUIRED_FIELDS.text
        res['statusData'] = error.BLANK_VALUES_FOR_REQUIRED_FIELDS.type(blank_value_keys)
        return jsonify(res), res_code

    max_marks = data.get('maxMarks')
    subject_id = data.get('subject')
    category_id = data.get('category')
    date = data.get('date')
    evaluator_id = data.get('evaluator')

    keys = ['subject', 'category', 'examId', 'maxMarks']
    if evaluator_id is not None:
        keys.append('evaluator')
    for key in keys:
        if not data.get(key).isdigit():
            res['statusText'] = error.INVALID_VALUE_TYPE.text
            res['statusData'] = error.INVALID_VALUE_TYPE.type(['number', key])
            return jsonify(res), res_code
    try:
        date = datetime.strptime(date, '%d/%m/%Y').date()
    except ValueError:
        res['statusText'] = error.INVALID_FORMAT.text
        res['statusData'] = error.INVALID_FORMAT.type(['dd/mm/yyyy', date])
        return jsonify(res), res_code

    if date < datetime.today().date():
        res['statusText'] = error.CUSTOM_ERROR.text
        res['statusData'] = error.CUSTOM_ERROR.type('Test date %s is not a future date' % date.strftime('%d/%m/%Y'))
        return jsonify(res), res_code

    subject_id = int(subject_id)
    category_id = int(category_id)
    max_marks = float(max_marks)
    if evaluator_id is not None:
        evaluator_id = int(evaluator_id)

    subject = Subject.query.get(subject_id)
    category = Category.query.get(category_id)
    objs, names = [subject, category], ['Subject', 'Category']
    evaluator = None
    if evaluator_id is not None:
        evaluator = Faculty.query.get(evaluator_id)
        objs.append(evaluator)
        names.append('Evaluator')
    for obj, modalName in zip(objs, names):
        if not obj:
            res['statusText'] = error.CUSTOM_ERROR.text
            res['statusData'] = error.CUSTOM_ERROR.type('Cannot create Test for non-existing %s' % modalName)
            return jsonify(res), res_code

    cat_sub_association = Association.query.filter_by(category=category, subject=subject).first()
    if not cat_sub_association:
        res['statusText'] = error.CUSTOM_ERROR.text
        msg = 'Category %s does not have Subject %s' % (category.name, subject.name)
        res['statusData'] = error.CUSTOM_ERROR.type(msg)
    test.category = category
    test.subject = subject
    test.max_marks = max_marks
    test.cat_sub_id = cat_sub_association.id
    test.date = date
    if evaluator is not None:
        test.evaluator = evaluator
    db.session.add(test)
    db.session.commit()
    res['status'] = 'success'
    res['test'] = test.serialize()
    return jsonify(res), res_code


@api.route('/delete/<int:testid>', methods=['GET'])
@decorators.login_required
@decorators.only_admins
@decorators.addLag
def delete(testid):
    test = Test.query.get(testid)
    res = dict(status='fail')
    if test:
        db.session.delete(test)
        db.session.commit()
        res['status'] = 'success'
    res['id'] = testid
    return jsonify(res), 200
