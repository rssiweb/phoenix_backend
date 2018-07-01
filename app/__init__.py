from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_rq2 import RQ

# Define the WSGI application object
app = Flask(__name__)

rq = RQ(app, default_timeout=180 * 2)

bcrypt = Bcrypt(app)

logger = app.logger

# Configurations
app.config.from_object('config')

# Define Database object which is imported by some modules
db = SQLAlchemy(app)

migrate = Migrate(app, db)
migrate.render_as_batch = True


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify(dict(error=str(error))), 404


from app.api.common import api as commonapi
from app.api.student import api as studentapi
from app.api.category import api as categoryapi
from app.api.branch import api as branchapi
from app.api.attendance import api as attendanceapi
from app.api.subject import api as subjectapi
from app.api.exam import api as examapi
from app.api.test import api as testapi
from app.api.marks import api as marksapi
from app.api.grade import api as gradeapi
from app.api.report import api as reportapi

from app.api.admin.attendance import api as admin_attendanceapi
from app.api.admin.branch import api as admin_branchapi
from app.api.admin.category import api as admin_catapi
from app.api.admin.faculty import api as admin_facapi
from app.api.admin.student import api as admin_stdapi
from app.api.admin.subject import api as admin_subapi
from app.api.admin.exam import api as admin_examapi
from app.api.admin.test import api as admin_testapi
from app.api.admin.grade import api as admin_gradeapi

from app.ui.controllers import ui

for api in [commonapi, studentapi, categoryapi, branchapi, attendanceapi,
            examapi, subjectapi, testapi, marksapi, gradeapi, reportapi,

            admin_attendanceapi, admin_branchapi, admin_catapi, admin_facapi,
            admin_stdapi, admin_subapi, admin_examapi, admin_testapi, admin_gradeapi,

            ui]:
    app.register_blueprint(api)

db.create_all()
