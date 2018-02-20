from flask import render_template, Blueprint

mod_ui = Blueprint('ui', __name__, url_prefix='')


@mod_ui.route('/')
def login():
    return render_template('login.html')


@mod_ui.route('/home')
def home():
    return render_template('home.html')
