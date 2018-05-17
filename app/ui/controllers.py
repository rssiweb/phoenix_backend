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
    return render_template('exam.html', page=6)
