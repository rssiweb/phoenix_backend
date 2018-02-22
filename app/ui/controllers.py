from flask import render_template, Blueprint

mod_ui = Blueprint('ui', __name__, url_prefix='')


@mod_ui.route('/')
def login():
    return render_template('login.html')


@mod_ui.route('/attendance')
def attendance():
    return render_template('attendance.html', page=1)


@mod_ui.route('/students')
def students():
    return render_template('students.html', page=2)


@mod_ui.route('/faculties')
def faculties():
    return render_template('faculties.html', page=3)
