from flask import request, Blueprint, send_from_directory
from app import jsonify
from app.utils import decorators
from app.jobs.report import attendance as attendance_job
from app.jobs.utils import JobMeta
from app.jobs.report import exam_report
from app.jobs.marksheet import build_marksheets
from app.jobs.card import build_card


api = Blueprint('report_api', __name__, url_prefix='/api/report')


@api.route('/generate/attendance', methods=['POST'])
@decorators.login_required
def enqueue_attendance():
    data = request.json or request.data or request.form
    month = data.get('month')
    if not month:
        pass
    print('month', month)
    ids = data.get('students')
    categories = data.get('categories', [])
    branches = data.get('branches', [])

    jobmeta = JobMeta()
    jobmeta.owner = request.user
    attendance_job.queue(jobmeta, ids, categories, branches, month)
    message = 'Attendace report queued, you will receive an email on {} email address.'.format(request.user.email)
    return jsonify(dict(status='success', message=message))


@api.route('/generate/exam/<int:examid>', methods=['GET'])
@decorators.login_required
def enqueue_exam(examid):
    jobmeta = JobMeta()
    jobmeta.owner = request.user
    exam_report.queue(jobmeta, examid)
    message = 'Exam report queued, you will receive an email on {} email address.'.format(request.user.email)
    return jsonify(dict(status='success', message=message))


@api.route('/generate/marksheet/<int:examid>', methods=['GET'])
@decorators.login_required
def enqueue_marksheet(examid):
    jobmeta = JobMeta()
    jobmeta.owner = request.user
    build_marksheets.queue(jobmeta, examid)
    message = 'Marksheet report queued, you will receive an email on {} email address.'.format(request.user.email)
    return jsonify(dict(status='success', message=message))


@api.route('/generate/card/<int:branchid>', methods=['GET'])
@decorators.login_required
def get_branch(branchid):
    jobmeta = JobMeta()
    jobmeta.owner = request.user
    build_card.queue(jobmeta, branchid)
    message = 'I-Card generation is queued, you will receive an email on {} email address.'.format(request.user.email)
    return jsonify(dict(status='success', message=message))


@api.route('/download/<string:name>', methods=['GET'])
@decorators.login_required
def get_report(name):
    return send_from_directory(directory='./gen/reports', filename=name)
