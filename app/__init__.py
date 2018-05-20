from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

# Define the WSGI application object
app = Flask(__name__)

bcrypt = Bcrypt(app)


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
from app.api.exam import api as examapi
from app.api.student import api as studentapi
from app.api.attendance import api as attendanceapi

from app.api.admin.attendance import api as admin_attendanceapi
from app.api.admin.branch import api as admin_branchapi
from app.api.admin.category import api as admin_catapi
from app.api.admin.faculty import api as admin_facapi
from app.api.admin.student import api as admin_stdapi

from app.ui.controllers import ui

for api in [commonapi, studentapi, attendanceapi,
            examapi, admin_attendanceapi, admin_branchapi,
            admin_catapi, admin_facapi, admin_stdapi, ui]:
    app.register_blueprint(api)

db.create_all()
