from flask import render_template, Blueprint

ui = Blueprint('ui', __name__, url_prefix='')


@ui.route('/')
def login():
    return render_template('login.html')


@ui.route('/attendance')
def attendance():
    return render_template('attendance.html', page=1)


@ui.route('/students')
def students():
    return render_template('students.html', page=2)


@ui.route('/faculties')
def faculties():
    return render_template('faculties.html', page=3)


@ui.route('/me')
def me():
    return render_template('myprofile.html', page=4)


@ui.route('/report')
def report():
    return render_template('report.html', page=5)


@ui.route('/exam')
def exam():
    return render_template('exam_center.html', page=6)


@ui.route('/adminactions')
def admin_actions():
    return render_template('admin_actions.html', page=7)


@ui.route('/exams_details/<int:examid>')
def admin_exam_Details(examid):
    return render_template('exam_details.html', page=7, examid=examid)
