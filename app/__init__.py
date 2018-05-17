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


from app.api.common import commonapi
from app.api.exam import examapi
from app.api.admin import adminapi
from app.api.student import studentapi
from app.api.attendance import attendanceapi
from app.ui.controllers import ui

app.register_blueprint(commonapi)
app.register_blueprint(adminapi)
app.register_blueprint(studentapi)
app.register_blueprint(attendanceapi)
app.register_blueprint(examapi)
app.register_blueprint(ui)

db.create_all()
